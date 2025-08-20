'''pytests for: eda

Using eda.main() entrypoint

If you want to run this, consider running from the root of opencos repo:
    > pytest --verbose opencos/*/*.py
    > python3 -m pytest --verbose opencos/*/*.py
    > python3 -m pytest -rx opencos/*/*.py
 which avoids using any pip installed opencos.eda

Throughout this file, if you see:
   assert rc > 1
It is not a typo. We would prefer all expected errors to be caught and reported by
eda.py. Python errors tend to return with rc=1, and those are problematic for us
and should be more gracefully handled.
'''

# pylint: disable=R0801 # (similar lines in 2+ files)

import os
import shutil
import subprocess
from contextlib import redirect_stdout, redirect_stderr

import pytest

from opencos import eda, eda_tool_helper
from opencos.utils.markup_helpers import yaml_safe_load
from opencos.tests import helpers
from opencos.tests.helpers import eda_wrap, eda_sim_wrap, eda_elab_wrap, \
    Helpers


THISPATH = os.path.dirname(__file__)

def chdir_remove_work_dir(relpath):
    '''Changes dir to relpath, removes the work directories (eda.work, eda.export*)'''
    return helpers.chdir_remove_work_dir(THISPATH, relpath)

# Figure out what tools the system has available, without calling eda.main(..)
config, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()

def can_run_eda_sim() -> bool:
    '''Returns True if we have any installed tool that can run: eda sim'''
    return helpers.can_run_eda_command('sim', config=config)

def can_run_eda_elab() -> bool:
    '''Returns True if we have any installed tool that can run: eda elab'''
    return helpers.can_run_eda_command('elab', config=config)

@pytest.mark.skipif(
    'verilator' not in tools_loaded and 'vivado' not in tools_loaded,
    reason="requires verilator OR vivado"
)
def test_args_sim_default_tool():
    '''Test that: eda sim <target>; works'''
    chdir_remove_work_dir('../../lib/tests')
    rc = eda_sim_wrap('oclib_fifo_test')
    print(f'{rc=}')
    assert rc == 0


class TestTargets(Helpers):
    '''Tests for: eda targets'''

    DEFAULT_DIR = os.path.join(THISPATH, '..', '..', 'lib', 'tests')

    def test_lib_tests__no_pattern(self):
        '''Test that this works: eda targets'''
        self.chdir()
        rc = self.log_it('targets --debug', use_eda_wrap=False)
        assert rc == 0
        assert self.is_in_log('oclib_fifo_test')
        assert self.is_in_log('oclib_rrarb_test')

    def test_lib_tests__with_pattern(self):
        '''Test that this works: eda targets oclib_fifo*test'''
        self.chdir()
        rc = self.log_it('targets oclib_fifo*test', use_eda_wrap=False)
        assert rc == 0
        assert self.is_in_log('oclib_fifo_test')
        assert not self.is_in_log('oclib_rrarb_test')


