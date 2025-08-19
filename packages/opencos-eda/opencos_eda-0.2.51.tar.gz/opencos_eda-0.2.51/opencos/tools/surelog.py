''' opencos.tools.surelog - Used by opencos.eda for elab commands w/ --tool=surelog

Contains classes for ToolSurelog, CommandElabSurelog
'''

import shutil
import subprocess

from opencos import util
from opencos.eda_base import Tool
from opencos.commands import CommandElab
from opencos.utils.str_helpers import sanitize_defines_for_sh


class ToolSurelog(Tool):
    '''Gets versions and holds executable for surelog, parent class for CommandElabSurelog'''

    _TOOL = 'surelog'
    _EXE = 'surelog'
    _URL = 'https://github.com/chipsalliance/Surelog'

    surelog_exe = ''

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION
        path = shutil.which(self._EXE)
        if not path:
            self.error(f'"{self._EXE}" not in path, need to get it ({self._URL})')
        else:
            self.surelog_exe = path

        version_ret = subprocess.run(
            [self.surelog_exe, '--version'], capture_output=True, check=False
        )
        stdout = version_ret.stdout.decode('utf-8', errors='replace')
        util.debug(f'{path=} {version_ret=}')
        words = stdout.split() # VERSION: 1.84 (first line)
        if len(words) < 2:
            self.error(f'{self.surelog_exe} --version: returned unexpected string {version_ret=}')
        version = words[1]
        ver_list = version.split('.')
        if len(ver_list) < 2:
            self.error(f'{self.surelog_exe} --version: returned unexpected string',
                       f'{version_ret=} {version=}')
        self._VERSION = version
        return self._VERSION

    def set_tool_defines(self):
        self.defines['OC_TOOL_SURELOG'] = None # add define
        if 'SYNTHESIS' not in self.defines:
            self.defines['SIMULATION'] = None # add define
        # Expected to manually add SYNTHESIS command line or target, otherwise.
        # Similarly, you could use --tool slang_yosys for a synthesis friendly
        # elab in Yosys.


class CommandElabSurelog(CommandElab, ToolSurelog):
    '''CommandElabSurelog is a command handler for: eda elab --tool=surelog'''

    def __init__(self, config:dict):
        CommandElab.__init__(self, config)
        ToolSurelog.__init__(self, config=self.config)
        self.args.update({
            'surelog-top': '',
        })

        self.surelog_command_lists = []


    # Note that we follow parent class CommandSim's do_it() flow, that way --export args
    # are handled.
    def prepare_compile(self) -> None:
        ''' prepare_compile() - following parent Commandsim's run() flow'''
        self.set_tool_defines()
        self.write_eda_config_and_args()

        self.surelog_command_lists = self.get_compile_command_lists()
        self.write_surelog_sh()

    def compile(self) -> None:
        pass

    def elaborate(self) -> None:
        ''' elaborate() - following parent Commandsim's run() flow, runs slang_command_lists'''
        if self.args['stop-before-compile'] or \
           self.args['stop-after-compile']:
            return
        self.run_commands_check_logs(self.surelog_command_lists)

    def get_compile_command_lists(self, **kwargs) -> list:
        '''Returns list of util.ShellCommandList, for surelog we'll run this in elaborate()'''
        command_list = [
            self.surelog_exe
        ]

        config_compile_args = self.tool_config.get(
            'compile-args',
            '-parse').split()
        command_list += config_compile_args

        if util.args.get('debug', None) or \
           util.args.get('verbose', None):
            command_list.append('-verbose')

        # incdirs
        for value in self.incdirs:
            command_list.append('+incdir+' + value)

        # defines:
        for k,v in self.defines.items():
            if v is None:
                command_list.append( f'+define+{k}' )
            else:
                # Generally we should only support int and str python types passed as
                # +define+{k}={v}
                command_list.append( f'+define+{k}={sanitize_defines_for_sh(v)}' )

        # Because many elab target-name won't match the --top needed for
        # slang, we'll leave this to arg --surelog-top:
        if self.args.get('surelog-top', None):
            command_list += [ '--top-module', self.args['surelog-top'] ]

        for vfile in self.files_v:
            command_list += [ '-v', vfile ]
        for svfile in self.files_sv:
            command_list += [ '-sv', svfile]

        command_list = util.ShellCommandList(command_list, tee_fpath='compile.log')
        return [command_list]

    def get_elaborate_command_lists(self, **kwargs) -> list:
        return []

    def write_surelog_sh(self) -> None:
        '''Returns None, writes run_surelog.sh for reproducing outside of the eda framework.'''

        util.write_shell_command_file(
            dirpath=self.args['work-dir'], filename='run_surelog.sh',
            command_lists=self.surelog_command_lists, line_breaks=True
        )
