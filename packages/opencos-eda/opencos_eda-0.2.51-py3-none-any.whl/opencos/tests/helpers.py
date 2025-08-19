'''opencos.tests.helpers - methods used to assist in various pytests on opencos'''

# pylint: disable=dangerous-default-value  # list arg w/ default values.

import json
import os
import shutil
from pathlib import Path

from contextlib import redirect_stdout, redirect_stderr

from opencos import eda
from opencos import deps_schema
from opencos.utils.markup_helpers import yaml_safe_load

def can_run_eda_command(*commands, config: dict) -> bool:
    '''Returns True if we have any installed tool that can run: eda <command>'''
    runnable = []
    for command in list(commands):
        handler = config['command_handler'].get(command, None)
        if not handler:
            return False
        if handler and getattr(handler, 'CHECK_REQUIRES', []):
            if not all(issubclass(handler, x) for x in getattr(handler, 'CHECK_REQUIRES', [])):
                return False
        runnable.append(True)
    return runnable and all(runnable)

def chdir_remove_work_dir(startpath, relpath):
    '''Changes dir to startpath/relpath, removes the work directories (eda.work, eda.export*)'''
    os.chdir(os.path.join(str(Path(startpath)), str(Path(relpath))))
    for outdir in ['eda.export', 'eda.work']:
        fullp = os.path.join(os.getcwd(), outdir)
        if fullp and ('eda.' in fullp) and os.path.isdir(fullp):
            shutil.rmtree(fullp)

def eda_wrap(*args):
    '''Calls eda.main, prefer seed=1 to avoid seed based simulation fails in pytests'''
    main_args = [x for x in list(args) if '--seed' not in x]
    return eda.main('--seed=1', *main_args)

def eda_sim_wrap(*args):
    '''Calls eda.main for 'sim' prefer seed=1 to avoid seed based simulation fails in pytests'''
    main_args = [x for x in list(args) if (x != 'sim' and '--seed' not in x)]
    return eda.main('sim', '--seed=1', *main_args)

def eda_elab_wrap(*args):
    '''Calls eda.main for 'elab'.'''
    main_args = [x for x in list(args) if (x != 'elab' and '--seed' not in x)]
    return eda.main('elab', *main_args)

def assert_sim_log_passes(
        filepath: str, want_str: str = 'TEST PASS',
        err_strs: list = ['Error', 'ERROR', 'TEST FAIL']
) -> None:
    '''Checks log in filepath, makes sure it has a want_str and no err_strs'''
    test_passed = False
    test_failed = False

    assert os.path.exists(filepath), f'{filepath=} does not exist'
    if not want_str:
        # we don't have a want_str, so looks like it passes no matter what
        test_passed = True
    with open(filepath, encoding='utf-8') as f:
        for line in f.readlines():
            if want_str and want_str in line:
                test_passed = True
            if any(x in line for x in err_strs):
                test_failed = True
    assert test_passed, f'{filepath=} did not have {want_str=}'
    assert not test_failed, f'{filepath=} has one of {err_strs=}'

def assert_gen_deps_yml_good(filepath:str, want_target:str='') -> dict:
    '''Generated DEPS files should be coming from --export style args,

    so we also confirm they pass the deps_schema.FILE_SIMPLIFIED'''
    assert os.path.exists(filepath), f'{filepath=} does not exist'
    data = yaml_safe_load(filepath)
    assert len(data.keys()) > 0
    if want_target:
        assert want_target, f'{want_target=} not in {filepath=} {data=}'
        assert 'deps' in data[want_target], f' key "deps" is not in {want_target=} in {data=}'
    assert deps_schema.check_files(filepath, schema_obj=deps_schema.FILE_SIMPLIFIED)
    return data


def assert_export_json_good(filepath:str) -> dict:
    '''Checks that an exported JSON (from eda export, or eda <command> --export) has known keys'''
    assert os.path.exists(filepath), f'{filepath=} does not exist'
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    assert 'name' in data
    assert 'eda' in data
    assert any(x in data for x in ['files', 'tb'])
    return data