@pytest.mark.skipif(
    'verilator' not in tools_loaded, reason="requires verilator"
)
class TestsRequiresVerilator( # pylint: disable=too-many-public-methods
        Helpers
):
    '''Tests that require verilator, skip if not present (in some Github Action containers)'''

    def test_verilator_cant_run_synth(self):
        '''Checks eda.check_command_handler_cls(...) so we don't fallback to a different tool'''
        # If you say you want verilator, then we will NOT choose a different default handler.
        chdir_remove_work_dir('../../lib')
        rc = eda_wrap('synth', '--tool', 'verilator', 'oclib_fifo')
        print(f'{rc=}')
        assert rc > 1


    def test_args_sim(self):
        '''Basic sim with --tool verilator'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0


    def test_args_sim_tool_with_path(self):
        '''Test for calling a tool as --tool=<tool>=</path/to/tool-exe>'''
        verilator_fullpath = shutil.which('verilator')
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--tool', f'verilator={verilator_fullpath}', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_args_sim_with_coverage(self):
        '''Test for verilator --coverage'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_wrap('sim', '--coverage', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0
        # We don't check the logs, but the command should succeed.

    def test_args_lint_only_sim(self):
        '''Confirm --lint-only works for Verilator with 'sim' command.'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--lint-only', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_args_elab(self):
        '''Test for: eda elab'''
        chdir_remove_work_dir('../../lib')
        rc = eda_elab_wrap('--tool', 'verilator', 'oclib_priarb')
        print(f'{rc=}')
        assert rc == 0

    def test_run_from_work_dir(self):
        '''
        Uses eda --stop-before-compile to craft the eda.work/(test)/ dirs and shell commands,
        and confirms that we can run those shell commands.
        '''

        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--stop-before-compile', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

        os.chdir(os.path.join(THISPATH, '../../lib/tests/eda.work/oclib_fifo_test.sim'))
        res = subprocess.run(
            [ './lint_only.sh' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True
        )
        rc = res.returncode
        print(f'{rc=}')
        assert rc == 0
        assert res.stdout
        assert res.stderr == b''

        res = subprocess.run(
            [ './all.sh' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True
        )
        rc = res.returncode
        print(f'{rc=}')
        assert rc == 0
        assert res.stdout
        assert res.stderr == b''

        res = subprocess.run(
            [ './simulate_only.sh' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True
        )
        rc = res.returncode
        print(f'{rc=}')
        assert rc == 0
        assert res.stdout
        assert res.stderr == b''

    def test_args_sim_waves(self):
        '''Test that --waves for verilator works (FST, not VCD)'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--tool', 'verilator', '--waves', 'oclib_fifo_test')
        print(f'{rc=}')
        assert os.path.exists(os.path.join('.', 'eda.work', 'oclib_fifo_test.sim', 'dump.fst'))
        assert rc == 0

    def test_args_sim_waves_dumpvcd(self):
        '''Test that --waves --dump-vcd works for the opencos/ style SV tests'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--tool', 'verilator', '--waves', '--dump-vcd', 'oclib_fifo_test')
        print(f'{rc=}')
        assert os.path.exists(os.path.join('.', 'eda.work', 'oclib_fifo_test.sim', 'dump.vcd'))
        assert rc == 0

    def test_args_sim_dumpvcd_verilator_trace(self):
        '''Do not set --dump-vcd, set --waves and do directly set +trace=vcd,
        and confirm +trace works as a bare CLI plusarg'''

        chdir_remove_work_dir('../../lib/tests')
        rc = self.log_it('sim --tool verilator --waves +trace=vcd oclib_fifo_test')
        assert rc == 0
        assert os.path.exists(os.path.join('.', 'eda.work', 'oclib_fifo_test.sim', 'dump.vcd'))
        lines = self.get_log_lines_with('exec: ./obj_dir/sim.exe')
        assert len(lines) == 1
        assert ' +trace=vcd ' in lines[0]
        assert ' +trace ' not in lines[0]

    def test_args_seed1(self):
        '''Test for: eda sim --tool verilator --seed <value>'''
        chdir_remove_work_dir('../../lib/tests')
        rc = self.log_it('sim --tool verilator --seed=1 oclib_fifo_test')
        assert rc == 0
        lines = self.get_log_lines_with('exec: ./obj_dir/sim.exe')
        assert len(lines) == 1
        assert ' +verilator+seed+1 ' in lines[0]

    def test_args_wno_fatal(self):
        '''Test for: eda sim --tool verilator w/ --verilate-args'''
        chdir_remove_work_dir('../../lib/tests')
        rc = self.log_it('sim --tool verilator --verilate-args=-Wno-fatal oclib_fifo_test')
        assert rc == 0
        lines = self.get_log_lines_with('exec: ')
        assert len(lines) == 2
        assert 'verilator' in lines[0]
        assert ' -Wno-fatal ' in lines[0]
        assert 'sim.exe' in lines[1]

    def test_args_sim_should_fail(self):
        '''Test that our command handler for verilator will fail b/c --xilinx set.'''
        chdir_remove_work_dir('../../lib/tests')
        # We'd expect this to fail b/c --xilinx and --tool verilator flags an error. I do not
        # want to use the xfail pytest decorator.
        rc = eda_sim_wrap('--xilinx', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc > 1

    def test_more_plusargs_sim(self):
        '''Test that unprocessed plusargs become sim-plusargs on CLI'''
        chdir_remove_work_dir('../../lib/tests')
        rc = self.log_it('sim --tool verilator +info=300 +some_plusarg_novalue oclib_fifo_test')
        assert rc == 0
        lines = self.get_log_lines_with('exec: ./obj_dir/sim.exe')
        assert len(lines) == 1
        assert ' +info=300 ' in lines[0]
        assert ' +info ' not in lines[0]
        assert ' +some_plusarg_novalue ' in lines[0]
        assert ' +some_plusarg_novalue=' not in lines[0]

    def test_args_multi_sim(self):
        '''Basic test for: eda multi sim, with common args, should pass.'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--seed=1', '--tool', 'verilator',
                      'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_args_multi_sim_timeout(self):
        '''Test for --single-timout in: eda multi'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--seed=1', '--tool', 'verilator',
                      '--single-timeout', '10', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_args_multi_sim_should_fail(self):
        '''Checks that: eda multi --fail-if-no-targets; will fail b/c the found target fails'''
        chdir_remove_work_dir('../../lib/tests')
        # We'd expect this to fail b/c --xilinx and --tool verilator flags an error. I do not
        # want to use the xfail pytest decorator.
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--seed=1', '--xilinx', '--tool',
                      'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc > 1

    def test_args_multi_sim_no_targets_should_fail(self):
        '''Checks that: eda multi --fail-if-no-targets; will fail if no targets expanded'''
        chdir_remove_work_dir('../../lib/tests')
        # We'd expect this to fail b/c no_targets* should expand to nothing.
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--seed=1', '--tool', 'verilator',
                      'no_targets*')
        print(f'{rc=}')
        assert rc > 1

    def test_elab_verilator_no_deps_files_involved(self):
        '''Test that inferring the --top from last file in provides files works.'''
        # no --top set, have to infer its final file name.
        chdir_remove_work_dir('../../lib')

        cmd_list = (
            'elab --tool verilator +incdir+.. oclib_assert_pkg.sv oclib_pkg.sv'
            ' ../sim/ocsim_pkg.sv ../sim/ocsim_urand.sv ./rams/oclib_ram1r1w_infer.sv'
            ' ./rams/oclib_ram1r1w_infer_core.v oclib_fifo.sv'
        ).split()

        rc = eda.main(*cmd_list)
        print(f'{rc=}')
        assert rc == 0
        # We don't get a log for this, but we can check the output generated eda_output_config.yml.
        eda_config_yml_path = os.path.join(
            os.getcwd(), 'eda.work', 'oclib_fifo.elab', 'eda_output_config.yml'
        )
        data = yaml_safe_load(eda_config_yml_path)
        assert 'args' in data
        assert data['args'].get('top', '') == 'oclib_fifo'
        assert 'config' in data
        assert 'eda_original_args' in data['config']
        assert 'oclib_fifo.sv' in data['config']['eda_original_args']
        assert data.get('target', '') == 'oclib_fifo'

    def test_elab_verilator_some_deps_files_involved(self):
        '''Test calling targets (not files) on CLI.'''
        # no --top set, have to infer its final file name.
        chdir_remove_work_dir('../../lib')
        cmd_list = 'elab --tool verilator +incdir+.. all_pkg oclib_ram1r1w oclib_fifo.sv'.split()
        rc = eda.main(*cmd_list)
        print(f'{rc=}')
        assert rc == 0
        # We don't get a log for this, but we can check the output generated eda_output_config.yml.
        eda_config_yml_path = os.path.join(
            os.getcwd(), 'eda.work', 'oclib_fifo.elab', 'eda_output_config.yml'
        )
        data = yaml_safe_load(eda_config_yml_path)
        assert 'args' in data
        assert data['args'].get('top', '') == 'oclib_fifo'
        assert 'config' in data
        assert 'eda_original_args' in data['config']
        assert 'oclib_fifo.sv' in data['config']['eda_original_args']
        assert 'all_pkg' in data['config']['eda_original_args']
        assert 'oclib_ram1r1w' in data['config']['eda_original_args']
        assert data.get('target', '') == 'oclib_fifo'

    def test_elab_verilator_no_deps_files_involved_should_fail(self):
        '''Test using no DEPS file on file that doesn't exist.'''
        chdir_remove_work_dir('../../lib')
        # pick some non-existent file oclib_doesnt_exist.nope.sv
        cmd_list = 'elab --tool verilator +incdir+.. oclib_doesnt_exist.nope.sv'.split()
        cmd_list +=' oclib_assert_pkg.sv oclib_pkg.sv oclib_fifo.sv'.split()
        rc = eda.main(*cmd_list)
        print(f'{rc=}')
        assert rc > 1

    def test_config_reduced_yml(self):
        '''Test using provided EDA --config-yml=eda_config_reduced.yml, confirm installed w/ pip'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--config-yml', 'eda_config_reduced.yml', '--tool', 'verilator',
                          'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_config_max_verilator_waivers_yml(self):
        '''Test using provided EDA --config-yml, confirm installed w/ pip'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--config-yml', 'eda_config_max_verilator_waivers.yml', '--tool',
                          'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_config_yml_custom(self):
        '''Test using user-custom --config-yml arg'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--config-yml', '../../opencos/tests/custom_config.yml', '--tool',
                          'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0
        eda_config_yml_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_fifo_test.sim',
                                           'eda_output_config.yml')
        data = yaml_safe_load(eda_config_yml_path)
        # make sure this config was actually used. We no longer re-add it to args
        # (it won't show up in 'original_args') it will will show up in the config though:
        used_yml_fname = data['config']['config-yml']
        assert used_yml_fname.endswith('opencos/tests/custom_config.yml')
        # this config overrides a value to False:
        assert 'config' in data
        local_config = data['config']
        assert local_config['dep_command_enables']['shell'] is False

    def test_verilator_rtl_missing_dumpfile_fst(self):
        '''test for eda with --waves, on RTL that has no $dumpfile,
        and we should auto-add _waves_pkg.sv with dump.fst'''

        chdir_remove_work_dir('./deps_files/test_deps_noext')
        rc = eda_wrap('sim', '--tool', 'verilator', '--waves', 'target_test')
        print(f'{rc=}')
        assert rc == 0

        assert not os.path.exists(
            os.path.join(os.getcwd(), 'eda.work', 'target_test.sim', 'dump.vcd')
        )
        assert os.path.exists(
            os.path.join(os.getcwd(), 'eda.work', 'target_test.sim', 'dump.fst')
        )

    def test_verilator_rtl_missing_dumpfile_vcd(self):
        '''test for eda with --waves, on RTL that has no $dumpfile,
        and we should auto-add _waves_pkg.sv with dump.vcd'''

        chdir_remove_work_dir('./deps_files/test_deps_noext')
        rc = eda_wrap('sim', '--tool', 'verilator', '--waves', '+trace=vcd', 'target_test')
        print(f'{rc=}')
        assert rc == 0

        assert os.path.exists(
            os.path.join(os.getcwd(), 'eda.work', 'target_test.sim', 'dump.vcd')
        )
        assert not os.path.exists(
            os.path.join(os.getcwd(), 'eda.work', 'target_test.sim', 'dump.fst')
        )

    def test_verilator_rtl_missing_dumpfile_none(self):
        '''test for eda with NO --waves, on RTL that has no $dumpfile,
        and we should see no auto-added _waves_pkg.sv and no dump.[vcd|fst]'''

        chdir_remove_work_dir('./deps_files/test_deps_noext')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_test')
        print(f'{rc=}')
        assert rc == 0

        assert not os.path.exists(
            os.path.join(os.getcwd(), 'eda.work', 'target_test.sim', 'dump.vcd')
        )
        assert not os.path.exists(
            os.path.join(os.getcwd(), 'eda.work', 'target_test.sim', 'dump.fst')
        )


class TestMissingDepsFileErrorMessages(Helpers):
    '''Test for missing DEPS.yml file, using 'eda export' to avoid tools.'''
    DEFAULT_DIR = os.path.join(THISPATH, 'deps_files', 'no_deps_here', 'empty')

    def test_bad0(self):
        '''Looks for target_bad0, but there is no DEPS file in .'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad0')
        assert rc > 1
        assert self.is_in_log(
            'Trying to resolve command-line target=./target_bad0:'
            ' but path ./ has no DEPS markup file',
            windows_path_support=True
        )


