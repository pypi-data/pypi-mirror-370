''' opencos.tools.vivado - Used by opencos.eda commands with --tool=vivado.

Contains classes for ToolVivado, and command handlers for sim, elab, synth, build,
upload, flist, open, proj.
'''

# pylint: disable=R0801 # (setting similar, but not identical, self.defines key/value pairs)

import os
import re
import shlex
import shutil
import sys

from datetime import datetime
from pathlib import Path

from opencos import util, eda_base
from opencos.eda_base import Tool

from opencos.commands import CommandSim, CommandSynth, CommandProj, CommandBuild, \
    CommandFList, CommandUpload, CommandOpen

class ToolVivado(Tool):
    '''ToolVivado used by opencos.eda for --tool=vivado'''

    _TOOL = 'vivado'
    _EXE = 'vivado'

    vivado_year = None
    vivado_release = None
    vivado_base_path = ''
    vivado_exe = ''

    def __init__(self, config: dict):
        super().__init__(config=config) # calls self.get_versions()
        self.args.update({
            'part': 'xcu200-fsgd2104-2-e',
            'add-glbl-v': False,
        })
        self.args_help.update({
            'part': 'Device used for commands: synth, build.',
            'add-glbl-v': '(for simulation) add glbl.v to filelist',
        })


    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION

        path = shutil.which(self._EXE)
        if not path:
            self.error("Vivado not in path, need to install or add to $PATH",
                       f"(looked for '{self._EXE}')")
        else:
            self.vivado_exe = path
            self.vivado_base_path, _ = os.path.split(path)

        xilinx_vivado = os.environ.get('XILINX_VIVADO')
        if not xilinx_vivado or \
           os.path.abspath(os.path.join(xilinx_vivado, 'bin')) != \
               os.path.abspath(os.path.dirname(self.vivado_exe)):
            util.info("environment for XILINX_VIVADO is not set or doesn't match the vivado path:",
                      f"XILINX_VIVADO={xilinx_vivado} EXE PATH={self.vivado_exe}")

        # Get version based on install path name. Calling vivado -verison is too slow.
        util.debug(f"vivado path = {self.vivado_exe}")
        m = re.search(r'(\d\d\d\d)\.(\d)', self.vivado_exe)
        if m:
            version = m.group(1) + '.' + m.group(2)
            self._VERSION = version
        else:
            self.error("Vivado path doesn't specificy version, expecting (dddd.d)")

        if version:
            numbers_list = version.split('.')
            self.vivado_year = int(numbers_list[0])
            self.vivado_release = int(numbers_list[1])
            self.vivado_version = float(numbers_list[0] + '.' + numbers_list[1])
        else:
            self.error(f"Vivado version not found, vivado path = {self.vivado_exe}")
        return self._VERSION


    def set_tool_defines(self) -> None:
        self.defines['OC_TOOL_VIVADO'] = None
        def_year_release = f'OC_TOOL_VIVADO_{self.vivado_year:04d}_{self.vivado_release:d}'
        self.defines[def_year_release] = None

        # Code can be conditional on Vivado versions and often keys of "X or older" ...
        versions = ['2021.1', '2021.2', '2022.1', '2022.2', '2023.1', '2023.2',
                    '2024.1', '2024.2']
        for ver in versions:
            float_ver = float(ver)
            str_ver = str(float_ver).replace('.', '_')
            if self.vivado_version <= float_ver:
                self.defines[f'OC_TOOL_VIVADO_{str_ver}_OR_OLDER'] = None
            if self.vivado_version >= float_ver:
                self.defines[f'OC_TOOL_VIVADO_{str_ver}_OR_NEWER'] = None

        # Older Vivado's don't correctly compare types in synthesis (xsim seems OK)
        if self.vivado_version < 2023.2:
            self.defines['OC_TOOL_BROKEN_TYPE_COMPARISON'] = None

        util.debug(f"Setup tool defines: {self.defines}")


    def get_vivado_tcl_verbose_arg(self) -> str:
        '''Returns a common Vivado tcl arg str (-verbose, -quiet, or both/none)'''
        v = "" # v = verbose tcl arg we'll add to many tcl commands.
        if util.args.get('verbose', ''):
            v += " -verbose"
        elif util.args.get('quiet', ''):
            v += " -quiet"
        return v


