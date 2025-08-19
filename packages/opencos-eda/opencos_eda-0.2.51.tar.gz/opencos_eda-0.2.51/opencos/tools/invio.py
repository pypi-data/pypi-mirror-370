''' opencos.tools.invio - class for ToolInvio to determine if Invio is present and what version'''

# pylint: disable=R0801 # (duplicate code in derived classes, such as if-condition return.)

import importlib.util

from opencos import util
from opencos.tools import invio_helpers
from opencos.eda_base import Tool
from opencos.commands import CommandElab



class ToolInvio(Tool):
    '''Invio w/out Yosys, used for elab in SIMULATIION (not the same as ToolInvioYosys)'''

    _TOOL = 'invio'
    _URL = 'https://www.verific.com/products/invio/'

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION

        # We also have to make sure we can import invio within python.
        spec = importlib.util.find_spec('invio')
        if not spec:
            self.error('"invio" package not in python env')


        return super().get_versions()

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'OC_TOOL_INVIO': None,
        })

class CommandElabInvio(CommandElab, ToolInvio):
    '''Command handler for: eda elab --tool=invio'''

    def __init__(self, config:dict):
        CommandElab.__init__(self, config)
        ToolInvio.__init__(self, config=self.config)
        self.args.update({
            'invio-blackbox': [],                # list of modules that invio/verific will blackbox.
        })

        self.invio_command_lists = []

    # Note that we follow parent class CommandSim's do_it() flow, that way --export args
    # are handled.
    def prepare_compile(self) -> None:
        ''' prepare_compile() - following parent Commandsim's run() flow'''
        self.set_tool_defines()
        self.write_eda_config_and_args()

        self.invio_command_lists = self.get_compile_command_lists()
        self.write_invio_sh()

    def compile(self) -> None:
        pass

    def elaborate(self) -> None:
        ''' elaborate() - following parent Commandsim's run() flow, runs invio_command_lists'''
        if self.args['stop-before-compile'] or \
           self.args['stop-after-compile']:
            return
        # Finally, run the command(s) if we made it this far: python run_invio.py:
        self.run_commands_check_logs(self.invio_command_lists)

    def get_compile_command_lists(self, **kwargs) -> list:
        '''Returns list of util.ShellCommandList, for slang we'll run this in elaborate()'''
        invio_blackbox_list = self.args.get('invio-blackbox', [])
        invio_dict = invio_helpers.get_invio_command_dict(
            self, blackbox_list=invio_blackbox_list, sim_elab=True
        )
        return invio_dict['command_lists']

    def write_invio_sh(self) -> None:
        '''Returns None, writes out run_invio.sh for reproducing outside of eda framework.'''
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='run_invio.sh',
                                      command_lists=self.invio_command_lists, line_breaks=True)

    def get_elaborate_command_lists(self, **kwargs) -> list:
        '''We only use 'compile' commands for invio elab, do not use elaborate commands'''
        return []
