#!/usr/bin/env python3
"""
remote_kernel CLI (SSH-config driven)

Subcommands:
  add       <HostAlias> [--name <Display Name>] [--python /path/to/python]
  list
  delete    <slug-or-name>

Kernel launch path (used by Jupyter's kernel.json):
  remote_kernel --endpoint <HostAlias> -f {connection_file} [--python /path/to/python]

Behavior:
- Reads the *local* Jupyter connection JSON (-f) to get ports + metadata.
- Prepares remote session (workspace + temp key, copies conn file).
- Opens ssh -L forwards for all 5 ZMQ ports (per ~/.ssh/config).
- Opens ssh -R <remote_port>:localhost:<local_sshd_port> and, on remote, mounts
  the LOCAL working path into REMOTE ~/ws<session> using sshfs via the reverse tunnel.
- Executes `python -m ipykernel_launcher -f ~/.runtime_<session>.json` on the remote.
- Cleans up remote artifacts and removes temp pubkey from local authorized_keys on exit.
- Jump/bastion is handled only via SSH config (no CLI -J).
"""

import socket
from pathlib import Path
import sys
import os
import json
import shutil
import time
import subprocess
import getpass
import shlex
from typing import Optional, Tuple, List, Dict, Any
import re

from remote_kernel import KERNELS_DIR, PYTHON_BIN, usage, version, SSH_CONFIG, SSH_PORT, SSH_AUTHORIZED_KEYS_PATH, LOG_FILE

# ---------------------------
# Helpers
# ---------------------------

SESSION_ID = ""

def log(msgstr: str, k: str = SESSION_ID):
    num = 1000
    msg = msgstr[:num] + ("" if len(msgstr) <= num else "...")
    prefix = f"[{k}] " if len(k) > 0 else ""
    #line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {prefix}{msg}"
    ts = int(time.time())  # unix timestamp (seconds)
    line = f"{ts}: {prefix}{msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        # Best-effort logging; ignore write errors
        pass


def _shorten_session_name(session: str) -> str:
    """
    Given a kernel/session name like:
        kernel-584da1fe-6683-44b3-8713-bb2fe1e9d9dc
    Return only the last hex block:
        bb2fe1e9d9dc
    """
    m = re.match(r"kernel-[0-9a-f\-]*([0-9a-f]{12})$", session)
    if m:
        return m.group(1)
    # fallback: just return the input if no match
    return session

def _list_ssh_config_hosts() -> List[str]:
    """Parse SSH_CONFIG file and return a list of host aliases (excluding '*')."""
    cfg_path = os.path.expanduser(SSH_CONFIG)
    if not os.path.exists(cfg_path):
        return []
    hosts: List[str] = []
    try:
        with open(cfg_path) as f:
            for line in f:
                s = line.strip()
                if s.lower().startswith("host ") and not s.lower().startswith("host *"):
                    parts = s.split()
                    for name in parts[1:]:
                        if name != "*" and name not in hosts:
                            hosts.append(name)
    except Exception as e:
        log(f"WARNING: Failed to read {cfg_path}: {e}")
    return hosts


def _arg(flag: str, default: Optional[str] = None) -> Optional[str]:
    """Return value following a flag if present, else default."""
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default

def _check_running(endpoint: str) -> bool:
    """
    True if an ipykernel process is already running on the remote host.
    Uses: ssh <endpoint> 'pgrep -f ipykernel_launcher >/dev/null'
    """
    rc = _run(
        ["ssh", endpoint, "pgrep -f ipykernel_launcher >/dev/null"],
        "Check remote ipykernel",
        check=False,  # don't raise; 0 means found, nonzero means not found
    )
    return rc == 0

