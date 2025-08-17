"ArchLinux tool to manage /etc configuration files using git."

import sys
import subprocess

__version__ = '0.5'

MIN_PYTHON_VERSION = (3, 12)

_version = sys.version_info[:2]
if _version < MIN_PYTHON_VERSION:
    sys.exit(f'*** error: the python version must be at least'
             f' {MIN_PYTHON_VERSION}')

class ApcError(Exception): pass

def warn(msg):
    print('*** warning:', msg)

def run_cmd(cmd, msg=None):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        err_msg = [msg] if msg is not None else []
        err_msg += [str(e)]
        if e.stdout:
            err_msg += [e.stdout.rstrip()]
        if e.stderr:
            err_msg += [e.stderr.rstrip()]
        raise ApcError('\n'.join(err_msg)) from e
