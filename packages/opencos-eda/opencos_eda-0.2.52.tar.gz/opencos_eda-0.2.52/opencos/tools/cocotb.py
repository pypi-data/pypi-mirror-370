''' opencos.tools.cocotb - Used by opencos.eda for sim commands with --tool=cocotb.

Contains classes for ToolCocotb, CommandSimCocotb.
'''

import os
import shutil
import subprocess

from opencos import util
from opencos.eda_base import Tool
from opencos.commands import CommandSim
from opencos.utils.str_helpers import sanitize_defines_for_sh


class ToolCocotb(Tool):
    '''ToolCocotb used by opencos.eda for --tool=cocotb'''

    _TOOL = 'cocotb'
    _EXE = 'python'
    _URL = 'https://github.com/cocotb/cocotb'

    cocotb_version = ''
    python_exe = ''

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION

        # Check if python is available
        python_path = shutil.which('python') or shutil.which('python3')
        if not python_path:
            self.error('"python" or "python3" not in path, required for cocotb')
        else:
            self.python_exe = python_path

        # Check if cocotb is installed
        try:
            version_ret = subprocess.run(
                [self.python_exe, '-c', 'import cocotb; print(cocotb.__version__)'],
                capture_output=True,
                check=True,
                text=True
            )
            version = version_ret.stdout.strip()
            self.cocotb_version = version
            self._VERSION = version
            util.debug(f'Found cocotb version: {version}')
            return self._VERSION
        except subprocess.CalledProcessError:
            self.error('cocotb package not installed in python environment. '
                      'Install with: pip install cocotb')
        except Exception as e:
            self.error(f'Failed to check cocotb version: {e}')

        return ''

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'SIMULATION': 1,
            'COCOTB': 1,
            'OC_TOOL_COCOTB': None,
        })


