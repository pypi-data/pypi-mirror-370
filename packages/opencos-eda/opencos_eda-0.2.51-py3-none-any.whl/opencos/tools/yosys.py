''' opencos.tools.yosys - base class for slang_yosys.py, invio_yosys.py, tabbycad_yosys.py

Contains classes for ToolYosys
'''

# pylint: disable=R0801 # (calling functions with same arguments)

import os
import shutil
import subprocess

from opencos import util, eda_config
from opencos.eda_base import Tool, get_eda_exec
from opencos.commands import CommandSynth, CommandLec
from opencos.utils.markup_helpers import yaml_safe_load


def get_commands_to_run_scriptfiles(
        script_fnames_list: list, yosys_exe: str
) -> [util.ShellCommandList]:
    '''Checks file existence and returns list of commands to run a

    list of yoysys script(s)'''

    if script_fnames_list:
        return []

    yosys_cmdlists = []
    for i,fpath in enumerate(script_fnames_list):
        if not os.path.isfile(fpath):
            util.error(f'yosys-scriptfile={fpath} file does not exist')
        cmdlist = util.ShellCommandList(
            [yosys_exe, '--scriptfile', os.path.abspath(fpath)],
            tee_fpath = f'yosys_scriptfile.{i}.log'
        )
        yosys_cmdlists.append(cmdlist)
    return yosys_cmdlists


class ToolYosys(Tool):
    '''Parent class for ToolTabbyCadYosys, ToolInvioYosys, ToolSlangYosys'''

    _TOOL = 'yosys'
    _EXE = 'yosys'
    _URL = 'https://yosyshq.readthedocs.io/en/latest/'

    yosys_exe = ''
    sta_exe = ''
    sta_version = ''

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION

        path = shutil.which(self._EXE)
        if not path:
            self.error(f'"{self._EXE}" not in path or not installed, see {self._URL}')
        else:
            self.yosys_exe = path

        # Unforunately we don't have a non-PATH friendly support on self._EXE to set
        # where standalone 'sta' is. Even though Yosys has 'sta' internally, Yosys does
        # not fully support timing constraints or .sdc files, so we have to run 'sta'
        # standalone.
        sta_path = shutil.which('sta')
        if sta_path:
            util.debug(f'Also located "sta" via {sta_path}')
            self.sta_exe = sta_path
            sta_version_ret = subprocess.run(
                [self.sta_exe, '-version'], capture_output=True, check=False
            )
            util.debug(f'{self.yosys_exe} {sta_version_ret=}')
            sta_ver = sta_version_ret.stdout.decode('utf-8', errors='replace').split()[0]
            if sta_ver:
                self.sta_version = sta_ver

        version_ret = subprocess.run(
            [self.yosys_exe, '--version'], capture_output=True, check=False
        )
        util.debug(f'{self.yosys_exe} {version_ret=}')

        # Yosys 0.48 (git sha1 aaa534749, clang++ 14.0.0-1ubuntu1.1 -fPIC -O3)
        words = version_ret.stdout.decode('utf-8', errors='replace').split()

        if len(words) < 2:
            self.error(f'{self.yosys_exe} --version: returned unexpected str {version_ret=}')
        self._VERSION = words[1]
        return self._VERSION

    def set_tool_defines(self):
        self.defines.update({
            'OC_TOOL_YOSYS': None
        })
        if 'OC_LIBRARY' not in self.defines:
            self.defines.update({
                'OC_LIBRARY_BEHAVIORAL': None,
                'OC_LIBRARY': "0"
            })


