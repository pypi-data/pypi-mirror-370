'''Because > 1 tools use the exe 'code', I don't want to run

`code --list-extensions --show-versionsvsim -version` for every tool that needs
to check if they exist in VScode land.

Instead, eda.py can call this once, and then query if the VScode extension exists when
running opencos.eda.auto_tool_setup(..)
'''

import shutil
import subprocess

from opencos.util import debug

vscode_path = shutil.which('code')

INIT_HAS_RUN = False
EXTENSIONS = {} # dict of {name: version} for VScode extensions of name


def init() -> None:
    '''Sets INIT_HAS_RUN=True (only runs once) and one of TOOL_IS[tool] = True'''
    global INIT_HAS_RUN # pylint: disable=global-statement

    if INIT_HAS_RUN:
        return

    INIT_HAS_RUN = True

    if not vscode_path:
        return

    proc = None
    try:
        proc = subprocess.run([vscode_path, '--list-extensions', '--show-versions'],
                              capture_output=True, check=False)
    except Exception as e:
        debug(f'vscode --list-extensions --show-versions: exception {e}')

    if proc is None or proc.returncode != 0:
        return

    for line in proc.stdout.decode('utf-8', errors='replace').split('\n'):
        if '@' in line:
            parts = line.split('@')
            if parts[0] and parts[1]:
                EXTENSIONS[parts[0]] = parts[1]