class CommandSimVivado(CommandSim, ToolVivado):
    '''CommandSimVivado is a command handler for: eda sim --tool=vivado, uses xvlog, xelab, xsim'''

    def __init__(self, config: dict):
        CommandSim.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this tool
        self.args.update({
            'gui':        False,
            'tcl-file':   'sim.tcl',
            'fpga':       '',
            'add-glbl-v': False,
            'all-sv':     False,
        })
        self.args_help.update({
            'gui':        'Run Vivado XSim in GUI mode',
            'tcl-file':   'name of TCL file to be created for XSim',
            'fpga':       'FPGA device name, can be used for various Xilinx IP or XCIs',
            'add-glbl-v': 'Use the glbl.v in xvlog for this version of Vivado',
        })

        self.sim_libraries = self.tool_config.get('sim-libraries', [])
        self.xvlog_commands = []
        self.xelab_commands = []
        self.xsim_commands = []


    def set_tool_defines(self):
        ToolVivado.set_tool_defines(self)

    # We do not override CommandSim.do_it(), CommandSim.check_logs_for_errors(...)

    def prepare_compile(self):
        self.set_tool_defines()
        self.xvlog_commands = self.get_compile_command_lists()
        self.xelab_commands = self.get_elaborate_command_lists()
        self.xsim_commands = self.get_simulate_command_lists()

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='compile.sh',
                                      command_lists=self.xvlog_commands)
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='elaborate.sh',
                                      command_lists=self.xelab_commands)
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='simulate.sh',
                                      command_lists=self.xsim_commands)
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='all.sh',
                                      command_lists = [
                                          ['./pre_compile_dep_shell_commands.sh'],
                                          ['./compile.sh'],
                                          ['./elaborate.sh'],
                                          ['./simulate.sh'],
                                      ])

        self.write_eda_config_and_args()

    def compile(self):
        if self.args['stop-before-compile']:
            return
        self.run_commands_check_logs(
            self.xvlog_commands, check_logs=True, log_filename='xvlog.log'
        )

    def elaborate(self):
        if self.args['stop-before-compile'] or self.args['stop-after-compile']:
            return
        # In this flow, we need to run compile + elaborate separately (unlike ModelsimASE)
        self.run_commands_check_logs(
            self.xelab_commands, check_logs=True, log_filename='xelab.log',
            must_strings=['Built simulation snapshot snapshot']
        )

    def simulate(self):
        if self.args['stop-before-compile'] or self.args['stop-after-compile'] or \
           self.args['stop-after-elaborate']:
            return
        self.run_commands_check_logs(
            self.xsim_commands, check_logs=True, log_filename='xsim.log'
        )

    def get_compile_command_lists(self, **kwargs) -> list:
        self.set_tool_defines()
        ret = [] # list of (list of ['xvlog', arg0, arg1, ..])

        if self.args['add-glbl-v']:
            self._add_glbl_v()

        # compile verilog
        if self.files_v:
            ret.append(
                self.get_xvlog_commands(files_list=self.files_v, typ='v')
            )

        # compile systemverilog
        if self.files_sv:
            ret.append(
                self.get_xvlog_commands(files_list=self.files_sv, typ='sv')
            )

        return ret # list of lists

    def get_elaborate_command_lists(self, **kwargs) -> list:
        # elab into snapshot
        command_list = [
            os.path.join(self.vivado_base_path, 'xelab'),
            self.args['top']
        ]
        if sys.platform == "win32":
            command_list[0] += ".bat"
        command_list += self.tool_config.get('elab-args',
                                             '-s snapshot -timescale 1ns/1ps --stats').split()
        if self.tool_config.get('elab-waves-args', ''):
            command_list += self.tool_config.get('elab-waves-args', '').split()
        elif self.args['gui'] and self.args['waves']:
            command_list += ['-debug', 'all']
        elif self.args['gui']:
            command_list += ['-debug', 'typical']
        elif self.args['waves']:
            command_list += ['-debug', 'wave']
        if util.args['verbose']:
            command_list += ['-v', '2']
        if self.args['sim-library'] or self.args['add-glbl-v']:
            self.sim_libraries += self.args['sim-library'] # Add any command line libraries
            for x in self.sim_libraries:
                command_list += ['-L', x]
            command_list += ['glbl']
        command_list += self.args['elab-args']
        return [command_list]

    def get_simulate_command_lists(self, **kwargs) -> list:
        # create TCL
        tcl_name = os.path.abspath(os.path.join(self.args['work-dir'], self.args['tcl-file']))

        if self.args['waves']:
            util.artifacts.add_extension(
                search_paths=self.args['work-dir'], file_extension='wdb',
                typ='waveform', description='Vivado XSim Waveform WDB (Wave DataBase) file'
            )


        with open( tcl_name, 'w', encoding='utf-8' ) as fo:
            if self.args['waves']:
                if self.args['waves-start']:
                    print(f"run {self.args['waves-start']} ns", file=fo)
                print("log_wave -recursive *", file=fo)
            print("run -all", file=fo)
            if not self.args['gui']:
                print("exit", file=fo)

        sv_seed = str(self.args['seed'])

        assert isinstance(self.args["sim-plusargs"], list), \
            f'{self.target=} {type(self.args["sim-plusargs"])=} but must be list'

        # xsim uses: --testplusarg foo=bar
        xsim_plusargs_list = []
        for x in self.args['sim-plusargs']:
            xsim_plusargs_list.append('--testplusarg')
            if x[0] == '+':
                x = x[1:]
            xsim_plusargs_list.append(f'\"{x}\"')

        # execute snapshot
        command_list = [ os.path.join(self.vivado_base_path, 'xsim') ]
        if sys.platform == "win32":
            command_list[0] += ".bat"
        command_list += self.tool_config.get('simulate-args', 'snapshot --stats').split()
        if self.args['gui']:
            command_list += ['-gui']
        command_list += [
            '--tclbatch', tcl_name.replace('\\','\\\\'),  # needed for windows paths
            "--sv_seed", sv_seed
        ]
        command_list += xsim_plusargs_list
        command_list += self.args['sim-args']
        return [command_list] # single command

    def get_post_simulate_command_lists(self, **kwargs) -> list:
        return []

    def get_xvlog_commands(self, files_list: list, typ: str = 'sv') -> list:
        '''Returns list. Vivado still treats .v files like Verilog-2001, so we split

        xvlog into .v and .sv sections'''
        command_list = []

        if files_list:
            command_list = [ os.path.join(self.vivado_base_path, 'xvlog') ]
            if sys.platform == "win32":
                command_list[0] += ".bat"
            if typ == 'sv':
                command_list.append('-sv')
            command_list += self.tool_config.get('compile-args', '').split()
            if util.args['verbose']:
                command_list += ['-v', '2']
            for value in self.incdirs:
                command_list.append('-i')
                command_list.append(value)
            for key, value in self.defines.items():
                command_list.append('-d')
                if value is None:
                    command_list.append(key)
                elif sys.platform == "win32":
                    command_list.append(f"\"{key}={value}\"") # only thing that seems to work
                elif "\'" in value:
                    command_list.append(f"\"{key}={value}\"")
                else:
                    command_list.append(f"{key}={value}")
            command_list += self.args['compile-args']
            command_list += files_list
        return command_list


    def _add_glbl_v(self):
        '''Adds glbl.v from Vivado's install path to self.files_v'''
        glbl_v = self.vivado_base_path.replace('bin', 'data/verilog/src/glbl.v')
        if any(x.endswith('glbl.v') for x in self.files_v):
            util.warning(f'--add-glbl-v: Not adding {glbl_v=} b/c glbl.v already in',
                         f'{self.files_v=}')
        elif not os.path.exists(glbl_v):
            self.error(f"Could not find file {glbl_v=}")
        else:
            self.files_v.insert(0, glbl_v)


    def artifacts_add(self, name: str, typ: str, description: str) -> None:
        '''Override from Command.artifacts_add, so we can catch known file

        names to make their typ/description better, such as CommandSim using
        sim.log or compile.log
        '''
        _, leafname = os.path.split(name)
        if leafname == 'xsim.log':
            description = 'Vivado XSim simulation step (3/3) log from stdout/stderr'
        elif leafname == 'xelab.log':
            description = 'Vivado XSim elaboration step (2/3) log from stdout/stderr'
        elif leafname == 'xvlog.log':
            description = 'Vivado XSim compile step (1/3) log from stdout/stderr'

        super().artifacts_add(name=name, typ=typ, description=description)