def _read_connection_file(conn_file: str) -> Tuple[Optional[List[int]], Optional[dict], Optional[str]]:
    """
    Load ports and the raw config from a Jupyter kernel connection file.
    Returns (ports_list, full_cfg_dict, working_path) or (None, None, None) on error.
    """
    if not os.path.exists(conn_file):
        log(f"ERROR: Connection file not found: {conn_file}")
        return None, None, None

    try:
        with open(conn_file) as f:
            cfg = json.load(f)
    except Exception as e:
        log(f"ERROR: Failed to parse connection file {conn_file}: {e}")
        return None, None, None

    working_path = os.getcwd()
    try:
        ports = [int(cfg[k]) for k in ("shell_port", "iopub_port", "stdin_port", "control_port", "hb_port")]
        ipynb_file = cfg.get("jupyter_session", None)
        if ipynb_file:
            working_path = str(Path(ipynb_file).parent)
    except KeyError as e:
        log(f"ERROR: Missing key in connection file: {e}")
        return None, None, None
    except (TypeError, ValueError) as e:
        log(f"ERROR: Invalid port value in {conn_file}: {e}")
        return None, None, None

    log(f"Working directory   : {working_path}", k=SESSION_ID)
    return ports, cfg, working_path


def _run(cmd: List[str], desc: str, check: bool = True) -> int:
    """Run a subprocess with logging; returns returncode (raises if check=True)."""
    pretty = shlex.join(cmd)
    log(f"{desc}: {pretty}", SESSION_ID)
    try:
        res = subprocess.run(cmd, check=check)
        #log(f"{desc} -> returncode={res.returncode}")
        return res.returncode
    except subprocess.CalledProcessError as e:
        log(f"ERROR during {desc}: returncode={e.returncode}")
        raise
    except FileNotFoundError:
        log(f"ERROR during {desc}: command not found: {cmd[0]}")
        raise

def _prepare_remote(endpoint: str, conn_file: str) -> Tuple[str, str]:
    """
    Returns: (pubkey, session)
    - Generates local temp keypair /tmp/remote_kernel_id_<session>{,.pub}
    - Copies private key to remote as ~/.remote_kernel_id_<session> and chmod 600
    - Copies conn_file to remote as ~/.runtime_<session>.json
    - Appends pubkey to local authorized_keys (or SSH_AUTHORIZED_KEYS)
      with a tagged comment for later cleanup.
    """
    basename = os.path.basename(conn_file)
    # session ID based on connection file name (strip extension)
    session = _shorten_session_name(basename.rsplit(".", 1)[0])
    key_path = f"/tmp/remote_kernel_id_{session}"
    pub_path = f"{key_path}.pub"
    workspace = f"ws{session}"

    if not Path(conn_file).exists():
        raise FileNotFoundError(f"Connection file not found: {conn_file}")

    # Clean any stale temp keys
    for p in (key_path, pub_path):
        try:
            Path(p).unlink(missing_ok=True)
        except Exception:
            pass

    # 1) Generate local keypair
    _run(["ssh-keygen", "-t", "rsa", "-N", "", "-f", key_path, "-q"], "Generate temp key pair", check=True)
    # 2) Prepare remote: workspace dir + copy private key and conn json
    _run(["ssh", endpoint, f"mkdir -p ~/{workspace}"], "Create remote workspace", check=True)
    _run(["scp", "-q", key_path, f"{endpoint}:~/.remote_kernel_id_{session}"], "Copy SSH key to remote", check=True)
    _run(["ssh", endpoint, f"chmod 600 ~/.remote_kernel_id_{session}"], "Set remote key permissions", check=True)
    _run(["scp", "-q", conn_file, f"{endpoint}:~/.runtime_{session}.json"], "Copy connection file to remote", check=True)

    # 3) Append pubkey to local authorized_keys (so remote can SSH back over -R)
    pubkey = Path(pub_path).read_text(encoding="utf-8").strip()
    ak_path = Path(SSH_AUTHORIZED_KEYS_PATH)
    ak_path.parent.mkdir(parents=True, exist_ok=True)
    current = ak_path.read_text(encoding="utf-8") if ak_path.exists() else ""
    tag = f"# remote-kernel-{session}"
    if pubkey not in current:
        with ak_path.open("a", encoding="utf-8") as f:
            if current and not current.endswith("\n"):
                f.write("\n")
            f.write(f"{pubkey} {tag}\n")

    # 4) Remove local temp keys
    try:
        Path(key_path).unlink(missing_ok=True)
        Path(pub_path).unlink(missing_ok=True)
    except Exception:
        pass

    return pubkey, session