class CommonSynthYosys(CommandSynth, ToolYosys):
    '''Common parent class used by invio_yosys and tabbycad_yosys

    for child classes: CommandSynthInvioYosys and tabbycad_yosys.CommandSynthTabbyCadYosys
    '''

    def __init__(self, config: dict):
        CommandSynth.__init__(self, config=config)
        ToolYosys.__init__(self, config=self.config)

        self.args.update({
            'sta': False,
            'liberty-file': '',
            'sdc-file': '',
            'yosys-synth': 'synth',              # synth_xilinx, synth_altera, etc (see: yosys help)
            'yosys-pre-synth': ['prep', 'proc'], # command run in yosys prior to yosys-synth.
            'yosys-blackbox': [],                # list of modules that yosys will blackbox.
            'yosys-scriptfile': [],
            'sta-scriptfile': [],
            'rename-module': ''
        })
        self.args_help.update({
            'sta': (
                'After running Yosys, run "sta" with --liberty-file.'
                ' sta can be installed via: https://github.com/The-OpenROAD-Project/OpenSTA'
            ),
            'sdc-file': (
                '.sdc file to use with --sta, if not present will use auto constraints.'
                ' Note you can have .sdc files in "deps" of DEPS.yml targets.'
            ),
            'liberty-file': (
                'Single liberty file for synthesis and sta,'
                ' for example: github/OpenSTA/examples/nangate45_slow.lib.gz'
            ),
            'yosys-synth': 'The synth command provided to Yosys, see: yosys help.',
            'yosys-pre-synth': (
                'Yosys commands performed prior to running "synth"'
                ' (or eda arg value for --yosys-synth)'
            ),
            'yosys-blackbox': (
                'List of modules that yosys will blackbox, likely will need these'
                ' in Verilog-2001 for yosys to read outside of slang and synth'
            ),
            'yosys-scriptfile': (
                'Instead of using a built-in flow from eda, use your own scripts that are called'
                ' via: yosys --scriptfile <this-arg>. You can set multiple args for multiple'
                ' scriptfile (appends)'
            ),
            'sta-scriptfile': (
                'Instead of using a built-in flow from eda, use your own script that is called'
                ' via: sta -no_init -exit <this-arg>.  You can set multiple args for multiple'
                ' scriptfile (appends)'
            ),
            'rename-module': 'Renames the output .v and module name',
        })

        self.yosys_out_dir = ''
        self.yosys_v_path = ''
        self.full_work_dir = ''
        self.blackbox_list = []
        self.top_module = ''

    def do_it(self) -> None:
        self.set_tool_defines()
        self.write_eda_config_and_args()

        # Set up some dirs and filenames.
        self.full_work_dir = self.args.get('work-dir', '')
        if not self.full_work_dir:
            self.error(f'work_dir={self.full_work_dir} is not set')
        self.full_work_dir = os.path.abspath(self.full_work_dir)
        self.yosys_out_dir = os.path.join(self.full_work_dir, 'yosys')
        util.safe_mkdir(self.yosys_out_dir)
        self.yosys_v_path = os.path.join(self.yosys_out_dir, f'{self.args["top"]}.v')

        if self.is_export_enabled():
            self.do_export()
            return

        if self.args['yosys-scriptfile']:
            yosys_cmdlists = self.get_commands_user_yosys_scriptfile()
            sta_cmdlists = self.create_sta_f() # works for --sta w/out BYO scripts.

            # We create a run_yosys.sh wrapping these scripts, but we do not run this one.
            util.write_shell_command_file(
                dirpath=self.args['work-dir'],
                filename='run_yosys.sh',
                command_lists=(yosys_cmdlists + sta_cmdlists)
            )

            # actually run it.
            for x in yosys_cmdlists + sta_cmdlists:
                if x:
                    self.exec(work_dir=self.full_work_dir, command_list=x,
                              tee_fpath=x.tee_fpath)

        else:
            self.write_and_run_yosys_f_files()


    def get_commands_user_yosys_scriptfile(self) -> [util.ShellCommandList]:
        '''Checks file existence and returns list of commands to run a

        list of yoysys script(s)'''
        cmd_lists = get_commands_to_run_scriptfiles(
            script_fnames_list=self.args['yosys-scriptfile'],
            yosys_exe=self.yosys_exe
        )

        if not cmd_lists:
            util.error('Could not generate yosys commands for scripts',
                       f'{self.args["yosys-scriptfile"]}')

        return cmd_lists


    def get_commands_user_sta_scriptfile(self) -> [util.ShellCommandList]:
        '''Checks file existence and returns list of commands'''
        if not self.args['sta-scriptfile']:
            return []

        ret_list = []
        for i,fpath in enumerate(self.args['sta-scriptfile']):
            if not os.path.isfile(fpath):
                self.error(f'sta-scriptfile={fpath} file does not exist')
            cmdlist = util.ShellCommandList(
                [self.sta_exe, '-no_init', '-exit', os.path.abspath(fpath)],
                tee_fpath = f'sta_scriptfile.{i}.log'
            )
            ret_list.append(cmdlist)
        return ret_list


    def write_and_run_yosys_f_files(self) -> None:
        '''Derived classes may override, to run remainder of do_it() steps

        These built-ins do not use slang or another SV preprocessing step.
        1. Creates and runs: yosys.synth.f
           -- does blackboxing and synth steps
        4. Creates a wrapper for human debug and reuse: yosys.f
        '''

        # Note - big assumption here that "module myname" is contained in myname.[v|sv]:
        # we use both synth-blackbox and yosys-blackbox lists to blackbox modules in the
        # yosys step (not in the slang step)
        self.blackbox_list = self.args.get('yosys-blackbox', [])
        self.blackbox_list += self.args.get('synth-blackbox', [])

        # work-dir / yosys has already been created.

        # Create and run yosys.synth.f
        synth_command_list = self.create_yosys_synth_f() # util.ShellCommandList

        # Optinally create and run a sta.f:
        sta_command_lists = self.create_sta_f() # [] or [util.ShellCommandList]

        # We create a run_yosys.sh wrapping these scripts, but we do not run this one.
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_yosys.sh',
            command_lists=[synth_command_list] + sta_command_lists,
        )

        # Do not run this if args['stop-before-compile'] is True
        if self.args.get('stop-before-compile', False):
            return

        # Run the synth commands standalone:
        self.exec(work_dir=self.full_work_dir, command_list=synth_command_list,
                  tee_fpath=synth_command_list.tee_fpath)

        for x in sta_command_lists:
            if self.args['sta'] and x:
                self.exec(work_dir=self.full_work_dir, command_list=x,
                          tee_fpath=x.tee_fpath)

        if self.status == 0:
            util.info(f'yosys: wrote verilog to {self.yosys_v_path}')


    def create_yosys_synth_f(self) -> util.ShellCommandList:
        '''Derived classes may define, if they wish to get a list of yosys commands'''

        # Create yosys.synth.f
        yosys_synth_f_path = os.path.join(self.full_work_dir, 'yosys.synth.f')

        # Since this assumes we didnt' run a SystemVerilog pre-processing step,
        # read in all the verilog
        yosys_blackbox_list = self.get_yosys_blackbox_list()

        if self.args['liberty-file'] and not os.path.exists(self.args['liberty-file']):
            self.error(f'--liberty-file={self.args["liberty-file"]} file does not exist')

        with open(yosys_synth_f_path, 'w', encoding='utf-8') as f:
            lines = [
                self._get_read_verilog_one_liner()
            ]

            if self.args['liberty-file']:
                lines.append('read_liberty -lib ' + self.args['liberty-file'])

            for inst in yosys_blackbox_list:
                lines.append('blackbox ' + inst)

            lines += self.get_synth_command_lines()
            f.write('\n'.join(lines))

        synth_command_list = util.ShellCommandList(
            [self.yosys_exe, '--scriptfile', 'yosys.synth.f'],
            tee_fpath = 'yosys.synth.log'
        )
        return synth_command_list


    def get_synth_command_lines(self) -> list:
        '''Common yosys tcl after all blackbox and read_verilog commands'''

        lines = []
        lines += self.args.get('yosys-pre-synth', [])

        synth_command = self.args.get('yosys-synth', 'synth')
        if self.args['flatten-all']:
            synth_command += ' -flatten'

        lines.append(synth_command)


        # TODO(drew): I need a blackbox flow here? Or a memory_libmap?
        #   --> https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/memory_libmap.html
        # TODO(drew): can I run multiple liberty files?
        if self.args['liberty-file']:
            lines += [
                'dfflibmap -liberty ' + self.args['liberty-file'],
                #'memory_libmap -lib ' + self.args['liberty-file'], # Has to be unzipped?
                'abc -liberty  ' + self.args['liberty-file'],
            ]
        lines += [
            'opt_clean',
        ]
        if self.args['rename-module']:
            lines += [f'rename {self.args["top"]} {self.args["rename-module"]}']
            self.top_module = self.args['rename-module']
        else:
            self.top_module = self.args["top"]
        lines += [
            f'write_verilog {self.yosys_v_path}',
            f'write_json {self.yosys_v_path}.json',
        ]
        return lines

    def get_yosys_blackbox_list(self) -> list:
        '''Returns blackbox list, since we don't have a preprocessing step like

        slang, simply return self.blackbox_list. Intended to be overwritten by
        derived classes so they can blackbox post-preprocessing.
        '''
        return self.blackbox_list


    def create_sta_f(self) -> [util.ShellCommandList]:
        '''Returns command list, for running 'sta' on sta.f'''

        if not self.args['sta']:
            return []

        if self.args['sta-scriptfile']:
            # User brought one or more scriptfiles for STA, use those.
            return self.get_commands_user_sta_scriptfile()

        if not self.args['liberty-file']:
            self.error('--sta is set, but need to also set --liberty-file=<file>')

        if self.args['sdc-file']:
            if not os.path.exists(self.args['sdc-file']):
                self.error(f'--sdc-file={self.args["sdc-file"]} file does not exist')

        if not self.sta_exe:
            self.error(f'--sta is set, but "sta" was not found in PATH, see: {self._URL}')

        sta_command_list = util.ShellCommandList(
            [ self.sta_exe, '-no_init', '-exit', 'sta.f' ],
            tee_fpath = 'sta.log'
        )

        # Need to create sta.f:
        if self.args['sdc-file']:
            sdc_path = self.args['sdc-file']
        elif self.files_sdc:
            # Use files from DEPS target or command line.
            sdc_path = ''
        else:
            # Need to create sdc.f:
            sdc_path = 'sdc.f'
            self.create_sdc_f()

        with open(os.path.join(self.args['work-dir'], 'sta.f'), 'w',
                  encoding='utf-8') as f:
            lines = [
                'read_liberty ' + self.args['liberty-file'],
                'read_verilog ' + self.yosys_v_path,
                'link_design ' + self.top_module,
            ]
            for _file in self.files_sdc:
                lines.append('read_sdc ' + _file)
            if sdc_path:
                lines.append('read_sdc ' + sdc_path)

            lines.append('report_checks')

            f.write('\n'.join(lines))

        # return list with our one generated command-list
        return [util.ShellCommandList(
            sta_command_list,
            tee_fpath = sta_command_list.tee_fpath
        )]


    def create_sdc_f(self) -> None:
        '''Returns None, creates sdc.f'''

        if self.args['sdc-file']:
            # already exists from args, return b/c nothing to create.
            return

        with open(os.path.join(self.args['work-dir'], 'sdc.f'), 'w',
                  encoding='utf-8') as f:
            clock_name = self.args['clock-name']
            period = self.args['clock-ns']
            name_not_equal_clocks_str = f'NAME !~ "{clock_name}"'
            lines = [
                f'create_clock -add -name {clock_name} -period {period} [get_ports ' \
                + '{' + clock_name + '}];',
                f'set_input_delay -max {self.args["idelay-ns"]} -clock {clock_name}' \
                + ' [get_ports * -filter {DIRECTION == IN && ' \
                + name_not_equal_clocks_str + '}];',
                f'set_output_delay -max {self.args["odelay-ns"]} -clock {clock_name}' \
                + ' [get_ports * -filter {DIRECTION == OUT}];',
            ]
            f.write('\n'.join(lines))


    def _get_read_verilog_one_liner(self) -> str:
        '''Returns a string, intended to be used w/out Slang, for Verilog or simple

        SV designs'''

        read_verilog_cmd = [
            'read_verilog',
            '-sv',
            '-icells',
        ]
        read_verilog_cmd += self.get_yosys_read_verilog_defines_incdirs_files()
        read_verilog_cmd.append(f'--top {self.args["top"]}')
        return ' '.join(read_verilog_cmd)


    def get_yosys_read_verilog_defines_incdirs_files(self) -> list:
        '''Returns a partial list of all the args for a read_verilog or read_slang command in yosys

        Handles defines, incdirs, files_sv, files_v
        '''
        ret_list = []

        for name,value in self.defines.items():
            if not name:
                continue
            if name in ['SIMULATION']:
                continue

            if value is None:
                ret_list.append(f'--define-macro {name}')
            else:
                ret_list.append(f'--define-macro {name}={value}')

        # We must define SYNTHESIS for oclib_defines.vh to work correctly.
        if 'SYNTHESIS' not in self.defines:
            ret_list.append('--define-macro SYNTHESIS')

        for path in self.incdirs:
            ret_list.append(f'-I {path}')

        for path in self.files_v:
            ret_list.append(path)

        for path in self.files_sv:
            ret_list.append(path)

        ret_list.append(f'--top {self.args["top"]}')
        return ret_list