class CommandElabVivado(CommandSimVivado):
    '''CommandElabVivado is a command handler for: eda elab --tool=vivado, uses xvlog, xelab'''
    def __init__(self, config: dict):
        CommandSimVivado.__init__(self, config)
        # add args specific to this tool
        self.args['stop-after-elaborate'] = True


class CommandSynthVivado(CommandSynth, ToolVivado):
    '''CommandSynthVivado is a command handler for: eda synth --tool=vivado'''
    def __init__(self, config: dict):
        CommandSynth.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this tool
        self.args['gui'] = False
        self.args['tcl-file'] = "synth.tcl"
        self.args['xdc'] = ""
        self.args['fpga'] = ""
        self.args['all-sv'] = False

    def do_it(self) -> None:
        CommandSynth.do_it(self)

        if self.is_export_enabled():
            return

        # create TCL
        tcl_file = os.path.abspath(
            os.path.join(self.args['work-dir'], self.args['tcl-file'])
        )

        self.write_tcl_file(tcl_file=tcl_file)

        # execute Vivado
        command_list = [
            self.vivado_exe, '-mode', 'batch', '-source', tcl_file,
            '-log', f"{self.args['top']}.synth.log"
        ]
        if not util.args['verbose']:
            command_list.append('-notrace')
        self.exec(self.args['work-dir'], command_list)


    def write_tcl_file( # pylint: disable=too-many-locals,too-many-branches
            self, tcl_file: str
    ) -> None:
        '''Writes synthesis capable Vivado tcl file to filepath 'tcl_file'.'''

        # TODO(drew): This method needs to be broken up to avoid the pylint
        # waivers.

        v = self.get_vivado_tcl_verbose_arg()

        defines = ""
        for key, value in self.defines.items():
            defines += (f"-verilog_define {key}" + (" " if value is None else f"={value} "))
        incdirs = ' '.join([f'-include_dirs {x}' for x in self.incdirs])
        flatten = ""
        if self.args['flatten-all']:
            flatten = "-flatten_hierarchy full"
        elif self.args['flatten-none']:
            flatten = "-flatten_hierarchy none"

        tcl_lines = []
        for f in self.files_v:
            tcl_lines.append(f"read_verilog {f}")
        for f in self.files_sv:
            tcl_lines.append(f"read_verilog -sv {f}")
        for f in self.files_vhd:
            tcl_lines.append(f"add_file {f}")

        part = self.args['part']
        top = self.args['top']

        default_xdc = False
        if self.args['xdc'] != "":
            xdc_file = os.path.abspath(self.args['xdc'])
        elif self.files_sdc:
            # Use files from DEPS target or command line.
            xdc_file = ''
        else:
            default_xdc = True
            xdc_file = os.path.abspath(os.path.join(self.args['work-dir'],
                                                    "default_constraints.xdc"))


        tcl_lines += [
            f"create_fileset -constrset constraints_1 {v}",
        ]
        for _file in self.files_sdc:
            # NOTE - sdc files cannot (yet) be attached to other modules.
            tcl_lines += [
                f"add_files -fileset constraints_1 {_file} {v}",
            ]
        if xdc_file:
            tcl_lines += [
                f"add_files -fileset constraints_1 {xdc_file} {v}",
            ]
        tcl_lines += [
            "# FIRST PASS -- auto_detect_xpm",
            "synth_design -rtl -rtl_skip_ip -rtl_skip_constraints -no_timing_driven -no_iobuf " \
            + f"-top {top} {incdirs} {defines} {v}",
            f"auto_detect_xpm {v} ",
            f"synth_design -no_iobuf -part {part} {flatten} -constrset constraints_1 " \
            + f"-top {top} {incdirs} {defines} {v}",
            f"write_verilog -force {top}.vg {v}",
            f"report_utilization -file {top}.flat.util.rpt {v}",
            f"report_utilization -file {top}.hier.util.rpt {v} -hierarchical " \
            + "-hierarchical_depth 20",
            f"report_timing -file {top}.timing.rpt {v}",
            f"report_timing_summary -file {top}.summary.timing.rpt {v}",
            f"report_timing -from [all_inputs] -file {top}.input.timing.rpt {v}",
            f"report_timing -to [all_outputs] -file {top}.output.timing.rpt {v}",
            "report_timing -from [all_inputs] -to [all_outputs] " \
            + f"-file {top}.through.timing.rpt {v}",
            "set si [get_property -quiet SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup " \
            + "-from [all_inputs]]]",
            "set so [get_property -quiet SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup " \
            + "-to [all_outputs]]]",
            f"set_false_path -from [all_inputs] {v}",
            f"set_false_path -to [all_outputs] {v}",
            "set sf [get_property -quiet SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]",
            "if { ! [string is double -strict $sf] } { set sf 9999 }",
            "if { ! [string is double -strict $si] } { set si 9999 }",
            "if { ! [string is double -strict $so] } { set so 9999 }",
            "puts \"\"",
            "puts \"*** ****************** ***\"",
            "puts \"***                    ***\"",
            "puts \"*** SYNTHESIS COMPLETE ***\"",
            "puts \"***                    ***\"",
            "puts \"*** ****************** ***\"",
            "puts \"\"",
            "puts \"** AREA **\"",
            "report_utilization -hierarchical",
            "puts \"** TIMING **\"",
            "puts \"\"",
        ]

        if default_xdc:
            tcl_lines += [
                f"puts \"(Used default XDC: {xdc_file})\"",
                f"puts \"DEF CLOCK NS  : [format %.3f {self.args['clock-ns']}]\"",
                f"puts \"DEF IDELAY NS : [format %.3f {self.args['idelay-ns']}]\"",
                f"puts \"DEF ODELAY NS : [format %.3f {self.args['odelay-ns']}]\"",
            ]
        else:
            tcl_lines += [
                f"puts \"(Used provided XDC: {xdc_file})\"",
            ]
        tcl_lines += [
            "puts \"\"",
            "puts \"F2F SLACK     : [format %.3f $sf]\"",
            "puts \"INPUT SLACK   : [format %.3f $si]\"",
            "puts \"OUTPUT SLACK  : [format %.3f $so]\"",
            "puts \"\"",
        ]

        if default_xdc:
            self.write_default_xdc(xdc_file=xdc_file)

        with open( tcl_file, 'w', encoding='utf-8' ) as ftcl:
            ftcl.write('\n'.join(tcl_lines))


    def write_default_xdc(self, xdc_file: str) -> None:
        '''Writes a default XDC file to filepath 'xdc_file'.'''

        xdc_lines = []
        util.info("Creating default constraints: clock:",
                  f"{self.args['clock-name']}, {self.args['clock-ns']} (ns),",
                  f"idelay:{self.args['idelay-ns']}, odelay:{self.args['odelay-ns']}")

        clock_name = self.args['clock-name']
        period = self.args['clock-ns']
        name_not_equal_clocks_str = f'NAME !~ "{clock_name}"'

        xdc_lines += [
            f"create_clock -add -name {clock_name} -period {period} [get_ports " \
            + "{" + clock_name + "}]",
        ]
        xdc_lines += [
            f"set_input_delay -max {self.args['idelay-ns']} -clock {clock_name} " +
            "[get_ports * -filter {DIRECTION == IN && " \
            + name_not_equal_clocks_str + "}]",
        ]
        xdc_lines += [
            f"set_output_delay -max {self.args['odelay-ns']} -clock {clock_name} " +
            "[get_ports * -filter {DIRECTION == OUT}]"
        ]
        with open( xdc_file, 'w', encoding='utf-8' ) as fxdc:
            fxdc.write('\n'.join(xdc_lines))



