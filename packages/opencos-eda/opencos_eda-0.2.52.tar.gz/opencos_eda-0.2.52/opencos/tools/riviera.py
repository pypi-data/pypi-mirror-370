''' opencos.tools.riviera - Used by opencos.eda for sim/elab commands w/ --tool=riviera.

Contains classes for ToolRiviera, CommandSimRiviera, CommandElabRiviera.
'''

# pylint: disable=too-many-ancestors
# pylint: disable=R0801 # (duplicate code in derived classes, such as if-condition return.)

import os
import shutil
import subprocess

from opencos import util
from opencos.tools.modelsim_ase import ToolModelsimAse, CommandSimModelsimAse
from opencos.utils.str_helpers import sanitize_defines_for_sh

class ToolRiviera(ToolModelsimAse):
    '''ToolRiviera used by opencos.eda for --tool=riviera'''

    _TOOL = 'riviera'
    _EXE = 'vsim'

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION
        path = shutil.which(self._EXE)
        if not path:
            self.error(f"{self._EXE} not in path, need to setup or add to PATH")
            util.debug(f"{path=}")
        else:
            self.sim_exe = path
            self.sim_exe_base_path, _ = os.path.split(path)

        version_ret = subprocess.run(
            [self.sim_exe, '-version'],
            capture_output=True,
            check=False
        )
        stdout = version_ret.stdout.decode('utf-8', errors='replace').rstrip()

        # Expect:
        #  Aldec, Inc. Riviera-PRO version 2025.04.139.9738 built for Linux64 on May 30, 2025
        left, right = stdout.split('version')
        if 'Riviera' not in left:
            self.error(f'{stdout}: does not show Riviera')
        self._VERSION = right.split()[0]
        return self._VERSION


