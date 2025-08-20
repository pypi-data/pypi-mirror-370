''' opencos.tools.invio_yosys - Used by opencos.eda for elab commands w/ --tool=invio_yosys'''

# pylint: disable=R0801 # (duplicate code in derived classes, such as if-condition return.)
# pylint: disable=too-many-ancestors
# pylint: disable=too-many-locals     # TODO(drew): fix this later.

import os
import importlib.util

from opencos import util
from opencos.tools import invio_helpers
from opencos.tools.yosys import ToolYosys, CommonSynthYosys

class ToolInvioYosys(ToolYosys):
    '''ToolInvioYosys, used by CommandSynthInvioYosys for versions and checking tool existence'''

    _TOOL = 'invio_yosys'
    _URL = 'https://www.verific.com/products/invio/'
    _EXE = 'yosys'

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION

        # We also have to make sure we can import invio within python.
        spec = importlib.util.find_spec('invio')
        if not spec:
            self.error('"invio" package not in python env')

        # run ToolYosys.get_versions() to set up self.yosys_exe, and return the version
        # str:
        return ToolYosys.get_versions(self)

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'OC_TOOL_INVIO': None,
        })


class CommandSynthInvioYosys(CommonSynthYosys, ToolInvioYosys):
    '''Command handler for: eda synth --tool invio_yosys.'''

    def __init__(self, config:dict):
        CommonSynthYosys.__init__(self, config)
        ToolInvioYosys.__init__(self, config=self.config)
        self.args.update({
            'invio-blackbox': [],                # list of modules that invio/verific will blackbox.
        })
        self.args_help.update({
            'invio-blackbox': 'List of modules that invio will blackbox prior to yosys',
        })

    def write_and_run_yosys_f_files(self) -> None:

        # Use helper module for Invio/Verific to save out Verilog-2001 from our
        # Verilog + SystemVerilog + VHDL file lists.
        invio_blackbox_list = self.args.get('invio-blackbox', [])

        # Generate run_invio.py:
        invio_dict = invio_helpers.get_invio_command_dict(
            self, blackbox_list=invio_blackbox_list, sim_elab=False
        )
        # run run_invio.py:
        if not self.args.get('stop-before-compile', False):
            for cmdlist in invio_dict['command_lists']:
                self.exec( self.args['work-dir'], cmdlist, tee_fpath=cmdlist.tee_fpath )
            util.info(f'invio/verific: wrote verilog to {invio_dict.get("full_v_filename", None)}')

        # create {work_dir} / yosys
        work_dir = invio_dict.get('work_dir', '')
        assert work_dir
        fullp = os.path.join(work_dir, "yosys")
        if not os.path.exists(fullp):
            os.mkdir(fullp)

        # create yosys.f so we can run a few commands within yosys.
        yosys_f_path = os.path.join(self.full_work_dir, 'yosys.f')
        self.yosys_v_path = os.path.join(self.yosys_out_dir, invio_dict['v_filename'])

        with open(yosys_f_path, 'w', encoding='utf-8') as f:
            lines = []
            if self.args['liberty-file']:
                lines.append('read_liberty -lib ' + self.args['liberty-file'])
            for path in invio_dict.get('blackbox_files_list', []):
                # We have to read the verilog files from the invio blackbox_files_list:
                lines.append(f'read_verilog {path}')
            for module in self.args.get('yosys-blackbox', []) + self.args.get('synth-blackbox', []):
                # But we may blackbox different cells for yosys synthesis.
                lines.append(f'blackbox {module}')


            lines.append(f'read_verilog {invio_dict["full_v_filename"]}')
            lines += self.get_synth_command_lines()
            f.write('\n'.join(lines))

        synth_command_list = util.ShellCommandList(
            [self.yosys_exe, '--scriptfile', yosys_f_path], tee_fpath='yosys.synth.log'
        )


        invio_command_list = util.ShellCommandList(
            ['python3', invio_dict['full_py_filename']], tee_fpath=invio_dict['full_py_filename']
        )

        # Optinally create and run a sta.f:
        sta_command_lists = self.create_sta_f() # [] or [util.ShellCommandList]

        # We create a run_yosys.sh wrapping these scripts, but we do not run this one.
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_invio.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                invio_command_list
            ],
        )
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_invio_yosys.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                invio_command_list,
                synth_command_list,
            ] + sta_command_lists,
        )

        # Do not run this if args['stop-before-compile'] is True
        if self.args.get('stop-before-compile', False) or \
           self.args.get('stop-after-compile', False):
            return

        # Run the synth commands standalone:
        self.exec( work_dir=work_dir, command_list=synth_command_list,
                   tee_fpath=synth_command_list.tee_fpath )

        for x in sta_command_lists:
            if self.args['sta'] and x:
                self.exec(work_dir=self.full_work_dir, command_list=x,
                          tee_fpath=x.tee_fpath)

        if self.status == 0:
            util.info(f'yosys: wrote verilog to {self.yosys_v_path}')


class CommandElabInvioYosys(CommandSynthInvioYosys):
    '''Run invio + yosys as elab only (does not run the synthesis portion)'''

    def __init__(self, config):
        super().__init__(config)
        self.command_name = 'elab'
        self.args.update({
            'stop-after-compile': True, # In the case of Invio/Yosys we run the Invio step
            'lint': True
        })