class CommandProjVivado(CommandProj, ToolVivado):
    '''CommandProjVivado is a command handler for: eda proj --tool=vivado'''

    def __init__(self, config: dict):
        CommandProj.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this tool
        self.args['gui'] = True
        self.args['oc-vivado-tcl'] = True
        self.args['tcl-file'] = "proj.tcl"
        self.args['xdc'] = ""
        self.args['board'] = ""
        self.args['all-sv'] = False

    def do_it(self):
        # add defines for this job
        self.set_tool_defines()
        self.write_eda_config_and_args()

        oc_root = util.get_oc_root()

        # create TCL
        tcl_file = os.path.abspath(os.path.join(self.args['work-dir'], self.args['tcl-file']))
        v = self.get_vivado_tcl_verbose_arg()

        incdirs = " ".join(self.incdirs)
        defines = ""
        for key, value in self.defines.items():
            defines += (f"{key} " if value is None else f"{key}={value} ")

        tcl_lines = [
            f"create_project {self.args['top']}_proj {self.args['work-dir']} {v}"
        ]

        if self.args['oc-vivado-tcl'] and oc_root:
            tcl_lines += [
                f"source \"{oc_root}/boards/vendors/xilinx/oc_vivado.tcl\" -notrace"
            ]

        if self.args['board']:
            tcl_lines += [
                f"set_property board_part {self.args['board']} [current_project]"
            ]

        tcl_lines += [
            f"set_property include_dirs {{{incdirs}}} [get_filesets sources_1]",
            f"set_property include_dirs {{{incdirs}}} [get_filesets sim_1]",
            f"set_property verilog_define {{{defines}}} [get_filesets sources_1]",
            f"set_property verilog_define {{SIMULATION {defines}}} [get_filesets sim_1]",
            "set_property -name {STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS} -value " \
            + "{{-verilog_define SYNTHESIS}} -objects [get_runs synth_1]",
            "set_property {xsim.simulate.runtime} {10ms} [get_filesets sim_1]",
            "set_property {xsim.simulate.log_all_signals} {true} [get_filesets sim_1]",
        ]

        for f in self.files_v + self.files_sv + self.files_vhd:
            # TODO(drew): automatically adding some files to sim_1 vs sources_1 should be
            # configurable in eda_config_defaults.yml or via some custom eda arg.
            if any(x in f for x in ['/sim/', '/tests/']):
                fileset = "sim_1"
            else:
                fileset = "sources_1"
            tcl_lines += [
                f"add_files -norecurse {f} -fileset [get_filesets {fileset}]"
            ]

        tcl_lines += [
            f"set_property top {self.args['top']} [get_filesets sim_1]"
        ]
        with open( tcl_file, 'w', encoding='utf-8' ) as fo:
            fo.write('\n'.join(tcl_lines))

        # execute Vivado
        command_list = [
            self.vivado_exe, '-mode', 'gui', '-source', tcl_file,
            '-log', f"{self.args['top']}.proj.log"
        ]
        if not util.args['verbose']:
            command_list.append('-notrace')
        self.exec(self.args['work-dir'], command_list)
        util.info(f"Project run done, results are in: {self.args['work-dir']}")


