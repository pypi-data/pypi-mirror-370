''' opencos.tools.iverilog - Used by opencos.eda for sim and elab commands with --tool=iverilog.

Contains classes for ToolIverilog CommandSimIverilog, CommandElabIverilog.
'''

import shutil
import subprocess

from opencos import util
from opencos.eda_base import Tool
from opencos.commands import CommandSim
from opencos.utils.str_helpers import sanitize_defines_for_sh


class ToolIverilog(Tool):
    '''ToolIverilog used by opencos.eda for --tool=iverilog'''

    _TOOL = 'iverilog'
    _EXE = 'iverilog'
    _URL = 'https://github.com/steveicarus/iverilog'

    def __init__(self, config: dict):
        self.iverilog_exe = ''
        super().__init__(config=config) # calls self.get_versions()

    def get_versions(self) -> str:
        self.iverilog_exe = ''
        if self._VERSION:
            return self._VERSION

        iverilog_path = shutil.which(self._EXE)
        if iverilog_path is None:
            self.error(f'"{self._EXE}" not in path, need to get it ({self._URL})')
        else:
            self.iverilog_exe = iverilog_path

        iverilog_version_ret = subprocess.run(
            [self.iverilog_exe, '-v'], capture_output=True, check=False
        )
        lines = iverilog_version_ret.stdout.decode("utf-8", errors="replace").split('\n')
        words = lines[0].split() # 'Icarus Verilog version 13.0 (devel) (s20221226-568-g62727e8b2)'
        version = words[3]
        util.debug(f'{iverilog_path=} {lines[0]=}')
        self._VERSION = version
        return self._VERSION

    def set_tool_defines(self):
        # TODO(drew): come back to this, Tool doesn't have self.defines. Command does.
        self.defines.update({
            'SIMULATION': 1,
            'IVERILOG': 1,
            'OC_ASSERT_PROPERTY_NOT_SUPPORTED': 1,
        })


class CommandSimIverilog(CommandSim, ToolIverilog):
    '''CommandSimIverilog is a command handler for: eda sim --tool=iverilog'''

    def __init__(self, config:dict):
        CommandSim.__init__(self, config)
        ToolIverilog.__init__(self, config=self.config)
        self.args['gui'] = False
        self.args['tcl-file'] = None

        self.args_help.update({
            'waves':    'Include waveforms, if possible for iverilog by applying' \
            + ' exe runtime arg +trace. User will need SV code to interpret the plusarg' \
            + ' and apply $dumpfile("dump.vcd") or another non-vcd file extension.',
        })

        self.iverilog_command_lists = []
        self.iverilog_exec_command_lists = []


    def set_tool_defines(self):
        ToolIverilog.set_tool_defines(self)

    # We do not override CommandSim.do_it()
    def prepare_compile(self):
        self.set_tool_defines()

        self.iverilog_command_lists = self.get_compile_command_lists()
        self.iverilog_exec_command_lists  = self.get_simulate_command_lists()

        paths = ['logs']
        util.safe_mkdirs(base=self.args['work-dir'], new_dirs=paths)

        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='compile_only.sh',
            command_lists=self.iverilog_command_lists,
            line_breaks=True
        )

        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='simulate_only.sh',
            command_lists=self.iverilog_exec_command_lists
        )

        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='all.sh',
            command_lists = [
                ['./pre_compile_dep_shell_commands.sh'],
                ['./compile_only.sh'],
                ['./simulate_only.sh'],
            ]
        )

        self.write_eda_config_and_args()

    def compile(self):
        if self.args['stop-before-compile']:
            return
        self.run_commands_check_logs(self.iverilog_command_lists, check_logs=False)

    def elaborate(self):
        pass

    def simulate(self):
        if self.args['stop-before-compile'] or self.args['stop-after-compile'] or \
           self.args['stop-after-elaborate']:
            # don't run this if we're stopping before/after compile/elab
            return

        # Note that this is not returning a pass/fail bash return code,
        # so we will likely have to log-scrape to deterimine pass/fail.
        self.run_commands_check_logs(self.iverilog_exec_command_lists)

    def get_compile_command_lists(self, **kwargs) -> list:

        command_list = [
            self.iverilog_exe,
        ]
        command_list += self.tool_config.get(
            'compile-args',
            '-gsupported-assertions -grelative-include').split()
        command_list += [
            '-s', self.args['top'],
            '-o', 'sim.exe',
        ]

        if util.args['verbose']:
            command_list += ['-v']

        # incdirs
        for value in self.incdirs:
            command_list += [ '-I', value ]

        for k,v in self.defines.items():
            if v is None:
                command_list += [ '-D', k ]
            else:
                # Generally we should only support int and str python types passed as
                # +define+{k}={v}, but also for SystemVerilog plusargs
                command_list += [ '-D', f'{k}={sanitize_defines_for_sh(v)}' ]

        if not self.files_sv and not self.files_v:
            if not self.args['stop-before-compile']:
                self.error(f'{self.target=} {self.files_sv=} and {self.files_v=} are empty,',
                           'cannot call iverilog')

        command_list += list(self.files_sv) + list(self.files_v)

        return [ util.ShellCommandList(command_list) ]

    def get_elaborate_command_lists(self, **kwargs) -> list:
        return []

    def get_simulate_command_lists(self, **kwargs) -> list:

        # Need to return a list-of-lists, even though we only have 1 command
        cmd_list = ['./sim.exe']
        cmd_list += self.tool_config.get('simulate-args', '').split()
        if self.args['waves']:
            cmd_list += self.tool_config.get('simulate-waves-args', '').split()
        return [ util.ShellCommandList(cmd_list, tee_fpath='sim.log') ]

    def get_post_simulate_command_lists(self, **kwargs) -> list:
        return []


class CommandElabIverilog(CommandSimIverilog):
    '''CommandElabIverilog is a command handler for: eda elab --tool=iverilog'''

    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True