def _clean_remote(endpoint: str, session: str, pubkey: str) -> None:
    """
    Remote:
      - Unmount ~/ws<session> if mounted; remove keys + runtime json; remove workspace.
    Local:
      - Remove line containing pubkey from authorized_keys (or SSH_AUTHORIZED_KEYS).
    """
    workspace = f"ws{session}"

    remote_unmount = (
        f"(mount | grep -q '/{workspace} ') && "
        f"(fusermount -uz ~/{workspace} 2>/dev/null || umount -l ~/{workspace} 2>/dev/null || true); true"
    )
    remote_rm = (
        f"rm -f ~/.remote_kernel_id_{session} ~/.runtime_{session}.json; "
        f"rm -rf ~/{workspace} 2>/dev/null || true"
    )

    try:
        _run(["ssh", endpoint, remote_unmount], f"Unmount remote ~/{workspace}", check=False)
    except Exception as e:
        log(f"⚠️ Remote unmount failed: {e}")

    time.sleep(1)
    try:
        _run(["ssh", endpoint, remote_rm], f"Remove remote artifacts for {session}", check=False)
    except Exception as e:
        log(f"⚠️ Remote cleanup failed: {e}")

    # Local cleanup of pubkey
    ak_path = Path(os.environ.get("SSH_AUTHORIZED_KEYS", str(Path.home() / ".ssh" / "authorized_keys")))
    if not ak_path.exists():
        log(f"⚠️ {ak_path} not found")
        return

    try:
        lines = ak_path.read_text(encoding="utf-8").splitlines()
        pubkey_stripped = pubkey.strip()
        filtered = [line for line in lines if pubkey_stripped not in line]
        ak_path.write_text(("\n".join(filtered) + ("\n" if filtered else "")), encoding="utf-8")
        log(f"Removed pubkey from {ak_path}")
    except Exception as e:
        log(f"⚠️ Failed to clean {ak_path}: {e}")