class CommandLecYosys(CommandLec, ToolYosys):
    '''Command handler for: eda lec --designs=<target1> --designs=<target2> --tool=yosys

    Also supports: eda lec --tool=yosys <target>
    If the target sets two args for --designs
    '''

    def __init__(self, config: dict):
        CommandLec.__init__(self, config=config)
        ToolYosys.__init__(self, config=self.config)

        self.args.update({
            'yosys-scriptfile': [],
            'pre-read-verilog': [],
        })
        self.args_help.update({
            'yosys-scriptfile': (
                'Instead of using a built-in flow from eda, use your own scripts that are called'
                ' via: yosys --scriptfile <this-arg>. You can set multiple args for multiple'
                ' scriptfile (appends)'
            ),
            'pre-read-verilog': 'Additional verilog files to read prior to running LEC',
        })

        self.synth_work_dirs = [
            os.path.join('eda.work', 'lec.Design1.synth'),
            os.path.join('eda.work', 'lec.Design2.synth')
        ]

        self.synth_designs_tops = [None, None]
        self.synth_designs_fpaths = [None, None]
        self.synth_design_top_module_names = [None, None]

    def get_synth_result_fpath(self, target: str) -> str:
        '''Overridden from CommandLec'''

        # Read the eda_output_config.yml, find the "top", and find the output .v filename.
        return ""

    def get_synth_command_list(self, design_num: int) -> list:
        '''Returns one of the synthesis command lists, for design_num=0 or 1'''

        if not design_num in [0, 1]:
            self.error(f'{design_num=} we only support LEC on designs 0 and 1')

        synth_cmd_list = [
            get_eda_exec('synth'),
            'synth',
        ]

        if self.args['tool']:
            synth_cmd_list.append('--tool=' + self.args['tool'])

        synth_cmd_list += [
            '--work-dir=' + self.synth_work_dirs[design_num],
            self.args['designs'][design_num],
            f'--rename-module=Design{design_num + 1}'
        ]

        self.synth_design_top_module_names[design_num] = f'Design{design_num + 1}'

        return synth_cmd_list


    def get_synth_top_from_output_config(self, design_num: int) -> str:
        '''Returns the top name given the design number that we synthesized'''

        work_dir = self.synth_work_dirs[design_num]
        output_cfg_fpath = os.path.join(work_dir, eda_config.EDA_OUTPUT_CONFIG_FNAME)
        data = yaml_safe_load(output_cfg_fpath)
        top = data.get('args', {}).get('top', '')
        if not top:
            self.error(f'"top" not found in synth run from {work_dir=} in',
                       f'config {output_cfg_fpath}')
        return top


    def get_synth_results_fpath(self, design_num: int, top: str) -> str:
        '''Returns the synthesized .v file fpath'''
        if not top:
            top = self.get_synth_top_from_output_config(design_num=design_num)

        work_dir = self.synth_work_dirs[design_num]
        fpath = os.path.join(work_dir, 'yosys', f'{top}.v')
        if not os.path.isfile(fpath):
            self.error(f'{fpath=} does not exists, looking for synth results for LEC {design_num=}')
        return fpath


    def do_it(self) -> None:
        self.set_tool_defines()
        self.write_eda_config_and_args()

        pwd = os.getcwd()

        if not self.args['top']:
            self.args['top'] = 'yosys_lec'

        if self.args['yosys-scriptfile']:
            yosys_cmdlists = get_commands_to_run_scriptfiles(
                script_fnames_list=self.args['yosys-scriptfile'],
                yosys_exe=self.yosys_exe
            )

            # We create a run_yosys.sh wrapping these scripts, but we do not run this one.
            util.write_shell_command_file(
                dirpath=self.args['work-dir'],
                filename='run_yosys.sh',
                command_lists=yosys_cmdlists
            )

            # actually run it.
            for x in yosys_cmdlists:
                if x:
                    self.exec(work_dir=self.args['work-dir'], command_list=x,
                              tee_fpath=x.tee_fpath)


        if self.args['synth']:
            synth1_cmd_list = self.get_synth_command_list(design_num=0)
            synth2_cmd_list = self.get_synth_command_list(design_num=1)

            util.info(f'LEC {synth1_cmd_list=}')
            util.info(f'LEC {synth2_cmd_list=}')

            self.exec(pwd, synth1_cmd_list, background=True)
            util.info(f'Finished with 1st LEC synthesis {self.args["designs"][0]}')

            self.exec(pwd, synth2_cmd_list, background=True)
            util.info(f'Finished with 2nd LEC synthesis {self.args["designs"][1]}')

            self.synth_designs_tops = [
                self.get_synth_top_from_output_config(design_num=0),
                self.get_synth_top_from_output_config(design_num=1)
            ]
            util.info(f'Design tops: {self.synth_designs_tops}')

            # read the output config
            self.synth_designs_fpaths = [
                os.path.abspath(
                    self.get_synth_results_fpath(design_num=0, top=self.synth_designs_tops[0])),
                os.path.abspath(
                    self.get_synth_results_fpath(design_num=1, top=self.synth_designs_tops[1]))
            ]
            util.info(f'Design tops: {self.synth_designs_fpaths}')

        else:
            # don't run synthesis, need the two top level .v files in
            # self.synth_designs_fpaths, and need the two top module names in
            # self.synth_designs_tops
            self.synth_designs_fpaths = [
                os.path.abspath(self.args['designs'][0]),
                os.path.abspath(self.args['designs'][1])
            ]

            path, fname = os.path.split(self.synth_designs_fpaths[0])
            module_guess, _ = os.path.splitext(fname)
            top1 = util.get_inferred_top_module_name(
                module_guess=module_guess, module_fpath=self.synth_designs_fpaths[0]
            )
            util.info(f'design1 top module name = {top1} (from {path} / {fname})')

            path, fname = os.path.split(self.synth_designs_fpaths[1])
            module_guess, _ = os.path.splitext(fname)
            top2 = util.get_inferred_top_module_name(
                module_guess=module_guess, module_fpath=self.synth_designs_fpaths[1]
            )
            util.info(f'design2 top module name = {top2} (from {path} / {fname})')

            self.synth_designs_tops = [top1, top2]

        # Need to create final LEC yosys script, that reads our two designs and runs
        # LEC. Note the designs must have different module names
        if self.synth_designs_tops[0] == self.synth_designs_tops[1]:
            self.error('Cannot run Yosys LEC on two designs with the same top module name:',
                       f'{self.synth_designs_tops}')

        lec_cmd_f_list = []
        if self.args['pre-read-verilog']:
            for x in self.args['pre-read-verilog']:
                if os.path.isfile(x):
                    lec_cmd_f_list += [
                        'read_verilog -sv -icells ' + os.path.abspath(x)
                    ]
                else:
                    self.error(f' --pre-read-verilog file {x} does not exist')
        lec_cmd_f_list += [
            '# Design1 (module):',
            f'read_verilog -sv -icells {self.synth_designs_fpaths[0]}',
            '# Design2 (module):',
            f'read_verilog -sv -icells {self.synth_designs_fpaths[1]}',
            'clk2fflogic;',
            f'miter -equiv -flatten {" ".join(self.synth_design_top_module_names)} miter',
            ('sat -seq 50 -verify -prove trigger 0 -show-all -show-inputs -show-outputs'
             ' -set-init-zero miter'),
        ]

        lec_cmd_f_fpath = os.path.join(self.args['work-dir'], 'yosys_lec.f')
        with open(lec_cmd_f_fpath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lec_cmd_f_list) + '\n')

        lec_cmd_list = 'yosys --scriptfile yosys_lec.f'.split()
        util.info(f'LEC running {lec_cmd_list}')
        self.exec(self.args['work-dir'], lec_cmd_list)
