'''pytests for opencos.deps modules'''

# TODO(drew): these need to be refactored if we cleanup opencos.deps commands;
# this uses the old DEPS (non-markup) command format, such as 'shell@some bash command'

# TODO(drew): for now, ignore long lines and docstrings
# pylint: disable=line-too-long,missing-function-docstring

from pathlib import Path
import os
import pytest

from opencos import eda_tool_helper

from opencos.deps import deps_file, deps_commands

THISPATH = os.path.dirname(__file__)

# Figure out what tools the system has avail, without calling eda.main(..)
config, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()


def test_get_all_targets():
    '''Makes sure that deps_file.get_all_targets(filter_str:str) works'''

    targets = deps_file.get_all_targets(
        dirs=[
            str(Path('../../lib/tests')),
            str(Path('../../lib/rams/tests')),
        ],
        base_path=str(Path(THISPATH)),
        filter_str='*test',
    )
    print(f'{targets=}')
    assert str(Path('../../lib/rams/tests/oclib_ram2rw_test')) in targets
    assert str(Path('../../lib/tests/oclib_fifo_test')) in targets
    for t in targets:
        assert t.endswith('test'), f'target {t} filter did not work *test'


@pytest.mark.skipif(
    not('vivado' in tools_loaded or
        'verilator' in tools_loaded),
    reason="requires vivado or verilator"
)
def test_get_all_targets_eda_multi():
    '''Makes sure that deps_file.get_all_targets(filter_using_mult:str) works'''

    targets = deps_file.get_all_targets(
        base_path=THISPATH,
        filter_using_multi='sim ../../lib/tests/*test ../../lib/rams/tests/*test',
    )
    print(f'{targets=}')
    assert '../../lib/rams/tests/oclib_ram2rw_test' in targets
    assert '../../lib/tests/oclib_fifo_test' in targets
    for t in targets:
        assert t.endswith('test'), f'target {t} filter did not work *test'


def test_parse_deps_shell_str__no_parse():
    line = 'some_file.sv'
    d = deps_commands.parse_deps_shell_str(line, '', '')
    assert not d, f'{d=}'

    line = 'some_target:'
    d = deps_commands.parse_deps_shell_str(line, '', '')
    assert not d, f'{d=}'

    line = '   csr@some_file.sv'
    d = deps_commands.parse_deps_shell_str(line, '', '')
    assert not d, f'{d=}'

def test_parse_deps_shell_str__cp():
    line = '    shell@ cp ./oclib_fifo_test.sv oclib_fifo_test_COPY.sv ;'
    d = deps_commands.parse_deps_shell_str(line, '', '')
    assert d, f'{d=}'
    assert d['exec_list'] == ['cp', './oclib_fifo_test.sv', 'oclib_fifo_test_COPY.sv', ';'], f'{d=}'

def test_parse_deps_shell_str__echo():
    line = '    shell@echo "hello world"'
    d = deps_commands.parse_deps_shell_str(line, '', '')
    assert d, f'{d=}'
    assert d['exec_list'] == ['echo', '"hello', 'world"'], f'{d=}'

def test_parse_deps_shell_str__enable_filepath_replacement():
    # Dealing w/ relative paths, change the current working directory to the module directory
    # Default is enabled.
    module_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(module_dir)
    line = 'shell@cp ../deps/deps_commands.py .pytest.copied.py'
    d = deps_commands.parse_deps_shell_str(line, target_path='./', target_node='foo_target')
    assert d, f'{d=}'
    spath = os.path.abspath(os.path.join('..', 'deps', 'deps_commands.py'))
    assert d['exec_list'] == ['cp', spath, '.pytest.copied.py'], f'{d=}'
    assert d['target_node'] == 'foo_target'
    assert d['target_path'] == os.path.abspath('./')

def test_parse_deps_shell_str__disable_filepath_replacement():
    # Dealing w/ relative paths, change the current working directory to the module directory
    module_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(module_dir)
    line = 'shell@cp ../deps/deps_commands.py .pytest.copied.py'
    d = deps_commands.parse_deps_shell_str(line, target_path='./', target_node='foo_target',
                                          enable_filepath_subst_target_dir=False)
    assert d, f'{d=}'
    assert d['exec_list'] == ['cp', '../deps/deps_commands.py', '.pytest.copied.py'], f'{d=}'
    assert d['target_node'] == 'foo_target'
    assert d['target_path'] == os.path.abspath('./')

