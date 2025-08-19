#!/usr/bin/env python3
import os
import time

__version__ = '2.7.1'

# Global variables for configuration
PID_FILE = "/tmp/remote_kernel.pid"
LOG_FILE = "/tmp/remote_kernel.log"
KERNELS_DIR_DEFAULT = os.path.expanduser("~/.local/share/jupyter/kernels")
SSH_CONFIG_DEFAULT  = os.path.expanduser("~/.ssh/config")
SSH_AUTHORIZED_KEYS_DEFAULT = os.path.expanduser("~/.ssh/authorized_keys")

# Environment-driven settings
PYTHON_BIN  = os.environ.get("REMOTE_KERNEL_PYTHON", "python")
SSH_PORT    = os.environ.get("SSH_PORT", "22")
KERNELS_DIR = os.environ.get("LOCAL_KERNELS_DIR", KERNELS_DIR_DEFAULT)
SSH_CONFIG  = os.environ.get("SSH_CONFIG_PATH", SSH_CONFIG_DEFAULT)
SSH_AUTHORIZED_KEYS_PATH = os.environ.get("SSH_AUTHORIZED_KEYS_PATH", SSH_AUTHORIZED_KEYS_DEFAULT)

def usage():
    print("Usage:")
    print("  remote_kernel --endpoint <HostAlias> -f <connection_file> [--python /path/to/python]")
    print("  remote_kernel add <HostAlias> --name <Display Name> [--python /path/to/python]")
    print("  remote_kernel list")
    print("  remote_kernel delete <slug-or-name>")
    print("  remote_kernel -v   (show version)")

def version():
    print(f"version {__version__}")
    print(f"ENV: LOCAL_KERNELS_DIR        = {KERNELS_DIR}")
    print(f"ENV: REMOTE_KERNEL_PYTHON     = {PYTHON_BIN}")
    print(f"ENV: SSH_CONFIG_PATH          = {SSH_CONFIG}")
    print(f"ENV: SSH_AUTHORIZED_KEYS_PATH = {SSH_AUTHORIZED_KEYS_PATH}")
    print(f"ENV: SSH_PORT                 = {SSH_PORT}")
    print(f"PID file: {PID_FILE}")
    print(f"Log file: {LOG_FILE}")