def assert_export_jsonl_good(filepath:str, jsonl:bool=True) -> list:
    '''Checks that an exported JSONL (from eda multi --export) has known keys'''
    assert os.path.exists(filepath), f'{filepath=} does not exist'
    ret = []
    with open(filepath, encoding='utf-8') as f:
        if jsonl:
            for line in f.readlines():
                line = line.strip()
                data = json.loads(line)
                assert 'name' in data
                assert 'eda' in data
                assert any(x in data for x in ['files', 'tb'])
                ret.append(data)
        else:
            data = json.load(f)
            assert 'tests' in data
            assert isinstance(data['tests'], list)
            for entry in data['tests']:
                assert 'name' in entry
                assert 'eda' in entry
                assert any(x in entry for x in ['files', 'tb'])
                ret.append(entry)


    return ret


class Helpers:
    '''We do so much with logging in this file, might as well make it reusable'''
    DEFAULT_DIR = ''
    DEFAULT_LOG_DIR = os.getcwd()
    DEFAULT_LOG = os.path.join(DEFAULT_LOG_DIR, '.pytest.eda.log')
    def chdir(self):
        '''Changes directory to self.DEFAULT_DIR and removes eda.work, eda.export paths'''
        chdir_remove_work_dir('', self.DEFAULT_DIR)

    def _resolve_logfile(self, logfile=None) -> str:
        '''Returns the logfile's filepath'''
        ret = logfile
        if ret is None:
            ret = self.DEFAULT_LOG
        else:
            left, right = os.path.split(logfile)
            if not left or left in [os.path.sep, '.', '..']:
                # relative logfile put in DEFAULT_LOG_DIR:
                ret = os.path.join(self.DEFAULT_LOG_DIR, right)
        return ret

    def log_it(self, command_str:str, logfile=None, use_eda_wrap=True) -> int:
        '''Replacement for calling eda.main or eda_wrap, when you want an internal logfile

        Usage:
            rc = self.log_it('sim foo')
            assert rc == 0

        Note this will run with --no-default-log to avoid a Windows problem with stomping
        on a log file.
        '''
        logfile = self._resolve_logfile(logfile)
        rc = 50

        # TODO(drew): There are some issues with log_it redirecting stdout from vivado
        # and modelsim_ase. So this may not work for all tools, you may have to directly
        # look at eda.work/{target}.sim/sim.log or xsim.log.
        print(f'{os.getcwd()=}')
        print(f'{command_str=}')
        with open(logfile, 'w', encoding='utf-8') as f:
            with redirect_stdout(f), redirect_stderr(f):
                if use_eda_wrap:
                    rc = eda_wrap('--no-default-log', *(command_str.split()))
                else:
                    rc = eda.main('--no-default-log', *(command_str.split()))
            print(f'Wrote: {os.path.abspath(logfile)=}')
        return rc

    def is_in_log(self, *want_str, logfile=None, windows_path_support=False):
        '''Check if any of want_str args are in the logfile, or self.DEFAULT_LOG'''
        logfile = self._resolve_logfile(logfile)
        want_str0 = ' '.join(list(want_str))
        want_str1 = want_str0.replace('/', '\\')
        with open(logfile, encoding='utf-8') as f:
            for line in f.readlines():
                if want_str0 in line or \
                   (windows_path_support and want_str1 in line):
                    return True
        return False

    def get_log_lines_with(self, *want_str, logfile=None, windows_path_support=False):
        '''gets all log lines with any of want_str args are in the logfile, or self.DEFAULT_LOG'''
        logfile = self._resolve_logfile(logfile)
        ret_list = []
        want_str0 = ' '.join(list(want_str))
        want_str1 = want_str0.replace('/', '\\')
        with open(logfile, encoding='utf-8') as f:
            for line in f.readlines():
                if want_str0 in line:
                    ret_list.append(line)
                elif windows_path_support and want_str1 in line:
                    ret_list.append(line)
        return ret_list

    def get_log_words_with(self, *want_str, logfile=None, windows_path_support=False):
        '''gets all log lines with any of *want_str within a single word
        in the logfile or self.DEFAULT_LOG
        '''
        logfile = self._resolve_logfile(logfile)
        ret_list = []
        want_str0 = ' '.join(list(want_str))
        want_str1 = want_str0.replace('/', '\\')
        with open(logfile, encoding='utf-8') as f:
            for line in f.readlines():
                if want_str0 in line:
                    for word in line.split():
                        if want_str0 in word:
                            ret_list.append(word)
                elif windows_path_support and want_str1 in line:
                    for word in line.split():
                        if want_str1 in word:
                            ret_list.append(word)

        return ret_list
