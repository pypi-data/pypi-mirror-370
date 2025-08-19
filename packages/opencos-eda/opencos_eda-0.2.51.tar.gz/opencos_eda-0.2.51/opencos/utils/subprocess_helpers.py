''' opencos.utils.subprocess_helpers -- wrappers for subprocess to support background/tee'''

import os
import shutil
import subprocess
import sys

from opencos.util import debug, error, info, progname, global_log

IS_WINDOWS = sys.platform.startswith('win')

def subprocess_run(
        work_dir: str, command_list: list, fake: bool = False, shell: bool = False
) -> int:
    ''' Run command_list in the foreground, with preference to use bash if shell=True'''

    proc_kwargs = {
        'shell': shell
    }
    if work_dir:
        proc_kwargs['cwd'] = work_dir

    bash_exec = shutil.which('bash')
    if shell and bash_exec and not IS_WINDOWS:
        proc_kwargs.update({'executable': bash_exec})

    if not IS_WINDOWS and shell:
        c = ' '.join(command_list)
    else:
        c = command_list

    if fake:
        info(f"subprocess_run FAKE: would have called subprocess.run({c}, **{proc_kwargs}")
        return 0

    debug(f"subprocess_run: About to call subprocess.run({c}, **{proc_kwargs}")
    proc = subprocess.run(c, check=True, **proc_kwargs)
    return proc.returncode


def subprocess_run_background(
        work_dir: str, command_list: list, background: bool = True, fake : bool = False,
        shell: bool = False, tee_fpath: str = ''
) -> (str, str, int):
    ''' Run command_list in the background, with preference to use bash if shell=True

    tee_fpath is relative to work_dir.

    Note that stderr is converted to stdout, and stderr is retuned as '':
        Returns tuple of (stdout str, '', int return code)
    '''

    debug(f'subprocess_run_background: {background=} {tee_fpath=} {shell=}')

    if fake:
        # let subprocess_run handle it (won't run anything)
        rc = subprocess_run(work_dir, command_list, fake=fake, shell=shell)
        return '', '', rc

    proc_kwargs = {'shell': shell,
                   'stdout': subprocess.PIPE,
                   'stderr': subprocess.STDOUT,
                   }
    if work_dir:
        proc_kwargs['cwd'] = work_dir

    bash_exec = shutil.which('bash')
    if shell and bash_exec and not IS_WINDOWS:
        # Note - windows powershell will end up calling: /bin/bash /c, which won't work
        proc_kwargs.update({'executable': bash_exec})

    if not IS_WINDOWS and shell:
        c = ' '.join(command_list)
    else:
        c = command_list # leave as list.

    debug(f"subprocess_run_background: about to call subprocess.Popen({c}, **{proc_kwargs})")
    proc = subprocess.Popen(c, **proc_kwargs) # pylint: disable=consider-using-with

    stdout = ''
    tee_fpath_f = None
    if tee_fpath:
        tee_fpath = os.path.join(work_dir, tee_fpath)
        try:
            tee_fpath_f = open( # pylint: disable=consider-using-with
                tee_fpath, 'w', encoding='utf-8'
            )
        except Exception as e:
            error(f'Unable to open file "{tee_fpath}" for writing, {e}')

    for line in iter(proc.stdout.readline, b''):
        line = line.rstrip().decode("utf-8", errors="replace")
        if not background:
            print(line)
        if tee_fpath_f:
            tee_fpath_f.write(line + '\n')
        if global_log.file:
            global_log.write(line, '\n')
        stdout += line + '\n'

    proc.communicate()
    rc = proc.returncode
    if tee_fpath_f:
        tee_fpath_f.write(f'INFO: [{progname}] subprocess_run_background: returncode={rc}\n')
        tee_fpath_f.close()
        info('subprocess_run_background: wrote: ' + os.path.abspath(tee_fpath))

    return stdout, '', rc