class CommandSimCocotb(CommandSim, ToolCocotb):
    '''CommandSimCocotb is a command handler for: eda sim --tool=cocotb'''

    def __init__(self, config: dict):
        CommandSim.__init__(self, config)
        ToolCocotb.__init__(self, config=self.config)

        self.args.update({
            'gui': False,
            'tcl-file': None,
            'cocotb-test-module': None,
            'cocotb-test-runner': 'python',
            'cocotb-simulator': 'verilator',
            'cocotb-makefile': False,
            'cocotb-python-runner': True,
            'cocotb-standalone-makefile': False,
        })

        self.args_help.update({
            'waves': 'Include waveforms by setting COCOTB_ENABLE_WAVES=1',
            'cocotb-test-module': 'Python test module name (e.g., test_my_design)',
            'cocotb-test-runner': 'Test runner to use: python (default) or pytest',
            'cocotb-simulator': ('Simulator backend: verilator (default), icarus, etc.'
                                 ' Note that iverilog will convert to icarus here'),
            'cocotb-makefile': 'Use traditional Makefile system instead of Python runner',
            'cocotb-python-runner': 'Use Python-based runner system (default, cocotb 1.8+)',
            'cocotb-standalone-makefile': ('Use provided Makefile as-is, '
                                          'run make in source directory'),
        })

        self.cocotb_command_lists = []
        self.cocotb_test_files = []

    def set_tool_defines(self):
        ToolCocotb.set_tool_defines(self)

    def prepare_compile(self):
        self.set_tool_defines()

        # Fix iverilog -> icarus
        if self.args['cocotb-simulator'] == 'iverilog':
            self.args['cocotb-simulator'] = 'icarus'

        # Find cocotb test files
        self._find_cocotb_test_files()

        if self.args['cocotb-standalone-makefile']:
            self._prepare_standalone_makefile_system()
        elif self.args['cocotb-makefile']:
            self._prepare_makefile_system()
        else:
            self._prepare_python_runner_system()

        # Create directories
        paths = ['logs', 'sim_build']
        util.safe_mkdirs(base=self.args['work-dir'], new_dirs=paths)

        # Write shell scripts
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='cocotb_test.sh',
            command_lists=self.cocotb_command_lists,
            line_breaks=True
        )

        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='all.sh',
            command_lists=[
                ['./pre_compile_dep_shell_commands.sh'],
                ['./cocotb_test.sh'],
            ]
        )

    def _find_cocotb_test_files(self):
        '''Find Python test files that contain cocotb tests'''
        self.cocotb_test_files = []

        # Look for test files in the current directory and deps
        for file_path in self.files_non_source:
            if (file_path.endswith('.py') and
                ('test' in file_path.lower() or 'tb' in file_path.lower())):
                # Check if it's a cocotb test file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'import cocotb' in content or 'from cocotb' in content:
                            self.cocotb_test_files.append(file_path)
                            util.debug(f'Found cocotb test file: {file_path}')
                except Exception as e:
                    util.debug(f'Could not read {file_path}: {e}')

        # If no test files found, look for explicit test module
        if not self.cocotb_test_files and self.args.get('cocotb-test-module'):
            test_module = self.args['cocotb-test-module']
            if not test_module.endswith('.py'):
                test_module += '.py'

            # Look in work directory and target directory
            for search_dir in [self.args['work-dir'], os.path.dirname(self.target or '.')]:
                test_path = os.path.join(search_dir, test_module)
                if os.path.exists(test_path):
                    self.cocotb_test_files.append(test_path)
                    break

        if not self.cocotb_test_files:
            self.error('No cocotb test files found. Either include .py files with '
                      'cocotb imports in your deps, or specify --cocotb-test-module')

    def _prepare_python_runner_system(self):
        '''Prepare cocotb using the Python-based runner system (cocotb 1.8+)'''

        # Create a Python runner script
        runner_script = self._create_python_runner_script()

        if self.args['cocotb-test-runner'] == 'pytest':
            # Use pytest to run the tests
            runner_script_name = os.path.basename(runner_script)
            cmd_list = [
                self.python_exe, '-m', 'pytest',
                runner_script_name,
                '-v', '-s'
            ]
        else:
            # Run the Python script directly
            runner_script_name = os.path.basename(runner_script)
            cmd_list = [self.python_exe, runner_script_name]

        # Set environment variables
        env_vars = self._get_cocotb_env_vars()

        # Create command with environment variables
        command_list = self._create_env_command(env_vars) + cmd_list
        self.cocotb_command_lists = [util.ShellCommandList(command_list,
                                                          tee_fpath='cocotb_test.log')]

    def _prepare_makefile_system(self):
        '''Prepare cocotb using the traditional Makefile system'''

        makefile_path = os.path.join(self.args['work-dir'], 'Makefile')
        with open(makefile_path, 'w', encoding='utf-8') as f:
            f.write(self._create_makefile_content())

        cmd_list = self._create_shell_command_with_success('make -f Makefile')
        self.cocotb_command_lists = [util.ShellCommandList(cmd_list,
                                                          tee_fpath='cocotb_makefile.log')]

    def _prepare_standalone_makefile_system(self):
        '''Use provided Makefile as-is, run make in source directory'''

        # Find the Makefile in our dependencies
        makefile_path = None
        for file_path in self.files_non_source:
            if os.path.basename(file_path).lower() == 'makefile':
                makefile_path = file_path
                break

        if not makefile_path:
            self.error('No Makefile found in deps for --cocotb-standalone-makefile')

        makefile_dir = os.path.dirname(os.path.abspath(makefile_path))
        cmd_list = self._create_shell_command_with_success(f'cd {makefile_dir} && make')
        self.cocotb_command_lists = [util.ShellCommandList(
            cmd_list, tee_fpath='cocotb_standalone.log')]

    def _get_test_module_name(self) -> str:
        '''Get the test module name from args or detected files'''
        if self.args.get('cocotb-test-module'):
            return self.args['cocotb-test-module']
        if self.cocotb_test_files:
            # Use the first test file found, strip .py extension
            test_file = os.path.basename(self.cocotb_test_files[0])
            return test_file.replace('.py', '')
        return 'test_design'


    def _get_hdl_sources(self) -> dict:
        '''Get HDL source files organized by type'''
        return {
            'verilog': (self.files_sv or []) + (self.files_v or []),
            'vhdl': self.files_vhd or [],
            'all': (self.files_sv or []) + (self.files_v or []) + (self.files_vhd or [])
        }

    def _create_python_runner_script(self) -> str:
        '''Create the Python runner script and return its path'''
        test_module = self._get_test_module_name()
        hdl_sources = self._get_hdl_sources()['all']

        script_content = self._generate_runner_script_content(test_module, hdl_sources)
        script_path = os.path.join(self.args['work-dir'], 'cocotb_runner.py')

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)

        return script_path

    def _generate_runner_script_content(self, test_module: str, hdl_sources: list) -> str:
        '''Generate the content for the Python runner script'''
        return f'''#!/usr/bin/env python3
"""
Cocotb test runner script generated by opencos
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path for test imports
sys.path.insert(0, os.getcwd())

try:
    from cocotb_tools.runner import get_runner
except ImportError:
    print("ERROR: cocotb not found. Install with: pip install cocotb")
    sys.exit(1)

def run_cocotb_test():
    """Run cocotb test using the Python runner system"""

    # Configuration
    simulator = "{self.args['cocotb-simulator']}"
    hdl_toplevel = "{self.args.get('top', 'top')}"
    test_module = "{test_module}"

    # HDL source files
    hdl_sources = {hdl_sources!r}

    # Convert to Path objects and make absolute
    sources = []
    for src in hdl_sources:
        src_path = Path(src)
        if not src_path.is_absolute():
            src_path = Path.cwd() / src_path
        sources.append(src_path)

    # Include directories
    include_dirs = {list(self.incdirs)!r}

    # Defines (filter out None values for cocotb compatibility)
    all_defines = {dict(self.defines)!r}
    defines = {{k: v for k, v in all_defines.items() if v is not None}}

    # Parameters (empty for simple modules without parameters)
    parameters = {{}}

    try:
        # Get the runner for the specified simulator
        runner = get_runner(simulator)

        # Build the design
        runner.build(
            sources=sources,
            hdl_toplevel=hdl_toplevel,
            includes=include_dirs,
            defines=defines,
            parameters=parameters,
            build_dir="sim_build",
        )

        # Run the test
        runner.test(
            hdl_toplevel=hdl_toplevel,
            test_module=test_module,
            test_dir=".",
        )

        print("{self._get_success_message()}")

    except Exception as e:
        print(f"ERROR: Cocotb test failed: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    run_cocotb_test()
'''

    def _create_makefile_content(self) -> str:
        '''Create Makefile content for cocotb traditional system'''

        # Determine test module
        test_module = self._get_test_module_name()

        # Get HDL sources and determine language
        hdl_sources = self._get_hdl_sources()
        verilog_sources = hdl_sources['verilog']
        vhdl_sources = hdl_sources['vhdl']

        # Determine HDL language
        if vhdl_sources and not verilog_sources:
            hdl_lang = 'vhdl'
            sources_var = 'VHDL_SOURCES'
            sources_list = ' '.join(vhdl_sources)
        else:
            hdl_lang = 'verilog'
            sources_var = 'VERILOG_SOURCES'
            sources_list = ' '.join(verilog_sources)

        makefile_content = f'''# Cocotb Makefile generated by opencos

# Simulator selection
SIM ?= {self.args['cocotb-simulator']}

# HDL language
TOPLEVEL_LANG = {hdl_lang}

# HDL sources
{sources_var} = {sources_list}

# Top level module
TOPLEVEL = {self.args.get('top', 'top')}

# Test module
MODULE = {test_module}

# Include directories
'''

        if self.incdirs:
            makefile_content += ('COMPILE_ARGS += ' +
                               ' '.join(f'-I{inc}' for inc in self.incdirs) + '\n')

        # Add defines
        if self.defines:
            define_args = []
            for k, v in self.defines.items():
                if v is None:
                    define_args.append(f'-D{k}')
                else:
                    define_args.append(f'-D{k}={sanitize_defines_for_sh(v)}')
            makefile_content += 'COMPILE_ARGS += ' + ' '.join(define_args) + '\n'

        makefile_content += '''
# Waves support
ifeq ($(WAVES),1)
    COCOTB_ENABLE_WAVES = 1
    export COCOTB_ENABLE_WAVES
endif

# Include cocotb's Makefile
include $(shell cocotb-config --makefiles)/Makefile.sim
'''

        return makefile_content

    def _get_success_message(self) -> str:
        '''Get standardized success message'''
        return "Cocotb test completed successfully!"

    def _create_shell_command_with_success(self, base_command: str) -> list:
        '''Create a shell command list with success message'''
        return ['sh', '-c', f'{base_command} && echo "{self._get_success_message()}"']

    def _get_cocotb_env_vars(self) -> dict:
        '''Get environment variables for cocotb execution'''
        env_vars = {}

        # Basic cocotb configuration
        env_vars['SIM'] = self.args['cocotb-simulator']
        env_vars['TOPLEVEL'] = self.args.get('top', 'top')

        # Enable waves if requested
        if self.args.get('waves', False):
            env_vars['COCOTB_ENABLE_WAVES'] = '1'

        # Set log level based on verbosity
        if util.args.get('verbose', False):
            env_vars['COCOTB_LOG_LEVEL'] = 'DEBUG'
        else:
            env_vars['COCOTB_LOG_LEVEL'] = 'INFO'

        # Random seed
        if self.args.get('seed'):
            env_vars['COCOTB_RANDOM_SEED'] = str(self.args['seed'])

        return env_vars

    def _create_env_command(self, env_vars: dict) -> list:
        '''Create environment variable command prefix'''
        env_cmd = []
        for key, value in env_vars.items():
            env_cmd.extend(['env', f'{key}={value}'])
        return env_cmd

    def compile(self):
        # For cocotb, compilation happens as part of the test run
        if self.args['stop-before-compile']:
            return
        util.info('Cocotb: compilation will happen during test execution')

    def elaborate(self):
        # For cocotb, elaboration happens as part of the test run
        pass

    def simulate(self):
        if self.args['stop-before-compile'] or self.args['stop-after-compile'] or \
           self.args['stop-after-elaborate']:
            return

        # Run the cocotb tests
        self.run_commands_check_logs(self.cocotb_command_lists)

    def get_compile_command_lists(self, **kwargs) -> list:
        # Cocotb handles compilation internally
        return []

    def get_elaborate_command_lists(self, **kwargs) -> list:
        # Cocotb handles elaboration internally
        return []

    def get_simulate_command_lists(self, **kwargs) -> list:
        return self.cocotb_command_lists

    def get_post_simulate_command_lists(self, **kwargs) -> list:
        return []