class CommandSimRiviera(CommandSimModelsimAse, ToolRiviera):
    '''CommandSimRiviera is a command handler for: eda sim --tool=riviera'''

    def __init__(self, config: dict):
        CommandSimModelsimAse.__init__(self, config=config)
        ToolRiviera.__init__(self, config=self.config)
        self.shell_command = os.path.join(self.sim_exe_base_path, 'vsim')
        self.starter_edition = True
        self.args.update({
            'tool': self._TOOL, # override
            'gui': False,
        })

    def set_tool_defines(self):
        # Update any defines from config.tools.modelsim_ase:
        self.defines.update(
            self.tool_config.get(
                'defines',
                # defaults, if not set:
                {'OC_TOOL_RIVIERA': 1}
            )
        )

    # Note: many of these we follow the same flow as CommandSimModelsimAse:
    # do_it, prepare_compile, compile, elaborate, simulate

    def get_compile_command_lists(self, **kwargs) -> list:
        # This will also set up a compile.
        vsim_command_list = [
            self.sim_exe,
            '' if self.args['gui'] else '-c',
            '-l', 'sim.log', '-do', 'vsim_vlogonly.do'
        ]
        return [vsim_command_list]

    def get_elaborate_command_lists(self, **kwargs) -> list:
        # This will also set up a compile, for vlog + vsim (0 time)
        vsim_command_list = [
            self.sim_exe,
            '' if self.args['gui'] else '-c',
            '-l', 'sim.log', '-do', 'vsim_lintonly.do',
        ]
        return [vsim_command_list]

    def get_simulate_command_lists(self, **kwargs) -> list:
    # This will also set up a compile, for vlog + vsim (with run -all)
        vsim_command_list = [
            self.sim_exe,
            '' if self.args['gui'] else '-c',
            '-l', 'sim.log', '-do', 'vsim.do',
        ]
        return [vsim_command_list]

    def get_post_simulate_command_lists(self, **kwargs) -> list:
        return []


    def write_vlog_dot_f(self, filename='vlog.f') -> None:
        '''Returns none, creates filename (str) for a vlog.f'''
        vlog_dot_f_lines = []

        # Add compile args from config.tool.riviera
        vlog_dot_f_lines += self.tool_config.get(
            'compile-args',
            '-sv -input_ports net').split()

        # Add waivers from config.tool.riviera, convert to warning:
        for waiver in self.tool_config.get('compile-waivers', []):
            vlog_dot_f_lines += [f'-err {waiver} W1']

        vlog_dot_f_fname = filename
        vlog_dot_f_fpath = os.path.join(self.args['work-dir'], vlog_dot_f_fname)

        for value in self.incdirs:
            vlog_dot_f_lines += [ f"+incdir+{value}" ]

        for k,v in self.defines.items():
            if v is None:
                vlog_dot_f_lines += [ f'+define+{k}' ]
            else:

                # if the value v is a double-quoted string, such as v='"hi"', the
                # entire +define+NAME="hi" needs to wrapped in double quotes with the
                # value v double-quotes escaped: "+define+NAME=\"hi\""
                if isinstance(v, str) and v.startswith('"') and v.endswith('"'):
                    str_v = v.replace('"', '\\"')
                    vlog_dot_f_lines += [ f'"+define+{k}={str_v}"' ]
                else:
                    # Generally we should only support int and str python types passed as
                    # +define+{k}={v}, but also for SystemVerilog plusargs
                    vlog_dot_f_lines += [ f'+define+{k}={sanitize_defines_for_sh(v)}' ]


        vlog_dot_f_lines += self.args['compile-args']
        if self.args['coverage']:
            vlog_dot_f_lines += self.tool_config.get('compile-coverage-args', '').split()

        vlog_dot_f_lines += [
            ] + list(self.files_sv) + list(self.files_v)

        if not self.files_sv and not self.files_v:
            if not self.args['stop-before-compile']:
                self.error(f'{self.target=} {self.files_sv=} and {self.files_v=} are empty,',
                           'cannot create a valid vlog.f')

        with open(vlog_dot_f_fpath, 'w', encoding='utf-8') as f:
            f.writelines(line + "\n" for line in vlog_dot_f_lines)


    def write_vsim_dot_do(self, dot_do_to_write: list) -> None:
        '''Writes files(s) based on dot_do_to_write(list of str)

        list arg values can be empty (all) or have items 'all', 'sim', 'lint', 'vlog'.'''

        vsim_dot_do_fpath = os.path.join(self.args['work-dir'], 'vsim.do')
        vsim_lintonly_dot_do_fpath = os.path.join(self.args['work-dir'], 'vsim_lintonly.do')
        vsim_vlogonly_dot_do_fpath = os.path.join(self.args['work-dir'], 'vsim_vlogonly.do')

        sim_plusargs_str = self._get_sim_plusargs_str()

        voptargs_str = ""
        if self.args['gui'] or self.args['waves'] or self.args['coverage']:
            voptargs_str = self.tool_config.get('simulate-waves-args',
                                                '+accb +accr +access +r+w')
        if self.args['coverage']:
            voptargs_str += self.tool_config.get('coverage-args', '')

        # TODO(drew): support self.args['sim_libary', 'elab-args', sim-args'] (3 lists)
        # to add to vsim_one_liner.

        vsim_one_liner = (
            "vsim"
            f" -sv_seed {self.args['seed']} {sim_plusargs_str}"
            f" {voptargs_str} work.{self.args['top']}"
        )

        vsim_one_liner = vsim_one_liner.replace('\n', ' ') # needs to be a one-liner

        vsim_vlogonly_dot_do_lines = [
            "if {[file exists work]} { vdel -all work; }",
            "vlib work;",
            "if {[catch {vlog -f vlog.f} result]} {",
            "    echo \"Caught $result \";",
            "    if {[batch_mode]} {",
            "        quit -code 20 -force;",
            "    }",
            "}",
            "if {[batch_mode]} {",
            "    quit -code 0 -force;",
            "}",
        ]

        vsim_lintonly_dot_do_lines = [
            "if {[file exists work]} { vdel -all work; }",
            "vlib work;",
            "set qc 30;",
            "if {[catch {vlog -f vlog.f} result]} {",
            "    echo \"Caught $result \";",
            "    if {[batch_mode]} {",
            "        quit -code 20 -force;",
            "    }",
            "}",
            "if {[catch { " + vsim_one_liner + " } result] } {",
            "    echo \"Caught $result\";",
            "    if {[batch_mode]} {",
            "        quit -code 19 -force;",
            "    }",
            "}",
            "if {[batch_mode]} {",
            "    quit -code 0 -force;",
            "}",
        ]

        vsim_dot_do_lines = [
            "if {[file exists work]} { vdel -all work; }",
            "vlib work;",
            "set qc 30;",
            "if {[catch {vlog -f vlog.f} result]} {",
            "    echo \"Caught $result \";",
            "    if {[batch_mode]} {",
            "        quit -code 20 -force;",
            "    }",
            "}",
            "if {[catch { " + vsim_one_liner + " } result] } {",
            "    echo \"Caught $result\";",
            "    if {[batch_mode]} {",
            "        quit -code 19 -force;",
            "    }",
            "}",
        ]

        if self.args['coverage']:
            vsim_dot_do_lines += [
                "run -all;",
                "acdb save",
                "acdb report -db work.acdb -txt -o cov.txt",
                # Note - could try:
                ##"cover report -o cov.report.txt -fullverbose -all_columns",
            ]
        else:
            vsim_dot_do_lines += [
                "run -all;",
            ]


        vsim_dot_do_lines += [
            "if {[batch_mode]} {",
            "    quit -code 0 -force;",
            "}",
        ]

        write_all = len(dot_do_to_write) == 0 or 'all' in dot_do_to_write
        if write_all or 'sim' in dot_do_to_write:
            with open(vsim_dot_do_fpath, 'w', encoding='utf-8') as f:
                f.writelines(line + "\n" for line in vsim_dot_do_lines)

        if write_all or 'lint' in dot_do_to_write:
            with open(vsim_lintonly_dot_do_fpath, 'w', encoding='utf-8') as f:
                f.writelines(line + "\n" for line in vsim_lintonly_dot_do_lines)

        if write_all or 'vlog' in dot_do_to_write:
            with open(vsim_vlogonly_dot_do_fpath, 'w', encoding='utf-8') as f:
                f.writelines(line + "\n" for line in vsim_vlogonly_dot_do_lines)



    def _get_vsim_suppress_list_str(self) -> str:
        vsim_suppress_list = []
        # Add waivers from config.tool.modelsim_ase:
        for waiver in self.tool_config.get(
                'simulate-waivers', [
                    #defaults: none
                ]):
            vsim_suppress_list += ['-filter', str(waiver)]

        return ' '.join(vsim_suppress_list)


class CommandElabRiviera(CommandSimRiviera):
    '''CommandElabRiviera is a command handler for: eda elab --tool=riviera'''

    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True