class TestDepsResolveErrorMessages(Helpers):
    '''Tests to check that error messaging with DEPS.yml works as expected.

    If this was not checked, we could have failing tests that produce a stacktrace
    or other less helpful information to the user. This confirms that file/target/
    linenumber information is printed when available.'''

    DEFAULT_DIR = os.path.join(THISPATH, 'deps_files', 'error_msgs')

    # files foo.sv, foo2.sv, target_bad0.sv, and target_bad1.sv exist.
    # files missing*.sv and targets missing* do not exist.
    # These all "export" targets, to avoid requiring an installed tool (for example, to elab)

    def test_good0(self):
        '''Simple test with good target (foo)'''
        self.chdir()
        rc = self.log_it('export foo')
        assert rc == 0

    def test_good1(self):
        '''Simple test with good target (foo2)'''
        self.chdir()
        rc = self.log_it('export foo2')
        assert rc == 0

    def test_good2(self):
        '''Simple test with good target (foo + top=foo using deps str)'''
        self.chdir()
        rc = self.log_it('export target_good2')
        assert rc == 0

    def test_good3(self):
        '''Simple test with good target (foo2 + top=foo2 using deps list)'''
        self.chdir()
        rc = self.log_it('export target_good3')
        assert rc == 0

    # Bit of a change-detector-test here, but I want to make sure the
    # line= numbers get reported correctly for the calling target.
    def test_bad0(self):
        '''Tests missing file in DEPS target using implicit deps str style'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad0')
        assert rc > 1
        assert self.is_in_log(
            "target=./missing0.sv (file?): called from ./DEPS.yml::target_bad0::line=20,",
            "File=missing0.sv not found in directory=.",
            windows_path_support=True
        )

    def test_bad1(self):
        '''Tests missing file in DEPS target using implicit deps list style'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad1')
        assert rc > 1
        assert self.is_in_log(
            "target=./missing1.sv (file?): called from ./DEPS.yml::target_bad1::line=24,",
            "File=missing1.sv not found in directory=.",
            windows_path_support=True
        )

    def test_bad2(self):
        '''Tests missing file in DEPS target using deps as str style'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad2')
        assert rc > 1
        assert self.is_in_log(
            "target=./missing2.sv (file?): called from ./DEPS.yml::target_bad2::line=28,",
            "File=missing2.sv not found in directory=.",
            windows_path_support=True
        )

    def test_bad3(self):
        '''Tests missing file in DEPS target using deps as list style'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad3')
        assert rc > 1
        assert self.is_in_log(
            "target=./missing3.sv (file?): called from ./DEPS.yml::target_bad3::line=33,",
            "File=missing3.sv not found in directory=.",
            windows_path_support=True
        )

    def test_bad4(self):
        '''EDA on a bad target (bad target within deps of 'target_bad4'), explicit deps str'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad4')
        assert rc > 1
        assert self.is_in_log(
            "target=./missing_target4: called from ./DEPS.yml::target_bad4::line=39,",
            "Target not found in deps_file=./DEPS.yml",
            windows_path_support=True
        )

    def test_bad5(self):
        '''EDA on a bad target (bad target within deps of 'target_bad4'), explicit deps list'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad5')
        assert rc > 1
        assert self.is_in_log(
            "target=./missing_target5: called from ./DEPS.yml::target_bad5::line=43,",
            "Target not found in deps_file=./DEPS.yml",
            windows_path_support=True
        )

    def test_bad6(self):
        '''EDA on a bad target (bad target within deps of 'target_bad4'), deps str'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad6')
        assert rc > 1
        assert self.is_in_log(
            "target=./missing_target6: called from ./DEPS.yml::target_bad6::line=47,",
            "Target not found in deps_file=./DEPS.yml",
            windows_path_support=True

        )

    def test_bad7(self):
        '''EDA on a bad target (bad target within deps of 'target_bad4'), deps list'''
        self.chdir()
        rc = self.log_it(command_str='export target_bad7')
        assert rc > 1
        assert self.is_in_log(
            "target=./missing_target7: called from ./DEPS.yml::target_bad7::line=52,",
            "Target not found in deps_file=./DEPS.yml",
            windows_path_support=True
        )

    def test_cmd_line_good0(self):
        '''EDA w/ out DEPS, on file'''
        self.chdir()
        rc = self.log_it(command_str='export foo.sv')
        assert rc == 0

    def test_cmd_line_good1(self):
        '''EDA w/ out DEPS, on two files'''
        self.chdir()
        rc = self.log_it(command_str='export foo.sv foo2.sv')
        assert rc == 0

    def test_cmd_line_bad0(self):
        '''EDA calling a non-existent target in DEPS file'''
        self.chdir()
        rc = self.log_it(command_str='export nope_target0')
        assert rc > 1
        assert self.is_in_log(
            "Trying to resolve command-line target=./nope_target0: was not",
            "found in deps_file=./DEPS.yml, possible targets in deps file = ['foo'",
            windows_path_support=True
        )

    def test_cmd_line_bad1(self):
        '''EDA calling a non-existent target in DEPS file, with file that exists.'''
        self.chdir()
        rc = self.log_it(command_str='export foo.sv nope_target1')
        assert rc > 1
        assert self.is_in_log(
            "Trying to resolve command-line target=./nope_target1: was not",
            "found in deps_file=./DEPS.yml, possible targets in deps file = ['foo'",
            windows_path_support=True
        )

    def test_cmd_line_bad2(self):
        '''EDA calling a non-existent file w/out DEPS'''
        self.chdir()
        rc = self.log_it(command_str='export nope_file0.sv')
        assert rc > 1
        assert self.is_in_log(
            "Trying to resolve command-line target=./nope_file0.sv",
            "(file?): File=nope_file0.sv not found in directory=.",
            windows_path_support=True
        )

    def test_cmd_line_bad3(self):
        '''EDA calling a non-existent file w/out DEPS, and a file that does exist.'''
        self.chdir()
        rc = self.log_it(command_str='export foo2.sv nope_file1.sv')
        assert rc > 1
        assert self.is_in_log(
            "Trying to resolve command-line target=./nope_file1.sv",
            "(file?): File=nope_file1.sv not found in directory=.",
            windows_path_support=True
        )


@pytest.mark.skipif('iverilog' not in tools_loaded, reason="requires iverilog")
class TestsRequiresIVerilog(Helpers):
    '''Test for Icarus Verilog'''

    def test_iverilog_help(self):
        '''Test for help'''
        rc = self.log_it('sim --tool iverilog help', use_eda_wrap=False)
        print(f'{rc=}')
        assert rc == 0
        assert self.is_in_log('Detected iverilog')
        assert self.is_in_log("Generic help for command='sim' (using 'CommandSimIverilog')")

    def test_iverilog_sim(self):
        '''Test for command sim'''
        chdir_remove_work_dir('deps_files/iverilog_test')
        cmd_list = 'sim --tool iverilog target_test'.split()
        rc = eda.main(*cmd_list)
        print(f'{rc=}')
        assert rc == 0


@pytest.mark.skipif(not can_run_eda_sim(), reason='no tool found to handle command: sim')
class TestDepsReqs:
    '''Tests for 'reqs' in the DEPS files. 'reqs' are requirements, like a .pcap or file
    used by SV $readmemh. They do not fit into normal compilable files (.sv, .v, .vhd[l])
    but are needed for export (command) and --export* (args on non-export command).'''

    def test_deps_reqs(self):
        '''Basic test using a .mem file in the 'deps' section of a target '''
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim foo_test'.split()
        rc = eda.main(*cmd_list)
        assert rc == 0

    def test_deps_reqs2(self):
        '''Basic test using a .mem file in the 'reqs' section of a target'''
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim foo_test2'.split()
        rc = eda.main(*cmd_list)
        assert rc == 0

    def test_deps_reqs3(self):
        '''Basic test using a .svh file in the 'reqs' section of a target'''
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim foo_test3'.split()
        rc = eda.main(*cmd_list)
        assert rc == 0

    def test_deps_reqs4(self):
        '''Basic test using a .svh file with just incdirs (no reqs).'''
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim foo_test4'.split()
        rc = eda.main(*cmd_list)
        assert rc == 0

    def test_deps_reqs5(self):
        '''Test that should fail due to reqs (bad file in reqs section)'''
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim should_fail_foo_test5'.split()
        rc = eda.main(*cmd_list)
        assert rc > 1

    def test_deps_reqs6(self):
        '''Test that should fail due bad file in deps section (none in reqs)'''
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim should_fail_foo_test6'.split()
        rc = eda.main(*cmd_list)
        assert rc > 1


@pytest.mark.parametrize("command", ['sim', 'shell'])
def test_deps_command_order(command):
    '''Test for various "commands" within a DEPS target. This test checks that command
    order is preserved in the top-to-bottom deps order, meaning that eda.py has to collect
    all commands deps order, and then execute them in that order.'''

    chdir_remove_work_dir('deps_files/command_order')
    if command == 'sim' and not can_run_eda_sim():
        pytest.skip(f'sim skipped, {can_run_eda_sim()=}')
        return # skip/pass

    if command == 'shell':
        cmd_list = 'shell target_test'.split()
    else:
        cmd_list = 'sim --stop-before-compile target_test'.split()

    with open('eda.log', 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            with redirect_stderr(f):
                rc = eda.main(*cmd_list)

    print(f'{rc=}')
    assert rc == 0

    # We should see "hi" before "bye" to confirm deps + command order is correct.
    # see ./deps_files/command_order/DEPS.yml - target = target_test
    found_str_list = [
        'exec: echo "hi"',
        'exec: echo "bye"',
    ]
    found_lines_list = [None, None]

    with open('eda.log', encoding='utf-8') as f:
        for lineno, line in enumerate(f.readlines()):
            line = line.rstrip()
            for idx,key in enumerate(found_str_list):
                if key in line:
                    found_lines_list[idx] = lineno

    assert found_lines_list[0] # found hi
    assert found_lines_list[1] # found bye
    assert found_lines_list[0] < found_lines_list[1] # hi before bye

    # Added check, we redirected to create eda.log earlier to confirm the targets worked,
    # but as a general eda.py check, all shell commands should create their own
    # {target}__shell_0.log file:
    work_dir = os.path.join(
        THISPATH, 'deps_files', 'command_order', 'eda.work', f'target_test.{command}'
    )
    # Note that eda will write out the returncode INFO line to tee'd log files, so
    # there is more in the log file than "hi" or "bye".
    with open(os.path.join(work_dir, 'target_echo_hi__shell_0.log'), encoding='utf-8') as f:
        text = ' '.join(f.readlines()).strip()
        assert any(text.startswith(x) for x in ['hi', '"hi"', '\\"hi\\"'])
    # Added check, one of the targets uses a custom 'tee' file name, instead of the default log.
    with open(os.path.join(work_dir, 'custom_tee_echo_bye.log'), encoding='utf-8') as f:
        text = ''.join(f.readlines()).strip()
        assert any(text.startswith(x) for x in ['bye', '"bye"', '\\"bye\\"'])


@pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
class TestDepsOtherMarkup:
    '''Tests for DEPS files that aren't YAML file extension.'''

    def test_deps_toml(self):
        '''test for DEPS.toml'''
        chdir_remove_work_dir('./deps_files/test_deps_toml')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_test')
        print(f'{rc=}')
        assert rc == 0

    def test_deps_json(self):
        '''test for DEPS.json'''
        chdir_remove_work_dir('./deps_files/test_deps_json')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_test')
        print(f'{rc=}')
        assert rc == 0

    def test_deps_no_extension(self):
        '''test for DEPS, which is treated as YAML'''
        chdir_remove_work_dir('./deps_files/test_deps_noext')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_test')
        print(f'{rc=}')
        assert rc == 0

@pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
class TestForceFileExt(Helpers):
    '''Tests for treating non .sv files (.txt) as SV using sv@<file>'''

    def test_sv_at(self):
        '''test for file as sv@<file>'''
        chdir_remove_work_dir('./deps_files/force_file_ext')
        rc = self.log_it('sim --tool verilator sv@foo.txt')
        assert rc == 0
        assert self.is_in_log("force_file_ext/foo.txt:6: Verilog $finish")

    def test_v_at(self):
        '''test for file as v@<file>'''
        chdir_remove_work_dir('./deps_files/force_file_ext')
        rc = self.log_it('sim --tool verilator v@foo.txt')
        assert rc == 0
        assert self.is_in_log("force_file_ext/foo.txt:6: Verilog $finish")


@pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
class TestDepsNoFilesTargets(Helpers):
    '''series of tests for running EDA w/out a DEPS target, all CLI files.'''

    def test_eda_sim__use_implicit_one_target(self):
        '''This test should work if the DEPS markup has a single target only'''
        # Using this b/c DEPS.toml has single target.
        chdir_remove_work_dir('./deps_files/test_deps_toml')
        rc = self.log_it('sim --tool verilator')
        assert rc == 0
        # Confirm the 'target_test' was used.
        assert self.is_in_log("using 'target_test' from")
        exec_lines = self.get_log_lines_with('exec: ')
        assert 'verilator ' in exec_lines[0]
        assert self.is_in_log("test_deps_toml/foo.sv:6: Verilog $finish")

    def test_eda_sim__wrong_target_shouldfail(self):
        '''This test should fail, wrong target name'''
        # Using this b/c DEPS.toml has single target.
        chdir_remove_work_dir('./deps_files/test_deps_toml')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_whoops')
        assert rc > 1

    def test_eda_sim__no_files_or_targets_shouldfail(self):
        '''This test should fail, there is DEPS.yml (empty, no implicit target), or missing file'''
        chdir_remove_work_dir('./deps_files/no_deps_here')
        rc = eda_wrap('sim', '--tool', 'verilator')
        assert rc > 1

    def test_eda_sim__no_files_or_targets_with_top_shouldfail(self):
        '''This test should fail, there is DEPS.yml (empty, no implicit target), or missing file'''
        chdir_remove_work_dir('./deps_files/no_deps_here')
        rc = eda_wrap('sim', '--tool', 'verilator', '--top', 'empty_file')
        assert rc > 1


