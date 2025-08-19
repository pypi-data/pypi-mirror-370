''' opencos.tools.slang - Used by opencos.eda for elab commands w/ --tool=slang

Contains classes for ToolSlang, CommandElabSlang
'''

# pylint: disable=R0801 # (calling functions with same arguments)

import os
import shutil
import subprocess

from opencos import util
from opencos.eda_base import Tool
from opencos.commands import CommandElab
from opencos.utils.str_helpers import sanitize_defines_for_sh


class ToolSlang(Tool):
    '''ToolSlang used by opencos.eda for --tool=slang'''

    _TOOL = 'slang'
    _EXE = 'slang'
    _URL = 'https://github.com/MikePopoloski/slang'

    slang_exe = ''
    slang_base_path = ''
    slang_tidy_exe = ''
    slang_hier_exe = ''

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION
        path = shutil.which(self._EXE)
        if not path:
            self.error(f'"{self._EXE}" not in path, need to get it ({self._URL}')
        else:
            self.slang_exe = path
            self.slang_base_path, _ = os.path.split(path)
            self.slang_tidy_exe = os.path.join(self.slang_base_path, 'slang-tidy')
            self.slang_hier_exe = os.path.join(self.slang_base_path, 'slang-hier')

        version_ret = subprocess.run(
            [self.slang_exe, '--version'],
            capture_output=True,
            check=False
        )
        stdout = version_ret.stdout.decode('utf-8', errors='replace')
        util.debug(f'{path=} {version_ret=}')
        words = stdout.split() # slang version 8.0.6+b4a74b00
        if len(words) < 3:
            self.error(f'{self.slang_exe} --version: returned unexpected string {version_ret=}')
        version = words[2]
        left, _ = version.split('+')
        ver_list = left.split('.')
        if len(ver_list) != 3:
            self.error(f'{self.slang_exe} --version: returned unexpected string',
                       f'{version_ret=} {version=}')
        self._VERSION = left
        return self._VERSION

    def set_tool_defines(self):
        self.defines['OC_TOOL_SLANG'] = None # add define
        if 'SYNTHESIS' not in self.defines:
            self.defines['SIMULATION'] = None # add define
        # Expected to manually add SYNTHESIS command line or target, otherwise.
        # Similarly, you could use --tool slang_yosys for a synthesis friendly
        # elab in Yosys.


class CommandElabSlang(CommandElab, ToolSlang):
    '''CommandElabSlang is a command handler for: eda elab --tool=slang'''

    def __init__(self, config:dict):
        CommandElab.__init__(self, config=config)
        ToolSlang.__init__(self, config=self.config)
        self.args.update({
            'slang-args': [], # aka, --single-unit, --ast-json <fname>, --ast-json-source-info
            'slang-json': False, # sets all the args I know of for AST.
            'slang-top': '',
            'tidy': False, # run slang-tidy instead of slang
            'hier': False, # run slang-hier instead of slang
        })

        self.all_json_args = [
            '--ast-json', ## needs filename: slang.json'
            '--ast-json-source-info',
            '--ast-json-detailed-types',
        ]

        self.args_help.update({
            'tidy': "Runs 'slang-tidy' instead of 'slang', with no ast- args.",
            'hier': "Runs 'slang-hier' instead of 'slang', with no ast- args.",
        })


        # If we're in elab, so not in general ToolSlang, set define for SLANG
        self.defines.update({
            'SLANG': 1
        })

        self.slang_command_lists = []


    # Note that we follow parent class CommandSim's do_it() flow, that way --export args
    # are handled.
    def prepare_compile(self):
        ''' prepare_compile() - following parent Commandsim's run() flow'''
        self.set_tool_defines()
        self.write_eda_config_and_args()

        self.slang_command_lists = self.get_compile_command_lists()
        self.write_slang_sh()

    def compile(self):
        pass

    def elaborate(self):
        ''' elaborate() - following parent Commandsim's run() flow, runs slang_command_lists'''
        if self.args['stop-before-compile'] or \
           self.args['stop-after-compile']:
            return
        self.run_commands_check_logs(self.slang_command_lists)

    def get_compile_command_lists(self, **kwargs) -> list:
        '''Returns list of util.ShellCommandList, for slang we'll run this in elaborate()'''

        command_list = self._get_slang_command_list_start() # slang vs slang-tidy vs slang-hier
        command_list += self.tool_config.get('compile-args', '--single-unit').split()
        command_list += self.args['slang-args'] # add user args.
        command_list += self._get_slang_json_args(command_exe=command_list[0])

        # incdirs
        for value in self.incdirs:
            command_list += [ '--include-directory', value ]

        # defines:
        for k,v in self.defines.items():
            command_list.append( '--define-macro' )
            if v is None:
                command_list.append( k )
            else:
                # Generally we should only support int and str python types passed as
                # --define-macro {k}={v}
                command_list.append( f'{k}={sanitize_defines_for_sh(v)}' )

        # Because many elab target-name won't match the --top needed for
        # slang, we'll leave this to arg --slang-top:
        if self.args.get('slang-top', None):
            command_list += [ '--top', self.args['slang-top'] ]


        command_list += self.files_sv + self.files_v

        command_list = util.ShellCommandList(command_list, tee_fpath='compile.log')
        return [command_list]

    def write_slang_sh(self):
        '''Writes run_slang.sh to work-dir'''
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_slang.sh',
            command_lists=self.slang_command_lists,
            line_breaks=True
        )

    def get_elaborate_command_lists(self, **kwargs) -> list:
        # all handled by get_compile_command_lists()
        return []

    def get_post_simulate_command_lists(self, **kwargs) -> list:
        return []

    def _get_slang_command_list_start(self) -> list:
        command_list = [self.slang_exe]

        if self.args['tidy']:
            if not shutil.which(self.slang_tidy_exe):
                util.warning("Running tool slang with --tidy, but 'slang-tidy'",
                             "not in PATH, using 'slang' instead")
            else:
                command_list = [self.slang_tidy_exe]

        if self.args['hier']:
            if self.args['tidy']:
                util.warning('Running with --tidy and --heir, will attempt to use slang-hier')
            elif not shutil.which(self.slang_hier_exe):
                util.warning("Running tool slang with --hier, but 'slang-hier'",
                             "not in PATH, using 'slang' instead")
            else:
                command_list = [self.slang_hier_exe]

        return command_list

    def _get_slang_json_args(self, command_exe: str) -> list:
        command_list = []

        _, command_exe_leaf = os.path.split(command_exe)
        if self.args.get('slang-json', False) and command_exe_leaf == 'slang':
            for arg in self.all_json_args:
                if arg not in command_list:
                    command_list.append(arg)
                    if arg == '--ast-json': # needs filename
                        command_list.append('slang.json')
                        util.artifacts.add(
                            name=os.path.join(self.args['work-dir'], 'slang.json'),
                            typ='json',
                            description='Abstract syntax tree from slang --ast-json'
                        )

        return command_list
