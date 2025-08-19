'''pytests for: eda [multi|tools-multi] synth [args] <target(s)>'''

import os
import shutil

import pytest

from opencos import eda, eda_tool_helper
from opencos.tests import helpers
from opencos.tests.helpers import Helpers


THISPATH = os.path.dirname(__file__)

def chdir_remove_work_dir(relpath):
    '''Changes dir to relpath, removes the work directories (eda.work, eda.export*)'''
    return helpers.chdir_remove_work_dir(THISPATH, relpath)

# Figure out what tools the system has available, without calling eda.main(..)
config, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()

# list of tools we'd like to try:
list_of_synth_tools = [
    'invio_yosys',
    'tabbycad_yosys',
    'slang_yosys'
]

list_of_elab_tools = [
    'invio_yosys',
    'slang_yosys'
]

def skip_it(tool, command) -> bool:
    '''skip_it: returns True if we should skip due to lack of tool existence'''
    return bool( tool not in tools_loaded or
                 (command == 'elab' and tool not in list_of_elab_tools) or
                 (command == 'synth' and tool not in list_of_synth_tools) )


@pytest.mark.parametrize("tool", list_of_synth_tools)
@pytest.mark.parametrize("command", ['elab', 'synth'])
class Tests:
    '''skippable (via pytest parameters) class holder for pytest methods'''

    def test_args_multi_synth_bad_target_should_fail(self, tool, command):
        '''Tests: eda mulit <elab|synth>, and this test should fail.'''
        if skip_it(tool, command):
            pytest.skip(f"{tool=} {command=} skipped, {tools_loaded=}")
            return # skip/pass
        chdir_remove_work_dir('../../lib')
        cmdlist = (f'multi {command} --debug --fail-if-no-targets --tool {tool}'
                   ' target_doesnt_exist*').split()
        rc = eda.main(*cmdlist)
        print(f'{rc=}')
        assert rc > 1

    def test_args_multi_synth_oclib_fifos(self, tool, command):
        '''This should be 4 jobs and takes ~15 seconds for synth.'''
        if skip_it(tool, command):
            pytest.skip(f"{tool=} {command=} skipped, {tools_loaded=}")
            return # skip/pass
        chdir_remove_work_dir('../../lib')
        cmdlist = (f'multi {command} --debug --fail-if-no-targets --tool {tool}'
                   ' --yosys-synth=synth_xilinx oclib_fifo*').split()
        rc = eda.main(*cmdlist)
        print(f'{rc=}')
        assert rc == 0

    def test_args_multi_synth_oclib_rams(self, tool, command):
        '''This should be 4 jobs and takes ~15 seconds for synth.'''
        if skip_it(tool, command):
            pytest.skip(f"{tool=} {command=} skipped, {tools_loaded=}")
            return # skip/pass
        chdir_remove_work_dir('../../lib')
        cmdlist = (f'multi {command} --debug --fail-if-no-targets --tool {tool}'
                   ' --yosys-synth=synth_xilinx rams/oclib_ram*').split()
        rc = eda.main(*cmdlist)
        print(f'{rc=}')
        assert rc == 0


def vivado_has_xpms() -> bool:
    '''Returns True if Vivado is installed and has visibility to XPMs'''
    if 'vivado' not in tools_loaded:
        return False
    vivado_exe = shutil.which('vivado')
    vivado_bin_path, _ = os.path.split(vivado_exe)
    vivado_base_path, _ = os.path.split(vivado_bin_path) # strip bin/vivado

    return os.path.exists(os.path.join(vivado_base_path, 'data', 'ip', 'xpm'))


@pytest.mark.skipif(
    'slang_yosys' not in tools_loaded, reason="requires slang_yosys for synth"
)
class TestsSlangYosys(Helpers):
    '''Tests that require tool=slang_yosys to be available'''

    def test_sdc_file(self):
        '''Test for 'eda synth' on oclib_fifo_with_sdc

        This does not use the actual .sdc file, but it also shouldn't fail with
        that file in the 'deps' list (CommandDesign should track it correctly)
        '''
        chdir_remove_work_dir('deps_files/test_sdc_files')
        cmd_str = 'synth --tool=slang_yosys oclib_fifo_with_sdc'
        rc = self.log_it(cmd_str, use_eda_wrap=False)
        assert rc == 0

@pytest.mark.skipif('vivado' not in tools_loaded, reason="requires vivado")
@pytest.mark.skipif(not vivado_has_xpms(), reason="requires install to have XPMs")
class TestsVivado(Helpers):
    '''Tests that require tool=vivado with XPMs available for synthesis'''

    def test_sdc_file(self):
        '''Test for 'eda synth' on oclib_fifo_with_sdc

        And check that the .sdc file was used and not the default generated .xdc
        file
        '''
        chdir_remove_work_dir('deps_files/test_sdc_files')
        cmd_str = 'synth --tool=vivado oclib_fifo_with_sdc'
        rc = self.log_it(cmd_str, use_eda_wrap=False)
        assert rc == 0

        # apparently this doesn't get saved in the eda.log. That's not great,
        # but we can check the <target>.synth.log file.
        synth_log = os.path.join(
            THISPATH, 'deps_files', 'test_sdc_files',
            'eda.work', 'oclib_fifo_with_sdc.synth', 'oclib_fifo.synth.log'
        )
        sdc_lines = self.get_log_lines_with('.sdc', logfile=synth_log)
        assert sdc_lines
        for sdc_line in sdc_lines:
            assert 'oclib_fifo_vivado.sdc' in sdc_line
            assert 'test_sdc_files' in sdc_line
            assert 'eda.work' not in sdc_line