class TestDepsTags(Helpers):
    '''Series of tests for DEPS - target - tags, in ./deps_files/tags_with_tools'''
    DEFAULT_DIR = os.path.join(THISPATH, 'deps_files', 'tags_with_tools')

    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_verilator(self):
        '''test for DEPS target that hits with-tools: verilator, so that
        additional args are applied from the DEPS tag.'''
        self.chdir()
        logfile = '.pytest.verilator_eda.log'
        rc = self.log_it('sim --tool verilator target_test', logfile=logfile)
        assert rc == 0

        # so the full sim should have not run
        exec_lines = self.get_log_lines_with('exec: ', logfile=logfile)
        assert len(exec_lines) == 1, \
            f'{exec_lines=} should have only been the compile --lint-only'
        assert 'exec: ' in exec_lines[0] and 'verilator ' in exec_lines[0], \
            f'{exec_lines[0]=} should have been verilator compile'


    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_replace_config_tools_verilator(self):
        '''test for DEPS target with tags that perfoms replacement config.

        AKA, lets you replace all the Verilator waivers to the DEPS target that only affect
        with-tools: verilator'''
        self.chdir()
        logfile = '.pytest.target_with_replace_config_tools_test.log'
        rc = self.log_it('sim --tool verilator target_with_replace_config_tools_test',
                         logfile=logfile)
        assert rc == 0
        # This target overrode all the Verilator waivers to nothing, so
        # we should see zero -Wno- in the log for verilator exec lines.
        exec_lines = self.get_log_lines_with('exec: ', logfile=logfile)
        assert len(exec_lines) == 2
        assert not '-Wno-' in exec_lines[0], f'-Wno- expected to be in one of: {exec_lines=}'


    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_additive_config_tools_verilator(self):
        '''test for DEPS target with tags that perfoms additive config.

        AKA, lets you add Verilator waivers to the DEPS target that only affect
        with-tools: verilator'''
        self.chdir()
        logfile = '.pytest.target_with_additive_config_tools_test.log'
        rc = self.log_it('sim --tool verilator --debug target_with_additive_config_tools_test',
                         logfile=logfile)
        assert rc == 0
        # This target added to the Verilator waivers -Wno-style, -Wno-fatal,
        # but the defaults should also be there (at least -Wno-UNSIGNED)
        waivers = self.get_log_words_with('-Wno-', logfile=logfile)
        assert '-Wno-style' in waivers
        assert '-Wno-fatal' in waivers
        assert '-Wno-UNSIGNED' in waivers


    @pytest.mark.skipif('vivado' not in tools_loaded, reason="requires vivado")
    def test_tags_with_tools_vivado(self):
        '''test for DEPS target with tag using with-tools: verilator

        Since we're running --tool=vivado (not verilator) this should not
        apply the arg --lint-only in the DEPS tag, and instead run the
        full simulation.'''
        self.chdir()
        logfile = '.pytest.vivado_eda.log'
        rc = self.log_it('sim --tool vivado target_test', logfile=logfile)
        assert rc == 0

        # make sure the tag wasn't applied (should only be applied in verilator)
        # so the full sim should have run (xvlog, xelab, xsim) (--lint-only not applied,
        # b/c that should only apply in 'verilator' for this target.)
        exec_lines = self.get_log_lines_with('exec: ', logfile=logfile)
        assert len(exec_lines) == 3
        assert 'xvlog' in exec_lines[0]
        assert 'xelab' in exec_lines[1]
        assert 'xsim' in exec_lines[2]
        assert not self.is_in_log('--lint-only', logfile=logfile)


    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_add_incdirs(self):
        '''test for DEPS target with tag that adds incdirs'''
        self.chdir()
        logfile = '.pytest.target_foo_sv_add_incdirs.log'
        rc = self.log_it('elab --tool verilator target_foo_sv_add_incdirs',
                         logfile=logfile)
        assert rc == 0
        # This target added . to incdirs in the DEPS.yml dir.

        incdirs = self.get_log_words_with('+incdir+', logfile=logfile)
        assert len(incdirs) == 1 # should only have 1
        assert 'tests/deps_files/tags_with_tools' in incdirs[0]


    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_add_defines(self):
        '''test for DEPS target with tag that adds defines'''
        self.chdir()
        logfile = '.pytest.target_foo_sv_add_defines.log'
        rc = self.log_it('elab --tool verilator --debug target_foo_sv_add_defines',
                         logfile=logfile)
        assert rc == 0
        assert self.is_in_log('+define+FOO_SV=3000', logfile=logfile)