def test_parse_deps_shell_str__enable_dirpath_replacement():
    # Dealing w/ relative paths, change the current working directory to the module directory
    module_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(module_dir)
    line = 'shell@ls -ltr ./'
    d = deps_commands.parse_deps_shell_str(line, target_path='./', target_node='foo_target',
                                          enable_dirpath_subst_target_dir=True)
    assert d, f'{d=}'
    assert d['exec_list'] == ['ls', '-ltr', os.path.abspath('./')], f'{d=}'
    assert d['target_node'] == 'foo_target'
    assert d['target_path'] == os.path.abspath('./')

def test_parse_deps_shell_str__disable_dirpath_replacement():
    # Dealing w/ relative paths, change the current working directory to the module directory
    # Default is disabled.
    module_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(module_dir)
    line = 'shell@ls -ltr ./'
    d = deps_commands.parse_deps_shell_str(line, target_path='./', target_node='foo_target')
    assert d, f'{d=}'
    assert d['exec_list'] == ['ls', '-ltr', './'], f'{d=}'
    assert d['target_node'] == 'foo_target'
    assert d['target_path'] == os.path.abspath('./')


def test_parse_deps_work_dir_add_srcs__no_parse():
    line = 'some_file.sv'
    d = deps_commands.parse_deps_work_dir_add_srcs(line, '', '')
    assert not d, f'{d=}'

    line = 'some_target:'
    d = deps_commands.parse_deps_work_dir_add_srcs(line, '', '')
    assert not d, f'{d=}'

    line = '   csr@some_file.sv'
    d = deps_commands.parse_deps_work_dir_add_srcs(line, '', '')
    assert not d, f'{d=}'

def test_parse_deps_work_dir_add_srcs__single_file():
    line = '    work_dir_add_srcs@ single_file.txt'
    d = deps_commands.parse_deps_work_dir_add_srcs(line, '', '')
    assert d, f'{d=}'
    assert d['file_list'] == ['single_file.txt']

def test_parse_deps_work_dir_add_srcs__several_file():
    line = '    work_dir_add_srcs@ single_file.txt another.sv  gen-verilog/mine.v ./gen-vhdl/wordy.vhdl'
    d = deps_commands.parse_deps_work_dir_add_srcs(line, '', '')
    assert d, f'{d=}'
    assert d['file_list'] == [
        'single_file.txt', 'another.sv', 'gen-verilog/mine.v', './gen-vhdl/wordy.vhdl'
    ]


def test_parse_deps_peakrdl__no_parse():
    line = 'some_file.sv'
    d = deps_commands.parse_deps_peakrdl(line, '', '')
    assert not d, f'{d=}'

    line = 'some_target:'
    d = deps_commands.parse_deps_peakrdl(line, '', '')
    assert not d, f'{d=}'

    line = '   csr@some_file.sv'
    d = deps_commands.parse_deps_peakrdl(line, '', '')
    assert not d, f'{d=}'

def test_parse_deps_peakrdl__with_top():
    line = '    peakrdl@ --cpuif axi4-lite-flat --top   my_fancy_csrs ./my_csrs.rdl'
    d = deps_commands.parse_deps_peakrdl(line, '', '')
    assert d, f'{d=}'
    assert len(d['shell_commands_list']) > 0
    assert d['work_dir_add_srcs']['file_list'] == ['peakrdl/my_fancy_csrs_pkg.sv', 'peakrdl/my_fancy_csrs.sv']

def test_parse_deps_peakrdl__with_top2():
    line = '    peakrdl@ --cpuif axi4-lite-flat --top=my_fancy_csrs ./my_csrs.rdl'
    d = deps_commands.parse_deps_peakrdl(line, '', '')
    assert d, f'{d=}'
    assert len(d['shell_commands_list']) > 0
    assert d['work_dir_add_srcs']['file_list'] == ['peakrdl/my_fancy_csrs_pkg.sv', 'peakrdl/my_fancy_csrs.sv']

def test_parse_deps_peakrdl__infer_top():
    line = '    peakrdl@ --cpuif axi4-lite-flat ./my_csrs.rdl'
    d = deps_commands.parse_deps_peakrdl(line, '', '')
    assert d, f'{d=}'
    assert len(d['shell_commands_list']) > 0
    assert d['work_dir_add_srcs']['file_list'] == ['peakrdl/my_csrs_pkg.sv', 'peakrdl/my_csrs.sv']