def _probe_remote(endpoint: str, python_bin: str, do_install: bool = True) -> bool:
    """
    Use plain: ssh <endpoint> '<cmd>'
    - trust python_bin
    - check sshfs
    - probe ipykernel; install once if missing
    """
    return True
    import subprocess, json, shlex

    def _sq(s: str) -> str:
        """Escape for single-quoted remote command:  ' -> '\'' """
        return s.replace("'", r"'\''")

    def run_cmd(cmd: str, timeout: int = 30):
        # ALWAYS send as one single-quoted string to remote shell
        quoted = "'" + _sq(cmd) + "'"
        p = subprocess.run(
            ["ssh", endpoint, quoted],
            capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

    # 1) python exists?
    rc, out, err = run_cmd(f"{python_bin} --version")
    if rc != 0:
        log(f"ERROR: Python binary '{python_bin}' not found on remote '{endpoint}'.")
        log("python_version        : None")
        log("ipykernel_version     : None")
        return False
    else:
        log(out)

    # 2) sshfs exists?
    rc, _, _ = run_cmd("sshfs --version >/dev/null 2>&1 || exit 1")
    if rc != 0:
        log(f"ERROR: sshfs not found on remote '{endpoint}'.")
        return False

    # 3) ipykernel probe
    code = (
        "import json,sys,importlib.util;"
        "pv=sys.version.split()[0];"
        "spec=importlib.util.find_spec('ipykernel');"
        "iv=__import__('ipykernel').__version__ if spec else None;"
        "print(json.dumps({'python_version': pv,'has': bool(spec),'iv': iv}))"
    )
    rc, out, err = run_cmd(f"{python_bin} -c '{_sq(code)}'")
    if rc != 0:
        log("ERROR: Failed to get Python/ipykernel info from remote.")
        return False

    try:
        info = json.loads(out or "{}")
    except Exception:
        log("ERROR: Bad JSON from remote probe.")
        return False

    log(f"python_version        : {info.get('python_version')}")
    log(f"ipykernel_version     : {info.get('iv')}")

    if info.get("has"):
        return True

    if not do_install:
        log("ipykernel missing (skipping install).")
        return False

    # 4) install ipykernel once (same interpreter)
    rc, _, err = run_cmd(
        f"{python_bin} -m pip install --user -q --disable-pip-version-check --no-input ipykernel",
        timeout=180
    )
    if rc != 0:
        log("ERROR: Failed to install ipykernel.")
        return False

    # recheck
    rc, out, err = run_cmd(f"{python_bin} -c '{_sq(code)}'")
    if rc != 0:
        log("ERROR: ipykernel still not importable after install (exec fail).")
        return False
    info = json.loads(out or "{}")
    log(f"ipykernel_version     : {info.get('iv')}")
    return bool(info.get("has"))

def _find_free_remote_port(endpoint: str, start: int = 30000, end: int = 31000) -> int:
    """
    Find a free TCP port on the remote host by probing via SSH.
    Returns the first available port in [start, end).
    Raises RuntimeError if none are available.
    """
    check_code = r"""
import socket, sys
start, end = int(sys.argv[1]), int(sys.argv[2])
found = None
for p in range(start, end):
    try:
        s = socket.socket()
        s.bind(('127.0.0.1', p))
        s.close()
        found = p
        break
    except OSError:
        continue
if found: print(found)
"""
    remote_cmd = f"python3 -c {shlex.quote(check_code)} {start} {end}"
    ssh_cmd = ["ssh", endpoint, remote_cmd]

    try:
        res = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True, timeout=15)
        port_str = res.stdout.strip()
        if port_str.isdigit():
            return int(port_str)
        raise RuntimeError(f"No available port found remotely on {endpoint}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"SSH failed while checking remote port: {e.stderr}") from e


# ---------------------------
# Core actions
# ---------------------------

def start_kernel(endpoint: str, conn_file: str, python_bin: str) -> None:
    """
    1) Read local connection file to get ports (for ssh -L mapping) and cfg
    2) Prepare remote (temp key, workspace, copy conn file)
    3) Launch remote ipykernel, after mounting LOCAL working path into REMOTE via sshfs over -R
    """
    basename = os.path.basename(conn_file)
    # session ID based on connection file name (strip extension)
    session = _shorten_session_name(basename.rsplit(".", 1)[0])
    global SESSION_ID
    SESSION_ID = session
    #if _check_running(endpoint):
    #    log(f"INFO: ipykernel is already running on {endpoint}", k=session)
    #    return
    log("=== remote_kernel START ===", k=session)

    local_user = getpass.getuser()
    local_ssh_port = int(SSH_PORT)
    ports, cfg, working_path = _read_connection_file(conn_file)
    if ports is None:
        return
    shell_p, iopub_p, stdin_p, control_p, hb_p = ports
    # Prepare remote
    pubkey = None
    try:
        pubkey, session = _prepare_remote(endpoint, conn_file)
        workspace = f"ws{session}"
        remote_file = f"~/.runtime_{session}.json"
        remote_port = _find_free_remote_port(endpoint=endpoint)
        log(f"Found remote port: {remote_port}", k=session)
        #remote_port = _find_free_local_port()
    except Exception as e:
        log(f"ERROR: Remote preparation failure: {e}", k=session)
        if pubkey and session:
            _clean_remote(endpoint, session, pubkey)
        else:
            # best-effort local cleanup tagless (no-op)
            pass
        return
    # Log context
    log(f"Endpoint            : {endpoint}", k=session)
    log(f"Local conn file     : {conn_file}", k=session)
    log(f"Remote conn file    : {remote_file}", k=session)
    log(f"Python (remote)     : {python_bin}", k=session)
    log(f"Ports               : shell={shell_p}, iopub={iopub_p}, stdin={stdin_p}, control={control_p}, hb={hb_p}", k=session)
    log(f"Transport           : {cfg.get('transport', 'tcp')}", k=session)
    log(f"Kernel name         : {cfg.get('kernel_name', '')}", k=session)
    log(f"Signature scheme    : {cfg.get('signature_scheme', '')}", k=session)
    log(f"IP (in file)        : {cfg.get('ip', '')}", k=session)
    log(f"Working path (local): {working_path}", k=session)
    log(f"Remote workspace    : ~/{workspace}", k=session)
    log(f"Reverse port (-R)   : {remote_port} -> localhost:{local_ssh_port}", k=session)

    # Build remote script: ensure fuse/sshfs, mount, run ipykernel
    remote_command = f"{shlex.quote(python_bin)} -m ipykernel_launcher -f {shlex.quote(remote_file)}"
    remote_script = (
        "set -euo pipefail; "
        # try loading fuse (ignore failure)
        "(modprobe fuse 2>/dev/null || (command -v sudo >/dev/null && sudo modprobe fuse) || true); "
        # require sshfs
        "if ! command -v sshfs >/dev/null; then echo '❌ sshfs not found on remote'; exit 1; fi; "
        f"mkdir -p ~/{workspace}; "
        # mount LOCAL -> REMOTE workspace via reverse tunnel
        f"sshfs -p {remote_port} "
        f"-o IdentityFile=~/.remote_kernel_id_{session} "
        f"-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
        f"{local_user}@localhost:{shlex.quote(os.path.abspath(working_path))} ~/{workspace} && "
        f"cd ~/{workspace} && {remote_command}"
    )

    # Build ssh cmd: -R remote_port:localhost:sshd_port + all -L forwards for ZMQ ports
    ssh_cmd = [
        "ssh",
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ServerAliveInterval=60",
        "-o", "ServerAliveCountMax=5",
        "-R", f"{remote_port}:localhost:{local_ssh_port}",
    ]
    for p in ports:
        ssh_cmd += ["-L", f"{p}:localhost:{p}"]
    ssh_cmd += [endpoint, "sh", "-lc", remote_script]

    log("Opening SSH: establishing -R (reverse) and -L (ZMQ) tunnels, then mounting & launching kernel ...", k=session)
    log("Note: this SSH session must stay open to keep the mount and tunnels alive.", k=session)

    try:
        _run(ssh_cmd, "Launch ipykernel", check=True)
    except Exception:
        log("SSH session terminated with error.", k=session)
    finally:
        time.sleep(1)
        _clean_remote(endpoint, session, pubkey)
        log("Kernel session ended (or SSH closed).", k=session)
        log("=== remote_kernel END ===", k=session)

# ---------------------------
# Kernel spec management
# ---------------------------

def add_kernel(endpoint: str, name: Optional[str], python_bin: Optional[str] = None) -> None:
    """
    Install a Jupyter kernel spec that calls this script with:
      remote_kernel --endpoint <endpoint> -f {connection_file} [--python <python_bin>]
    """
    if not name:
        name = endpoint

    # Warn if endpoint is not present in SSH config
    ssh_hosts = _list_ssh_config_hosts()
    if not ssh_hosts:
        log("⚠ No hosts found in SSH config.")
    elif endpoint not in ssh_hosts:
        log(f"⚠ Endpoint '{endpoint}' not found in SSH config.")
        log("Available hosts:")
        for h in ssh_hosts:
            print(f"  - {h}")

    # Probe once at add-time (optional; you can skip if you prefer)
    if not _probe_remote(endpoint, python_bin or "python"):
        return

    abs_path = os.path.abspath(sys.argv[0])
    slug = name.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    os.makedirs(kernel_dir, exist_ok=True)

    argv = [abs_path, "--endpoint", endpoint, "-f", "{connection_file}"]
    if python_bin:
        argv += ["--python", python_bin]

    kernel_json = {
        "argv": argv,
        "display_name": name,
        "language": "python"
    }

    with open(os.path.join(kernel_dir, "kernel.json"), "w") as f:
        json.dump(kernel_json, f, indent=2)

    log(f"Added kernel          : {name}")
    log(f"Slug/dir              : {slug} -> {kernel_dir}")
    log(f"Endpoint              : {endpoint}")
    log(f"Python (remote)       : {python_bin or 'python'}")


def list_kernels() -> None:
    """List kernels with endpoint, formatted as a clean table."""
    if not os.path.exists(KERNELS_DIR):
        log("No kernels installed")
        return

    print(f"{'slug':<20}| {'name':<26}| {'python':<18}| endpoint")
    print("-" * 90)
    for slug in sorted(os.listdir(KERNELS_DIR)):
        kjson = os.path.join(KERNELS_DIR, slug, "kernel.json")
        if not os.path.isfile(kjson):
            continue
        try:
            with open(kjson) as f:
                data = json.load(f)
            name = data.get("display_name", slug)
            argv = data.get("argv", [])
            endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
            python_bin = argv[argv.index("--python") + 1] if "--python" in argv else "python"
            if not endpoint:
                continue
            print(f"{slug:<20}| {name:<26}| {python_bin:<18}| {endpoint}")
        except Exception as e:
            log(f"Failed to read kernel spec {kjson}: {e}")
    print("---")


def delete_kernel(name_or_slug: str) -> None:
    slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    if not os.path.exists(kernel_dir):
        log(f"Kernel '{name_or_slug}' not found")
        return
    try:
        shutil.rmtree(kernel_dir)
        log(f"Deleted kernel '{name_or_slug}'")
    except Exception as e:
        log(f"Failed to delete kernel '{name_or_slug}': {e}")

# ---------------------------
# Entry
# ---------------------------

def main():
    if len(sys.argv) < 2 or "-h" in sys.argv or "--help" in sys.argv:
        usage()
        return
    if "-v" in sys.argv or "--version" in sys.argv:
        version()
        return

    first_cmd = sys.argv[1].lower()

    if first_cmd == "add":
        # Format: remote_kernel add <HostAlias> [--name <Display Name>] [--python <path>]
        if len(sys.argv) < 3:
            usage()
            hosts = _list_ssh_config_hosts()
            if hosts:
                print("\nAvailable SSH hosts (from SSH_CONFIG or ~/.ssh/config):")
                for h in hosts:
                    print(f"  - {h}")
            else:
                print("\nNo SSH hosts found (set SSH_CONFIG or create ~/.ssh/config).")
            return

        endpoint = sys.argv[2]  # positional after 'add'
        name = _arg("--name")   # may be None -> default to endpoint
        python_bin = _arg("--python")
        add_kernel(endpoint, name, python_bin)
        return

    if first_cmd == "list":
        list_kernels()
        return

    if first_cmd == "delete":
        if len(sys.argv) < 3:
            usage()
            return
        delete_kernel(sys.argv[2])
        return

    # Direct kernel launch path (called by Jupyter via kernel.json)
    if "--endpoint" not in sys.argv or "-f" not in sys.argv:
        usage()
        return

    endpoint = _arg("--endpoint")
    conn_file = _arg("-f")
    python_bin = _arg("--python", PYTHON_BIN)

    start_kernel(endpoint, conn_file, python_bin)


if __name__ == "__main__":
    main()