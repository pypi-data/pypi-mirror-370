'''Because so many tools use the exe vsim, I don't want to run `vsim -version` N times for N
tools each to figure out if it's full-Questa, Modelsim, QuestaFSE, or Riviera.

Instead, eda.py can call this once, and then query if this tool exists when running
opencos.eda.auto_tool_setup(..)
'''

import shutil
import subprocess

from opencos.util import debug

vsim_path = shutil.which('vsim')

INIT_HAS_RUN = False
TOOL_IS = {
    'riviera': False,
    'modelsim_ase': False,
    'questa' : False,
    'questa_fse': False
}


def init() -> None:
    '''Sets INIT_HAS_RUN=True (only runs once) and one of TOOL_IS[tool] = True'''
    global INIT_HAS_RUN # pylint: disable=global-statement

    if INIT_HAS_RUN:
        return

    INIT_HAS_RUN = True

    if not vsim_path:
        return

    proc = None
    try:
        proc = subprocess.run([vsim_path, '-version'], capture_output=True, check=False)
    except Exception as e:
        debug(f'vsim -version: exception {e}')

    if proc is None or proc.returncode != 0:
        return


    stdout_str_lower = proc.stdout.decode('utf-8', errors='replace').lower()

    if all(x in stdout_str_lower for x in ('starter', 'modelsim', 'fpga')):
        TOOL_IS['modelsim_ase'] = True
    elif all(x in stdout_str_lower for x in ('starter', 'questa', 'fpga')):
        TOOL_IS['questa_fse'] = True
    elif all(x in stdout_str_lower for x in ('riviera', 'aldec')):
        TOOL_IS['riviera'] = True
    elif 'questa' in stdout_str_lower:
        TOOL_IS['questa'] = True