class CommandBuildVivado(CommandBuild, ToolVivado):
    '''CommandBuildVivado is a command handler for: eda build --tool=vivado'''

    def __init__(self, config: dict):
        CommandBuild.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this tool
        self.args['gui'] = False
        self.args['fpga'] = ""
        self.args['proj'] = False
        self.args['resynth'] = False
        self.args['reset'] = False
        self.args['all-sv'] = False

    def do_it(self):
        # add defines for this job
        self.set_tool_defines()
        self.write_eda_config_and_args()

        # create FLIST
        flist_file = os.path.join(self.args['work-dir'],'build.flist')
        util.debug(f"CommandBuildVivado: {self.args['top-path']=}")

        eda_path = eda_base.get_eda_exec('flist')
        command_list = [
            eda_path, 'flist',
            '--tool=' + self.args['tool'],
            self.args['top-path'],
            '--force',
            '--out=' + flist_file,
            #'--no-emit-incdir',
            #'--no-single-quote-define', # Needed to run in Command.exec( ... shell=False)
            '--no-quote-define',
            #'--bracket-quote-define',
            '--quote-define-value',
            '--escape-define-value',
            '--no-equal-define',
            '--bracket-quote-path',
            # on --prefix- items, use shlex.quote(str) so spaces work with subprocess shell=False:
            '--prefix-incdir=' + shlex.quote("oc_set_project_incdir "),
            '--prefix-define=' + shlex.quote("oc_set_project_define "),
            '--prefix-sv=' + shlex.quote("add_files -norecurse "),
            '--prefix-v=' + shlex.quote("add_files -norecurse "),
            '--prefix-vhd=' + shlex.quote("add_files -norecurse "),
        ]
        for key,value in self.defines.items():
            if value is None:
                command_list += [ f"+define+{key}" ]
            else:
                command_list += [ shlex.quote(f"+define+{key}={value}") ]
        cwd = util.getcwd()
        util.debug(f"CommandBuildVivado: {cwd=}")


        # Write out a .sh command, but only for debug, it is not run.
        command_list = util.ShellCommandList(command_list, tee_fpath='run_eda_flist.log')
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='run_eda_flist.sh',
                                      command_lists=[command_list], line_breaks=True)

        self.exec(cwd, command_list, tee_fpath=command_list.tee_fpath)

        if self.args['job-name'] == "":
            self.args['job-name'] = self.args['design']
        project_dir = 'project.'+self.args['job-name']

        # launch Vivado
        command_list = [self.vivado_exe]
        command_list += [
            '-mode',
            'gui' if self.args['gui'] else 'batch',
            '-log', os.path.join(self.args['work-dir'], self.args['top'] + '.build.log')
        ]
        if not util.args['verbose']:
            command_list.append('-notrace')
        command_list += [
            '-source', self.args['build-script'],
            '-tclargs', project_dir,
            # these must come last, all after -tclargs get passed to build-script
            flist_file,
        ]
        if self.args['proj']:
            command_list += ['--proj']
        if self.args['resynth']:
            command_list += ['--resynth']
        if self.args['reset']:
            command_list += ['--reset']

        # Write out a .sh command, but only for debug, it is not run.
        command_list = util.ShellCommandList(command_list, tee_fpath=None)
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='run_vivado.sh',
                                      command_lists=[command_list], line_breaks=True)

        self.exec(cwd, command_list, tee_fpath=command_list.tee_fpath)
        util.info(f"Build done, results are in: {self.args['work-dir']}")


