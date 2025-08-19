''' opencos.tools.questa_fse - Used by opencos.eda for sim/elab commands w/ --tool=questa_fse.

Contains classes for CommandSimQuestaFse, CommandElabQuestaFse.
For: Questa Intel Starter FPGA Edition-64 vsim 20XX.X Simulator

'''

# pylint: disable=R0801 # (duplicate code in derived classes, such as if-condition return.)
# pylint: disable=too-many-ancestors

import os

from opencos.tools.modelsim_ase import CommandSimModelsimAse


class CommandSimQuestaFse(CommandSimModelsimAse):
    '''CommandSimQuestaFse is a command handler for: eda sim --tool=questa_fse

    Note this inherits 99% from CommandSimModelSimAse for command handling
    '''
    _TOOL = 'questa_fse'
    _EXE = 'vsim'

    def __init__(self, config: dict):
        # this will setup with self._TOOL = modelsim_ase, which is not ideal so
        # we have to repait it later.
        CommandSimModelsimAse.__init__(self, config=config)

        # repairs: override self._TOOL, and run get_versions() again.
        self._TOOL = 'questa_fse'

        self.shell_command = os.path.join(self.sim_exe_base_path, 'vsim')
        self.starter_edition = True
        self.args.update({
            'tool': self._TOOL, # override
            'gui': False,
        })


    def set_tool_defines(self):
        '''Override from questa.ToolQuesta'''
        # Update any defines from config.tools.questa_fse:
        self.defines.update(
            self.tool_config.get(
                'defines',
                # defaults, if not set:
                {
                 'OC_TOOL_QUESTA_FSE': 1
                }
            )
        )


class CommandElabQuestaFse(CommandSimQuestaFse):
    '''CommandElabQuestaFse is a command handler for: eda elab --tool=questa_fse'''

    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True
