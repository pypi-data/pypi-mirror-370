'''pytests for: eda elab <command> [args] <target>'''

import os
import pytest

from opencos import eda_tool_helper
from opencos.tests import helpers
from opencos.tests.helpers import eda_wrap, eda_elab_wrap


thispath = os.path.dirname(__file__)

def chdir_remove_work_dir(relpath):
    '''Changes dir to relpath, removes the work directories (eda.work, eda.export*)'''
    return helpers.chdir_remove_work_dir(thispath, relpath)

# Figure out what tools the system has available, without calling eda.main(..)
config, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()

# list of tools we'd like to try:
list_of_elab_tools = [
    'slang',
    'verilator',
    'vivado',
    'modelsim_ase'
    'questa_fse',
    'invio',
    'surelog',
    'invio_yosys',
]

list_of_elab_tools_cant_sim = [
    'slang',
    'invio',
    'surelog',
    'invio_yosys',
]

def skip_it(tool) -> bool:
    '''Returns True if this test should be skipped

    For example, run in a github Action w/ container that doesn't have a tool
    in tool_loaded.
    '''
    return bool( tool not in tools_loaded )

@pytest.mark.parametrize("tool", list_of_elab_tools)
class Tests:
    '''Test tools from list_of_elab_tools for 'eda elab' and 'eda multi elab'.'''

    def test_args_elab(self, tool):
        '''tests: eda elab --tool oclib_priarb'''
        if skip_it(tool):
            pytest.skip(f"{tool=} skipped, {tools_loaded=}")
            return # skip/pass
        chdir_remove_work_dir('../../lib')
        rc = eda_elab_wrap('--tool', tool, 'oclib_priarb')
        print(f'{rc=}')
        assert rc == 0

    def test_args_multi_elab(self, tool):
        '''tests: eda multi elab --tool oclib_*arb'''
        if skip_it(tool):
            pytest.skip(f"{tool=} skipped, {tools_loaded=}")
            return # skip/pass
        chdir_remove_work_dir('../../lib')
        rc = eda_wrap('multi', 'elab', '--tool', tool, 'oclib_*arb')
        print(f'{rc=}')
        assert rc == 0


@pytest.mark.parametrize("tool", list_of_elab_tools_cant_sim)
def test_elab_tool_cant_run_sim(tool):
    '''Checks eda.check_command_handler_cls(...) so we don't fallback to a different tool'''
    if skip_it(tool):
        pytest.skip(f"{tool=}skipped, {tools_loaded=}")
        return # skip/pass
    chdir_remove_work_dir('../../lib')

    # Calling this will have rc non-zero, but will also throw CommandSim NotImplementedError.
    rc = 0
    try:
        rc = eda_wrap('sim', '--tool', tool, 'oclib_fifo')
        print(f'{rc=}')
        assert rc > 1
    except NotImplementedError:
        rc = 3
        print(f'{rc=} (forced to 3 for NotImplementedError)')
    assert rc > 1
