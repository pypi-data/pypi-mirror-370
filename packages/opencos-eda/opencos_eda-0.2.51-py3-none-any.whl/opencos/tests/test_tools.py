'''pytests for testing a few different tools within opencos.eda'''

# pylint: disable=R0801 # (similar lines in 2+ files)

import os
import sys
import pytest

from opencos import eda, eda_tool_helper, eda_base

from opencos.tools.verilator import ToolVerilator
from opencos.tools.vivado import ToolVivado
from opencos.tests import helpers
from opencos.tests.helpers import eda_wrap
from opencos.utils.markup_helpers import yaml_safe_load


thispath = os.path.dirname(__file__)

def chdir_remove_work_dir(relpath):
    '''Changes dir to relpath, removes the work directories (eda.work, eda.export*)'''
    return helpers.chdir_remove_work_dir(thispath, relpath)

# Figure out what tools the system has available, without calling eda.main(..)
config, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()

def test_tools_loaded():
    '''Does not directly call 'eda.main' instead create a few Tool

    class objects and confirm the versioning methods work.
    '''
    assert config
    assert len(config.keys()) > 0

    # It's possible we're running in some container or install that has no tools, for example,
    # Windows.
    if sys.platform.startswith('win') and \
       not helpers.can_run_eda_command('elab', 'sim', config=config):
        # Windows, not handlers for elab or sim:
        pass
    else:
        assert len(tools_loaded) > 0

    def version_checker(
            obj: eda_base.Tool, chk_str: str
    ) -> None:
        assert obj.get_versions()
        full_ver = obj.get_full_tool_and_versions()
        assert chk_str in full_ver, f'{chk_str=} not in {full_ver=}'
        ver_num = full_ver.rsplit(':', maxsplit=1)[-1]
        assert float(ver_num), f'{ver_num=} is not a float, from {full_ver=}'


    # Do some very crude checks on the eda.Tool methods, and make
    # sure versions work for Verilator and Vivado:
    if 'verilator' in tools_loaded:
        my_tool = ToolVerilator(config={})
        version_checker(obj=my_tool, chk_str='verilator:')

    if 'vivado' in tools_loaded:
        my_tool = ToolVivado(config={})
        version_checker(obj=my_tool, chk_str='vivado:')


# Run these on simulation tools.
list_of_commands = [
    'sim',
    'elab'
]

list_of_tools = [
    'iverilog',
    'verilator',
    'vivado',
    'modelsim_ase',
    'questa_fse',
]

list_of_deps_targets = [
    ('tb_no_errs', True),       # target:str, sim_expect_pass:bool (sim only, all elab should pass)
    ('tb_dollar_fatal', False),
    ('tb_dollar_err', False),
]

@pytest.mark.parametrize("command", list_of_commands)
@pytest.mark.parametrize("tool", list_of_tools)
@pytest.mark.parametrize("target,sim_expect_pass", list_of_deps_targets)
def test_err_fatal(command, tool, target, sim_expect_pass):
    '''tests that: eda <sim|elab> --tool <parameter-tool> <parameter-target>

    will correctly pass or fail depending on if it is supported or not.
    '''
    if tool not in tools_loaded:
        pytest.skip(f"{tool=} skipped, {tools_loaded=}")
        return # skip/pass

    relative_dir = "deps_files/test_err_fatal"
    os.chdir(os.path.join(thispath, relative_dir))
    rc = eda.main(command, '--tool', tool, target)
    print(f'{rc=}')
    if command != 'sim' or sim_expect_pass:
        # command='elab' should pass.
        assert rc == 0
    else:
        assert rc > 0


@pytest.mark.skipif('vivado' not in tools_loaded, reason="requires vivado")
def test_vivado_tool_defines():
    '''This test attempts to confirm that the following class inheritance works:

    Command <- CommandDesign <- CommandSim <- CommandSimVivado <- CommandElabVivado

    in particular that CommandElabVivado(CommandSimVivado, ToolVivado) has the
    correct ToolVivado.set_tool_defines() method, and that no other parent Command
    class has overriden it to defeat the defines that should be set.

    We also run with an added dependency (lib_ultrascale_plus_defines) to check that
    defines are set as expected.
    '''

    chdir_remove_work_dir('../../lib')
    rc = eda_wrap(
        'elab', '--tool', 'vivado', 'third_party/vendors/xilinx/lib_ultrascale_plus_defines',
        'oclib_fifo'
    )
    assert rc == 0

    # Confirm that args and defines we expected to be set are set.
    eda_config_yml_path = os.path.join(
        os.getcwd(), 'eda.work', 'oclib_fifo.elab', 'eda_output_config.yml'
    )

    data = yaml_safe_load(eda_config_yml_path)
    assert 'args' in data
    assert data['args'].get('top', '') == 'oclib_fifo'
    assert 'config' in data
    assert 'eda_original_args' in data['config']
    assert 'oclib_fifo' in data['config']['eda_original_args']
    assert data.get('target', '') == 'oclib_fifo'


    # This checks opencos.tools.vivado.ToolVivado.set_tool_defines():
    # We ran with --xilinx, so we expect certain defines to be set, others not to be set.
    assert 'defines' in data

    assert 'OC_TOOL_VIVADO' in data['defines']
    assert 'OC_LIBRARY' in data['defines']
    assert 'OC_LIBRARY_ULTRASCALE_PLUS' in data['defines']

    assert 'OC_LIBRARY_BEHAVIORAL' not in data['defines']
    assert 'VERILATOR' not in data['defines']
    assert 'SYNTHESIS' not in data['defines']

    assert data['defines']['OC_LIBRARY'] == '1'
    assert data['defines']['OC_LIBRARY_ULTRASCALE_PLUS'] is None # key present, no value