class CommandFListVivado(CommandFList, ToolVivado):
    '''CommandFlistVivado is a command handler for: eda flist --tool=vivado'''

    def __init__(self, config: dict):
        CommandFList.__init__(self, config=config)
        ToolVivado.__init__(self, config=self.config)
        self.args['all-sv'] = False


class CommandUploadVivado(CommandUpload, ToolVivado):
    '''CommandUploadVivado is a command handler for: eda upload --tool=vivado'''

    def __init__(self, config: dict):
        CommandUpload.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this tool
        self.args.update({
            'gui': False,
            'bitfile': "",
            'list-usbs': False,
            'list-devices': False,
            'list-bitfiles': False,
            'usb': -1,
            'device': -1,
            'host': "localhost",
            'port': 3121,
            'all-sv': False,
            'tcl-file': "eda_upload.tcl",
            'log-file': "eda_upload.log",
            'test-mode': False,
        })
        # TODO(drew): Add self.args_help.update({...})

    # TODO(drew): This method needs to be refactored (with tests somehow) to clean
    # up pylint waivers
    def do_it(self): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        # add defines for this job
        self.set_tool_defines()
        self.write_eda_config_and_args()

        bitfile = None
        targets = []
        if self.args['bitfile']:
            if os.path.isfile(self.args['bitfile']):
                bitfile = self.args['bitfile']
            else:
                # Not a file, treat as search pattern
                targets = [self.args['bitfile']]

        # TODO(drew): It might be nice to use positional args (supported by
        # eda_base.Command) here, and in multi.py, so we don't accidentally
        # grab errant --arg style strings as potential filenames or target patterns
        for f in self.unparsed_args:
            # self.unparsed_args are leftovers from Command.process_tokens(..)
            if os.path.isfile(f):
                if bitfile is None:
                    bitfile = f
                else:
                    util.error("Too many bitfiles provided")
                    if not self.args['test-mode']:
                        sys.exit(0)
            else:
                # Not a file, treat as search pattern
                targets.append(f)

        # Auto-discover bitfile logic (for when we have no bitfile, and we
        # weren't called just to listdevice/listusb)
        if self.args['list-bitfiles'] or \
           (not bitfile and not self.args['list-devices'] and not self.args['list-usbs']):
            bitfiles: list[Path] = []

            util.debug(f"Looking for bitfiles in {os.path.abspath('.')=}")
            for root, _, files in os.walk("."):
                for f in files:
                    if f.endswith(".bit"):
                        fullpath = os.path.abspath(Path(root) / f)
                        if fullpath not in bitfiles:
                            bitfiles.append(fullpath)

            matched: list[Path] = []
            for cand in bitfiles:
                util.debug(f"Looking for {cand=} in {targets=}")
                passing = all(re.search(t, str(cand)) for t in targets)
                if passing:
                    matched.append(cand)
                    mod_time_string = datetime.fromtimestamp(
                        os.path.getmtime(cand)).strftime('%Y-%m-%d %H:%M:%S')
                    util.info(f"Found matching bitfile: {mod_time_string} : {cand}")

            if len(matched) > 1:
                if self.args['list-bitfiles']:
                    util.info("Too many matches to continue without adding search terms.  Done.")
                    if not self.args['test-mode']:
                        sys.exit(0)
                else:
                    util.error("Too many matches, please add search terms...")

            if not matched and bitfile is None:
                if self.args['list-bitfiles']:
                    util.info("No matching bitfiles found, done.")
                    if not self.args['test-mode']:
                        sys.exit(0)
                else:
                    util.error("Failed to find a matching bitfile")

            if matched and bitfile is None:
                bitfile = matched[0]

        # ── Generate TCL script ───────────────────────────────────────────────────
        script_file = Path(self.args['tcl-file'])
        log_file    = Path(self.args['log-file'])

        try:
            with script_file.open("w", encoding="utf-8") as fout:
                w = fout.write   # local alias (brevity)

                w('open_hw_manager\n')
                w(f'connect_hw_server -url {self.args["host"]}:{self.args["port"]}\n')
                w('refresh_hw_server -force_poll\n')

                w('set hw_targets [get_hw_targets -quiet */xilinx_tcf/Xilinx/*]\n')
                w('set num_targets [llength $hw_targets]\n')
                if self.args['list-usbs']:
                    w('puts "\\[INFO\\] OC_LOAD_BITFILE TCL $num_targets USB targets found"\n')
                    w('for {set u 0} {$u < $num_targets} {incr u} {\n')
                    w('  puts "\\[INFO\\] OC_LOAD_BITFILE TCL: USB $u : [lindex $hw_targets $u]"\n')
                    w('}\n')
                    w('if { $num_targets > 1} {\n')
                    w('  set maxusb [expr $num_targets - 1]\n')
                    w('  puts "\\[INFO\\] OC_LOAD_BITFILE TCL: With >1 target you need to specify'
                      '--usb <n> where <n> is 0-$maxusb"\n')
                    w('}\n')
                w('if { $num_targets == 0 } {\n')
                w('  puts "\\[ERROR\\] OC_LOAD_BITFILE TCL: No HW_targets found!"\n')
                w('  exit\n}\n')

                if self.args['usb'] == -1:
                    w('if { $num_targets == 1 } {\n')
                    w('  puts "\\[INFO\\] OC_LOAD_BITFILE TCL: Defaulting to USB #0, since there is'
                      'only one device"\n')
                    w('  set usb 0\n} else {\n')
                    if not self.args['list-usbs']:
                        w('  set maxusb [expr $num_targets - 1]\n')
                        w('  puts "\\[ERROR\\] OC_LOAD_BITFILE TCL: Need --usb <n> argument, <n>'
                          'being 0-$maxusb, use --list-usbs if needed"\n')
                    w('  exit\n}\n')
                else:
                    w(f'set usb {self.args["usb"]}\n')

                w('if { $num_targets <= $usb } {\n')
                w('  puts "\\[ERROR\\] OC_LOAD_BITFILE TCL: hw_target #$usb doesn\'t exist!!"\n')
                w('  exit\n}\n')
                w('set hw_target [lindex $hw_targets $usb]\n')
                w('current_hw_target $hw_target\n')
                w('open_hw_target\n')
                w('refresh_hw_target\n')

                w('set hw_devices [get_hw_devices -quiet]\n')
                w('set num_devices [llength $hw_devices]\n')
                if self.args['list-devices']:
                    w('puts "\\[INFO\\] OC_LOAD_BITFILE TCL $num_devices devices found"\n')
                    w('for {set d 0} {$d < $num_devices} {incr d} {\n')
                    w('  puts "\\[INFO\\] OC_LOAD_BITFILE TCL: Device $d :'
                      '[lindex $hw_devices $d]"\n')
                    w('}\n')

                if self.args['device'] == -1:
                    w('if { $num_devices > 1 } {\n')
                    w('  if { [lindex $hw_devices 0] eq "arm_dap_0" } {\n')
                    w('    set hw_device [lindex $hw_devices 1]\n  } else {\n')
                    w('    set hw_device [lindex $hw_devices 0]\n  }\n')
                    w('}\n')
                else:
                    w(f'set hw_device [lindex $hw_devices {self.args["device"]  }]\n')

                w('puts "HW_DEVICE DID  : [get_property DID $hw_device]"\n')
                w('puts "HW_DEVICE PART : [get_property PART $hw_device]"\n')
                w('current_hw_device $hw_device\n')
                w('refresh_hw_device -update_hw_probes false -quiet $hw_device\n')

                if bitfile is not None:
                    w('set_property PROGRAM.FILE {' + bitfile + '} $hw_device\n')
                    w('program_hw_devices [current_hw_device]\n')

                w('close_hw_target\n')

        except OSError as exc:
            util.error(f"Cannot create {script_file}: {exc}")

        if bitfile is None:
            util.info("No bitfile provided or found")
        else:
            if os.path.isfile(bitfile):
                util.info(f"Using bitfile {bitfile}")
            else:
                util.warning(f"Using bitfile {bitfile}, which doesn't exist (or is not a file)")

        if self.args['test-mode']:
            util.info(f"test-mode set, upload skipped, {script_file=}")
            return

        # ── Execute Vivado ───────────────────────────────────────────────────────
        command_list = [
            self.vivado_exe, '-mode', 'batch', '-source', str(script_file), '-log', str(log_file)
        ]
        if not util.args['verbose']:
            command_list.append('-notrace')
        self.exec(Path(util.getcwd()), command_list)

        if not self.args['keep']:
            os.unlink(self.args['tcl-file'])

        util.info("Upload done")


class CommandOpenVivado(CommandOpen, ToolVivado):
    '''CommandOpenVivado command handler class used by: eda open --tool vivado'''
    def __init__(self, config: dict):
        CommandOpen.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this tool
        self.args['gui'] = True
        self.args['file'] = False
        self.args['all-sv'] = False

    def do_it(self):
        if not self.args['file']:
            util.info("Searching for project...")
            found_file = False
            all_files = []
            for root, _, files in os.walk("."):
                for file in files:
                    if file.endswith(".xpr"):
                        found_file = os.path.abspath(os.path.join(root,file))
                        util.info(f"Found project: {found_file}")
                        all_files.append(found_file)
            self.args['file'] = found_file
            if len(all_files) > 1:
                all_files.sort(key=os.path.getmtime)
                self.args['file'] = all_files[-1]
                util.info(f"Choosing: {self.args['file']} (newest)")
        if not self.args['file']:
            self.error("Couldn't find an XPR Vivado project to open")
        projname = os.path.splitext(os.path.basename(self.args['file']))[0]
        projdir = os.path.dirname(self.args['file'])
        oc_root = util.get_oc_root()
        oc_vivado_tcl = os.path.join(oc_root, 'boards', 'vendors', 'xilinx', 'oc_vivado.tcl')
        command_list = [
            self.vivado_exe, '-source', oc_vivado_tcl,
            '-log', f"{projname}.open.log", self.args['file']
        ]
        self.write_eda_config_and_args()
        self.exec(projdir, command_list)
