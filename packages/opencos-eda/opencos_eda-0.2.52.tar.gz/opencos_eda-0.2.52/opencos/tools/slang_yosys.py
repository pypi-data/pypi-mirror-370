''' opencos.tools.slang_yosys - classes for: eda [synth|elab] --tool=slang_yosys

Contains classes for ToolSlangYosys, CommandSynthSlangYosys
'''

# pylint: disable=R0801 # (duplicate code in derived classes, such as if-condition return.)

import os

from opencos import util
from opencos.tools.yosys import ToolYosys, CommonSynthYosys, CommandLecYosys

class ToolSlangYosys(ToolYosys):
    '''Uses slang.so in yosys plugins directory, called via yosys > plugin -i slang'''
    _TOOL = 'slang_yosys'
    _URL = [
        'https://github.com/povik/yosys-slang',
        'https://github.com/The-OpenROAD-Project/OpenSTA',
        'https://yosyshq.readthedocs.io/en/latest/',
        'https://github.com/MikePopoloski/slang',
    ]

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'OC_TOOL_SLANG': None,
        })


class CommandSynthSlangYosys(CommonSynthYosys, ToolSlangYosys):
    '''CommandSynthSlangYosys is a command handler for: eda synth --tool=slang_yosys'''

    def __init__(self, config: dict):
        CommonSynthYosys.__init__(self, config)
        ToolSlangYosys.__init__(self, config=self.config)

        self.slang_out_dir = ''
        self.slang_v_path = ''

    def write_and_run_yosys_f_files(self) -> None:
        '''
        1. Creates and runs: yosys.slang.f
           -- should create post_slang_ls.txt
        2. python will examine this .txt file and compare to our blackbox_list (modules)
        3. Creates and runs: yosys.synth.f
           -- does blackboxing and synth steps
        4. Creates a wrapper for human debug and reuse: yosys.f
        '''

        # Note - big assumption here that "module myname" is contained in myname.[v|sv]:
        # we use both synth-blackbox and yosys-blackbox lists to blackbox modules in the
        # yosys step (not in the slang step)
        self.blackbox_list = self.args.get('yosys-blackbox', [])
        self.blackbox_list += self.args.get('synth-blackbox', [])
        util.debug(f'slang_yosys: {self.blackbox_list=}')

        # create {work_dir} / slang
        self.slang_out_dir = os.path.join(self.full_work_dir, 'slang')
        util.safe_mkdir(self.slang_out_dir)

        self.slang_v_path = os.path.join(self.slang_out_dir, f'{self.args["top"]}.v')

        # Run our created yosys.slang.f script
        # Note - this will always run, even if --stop-before-compile is set.
        slang_command_list = self._create_and_run_yosys_slang_f() # util.ShellCommandList

        # Create and run yosys.synth.f
        synth_command_list = self.create_yosys_synth_f() # util.ShellCommandList

        # Optinally create and run a sta.f:
        sta_command_lists = self.create_sta_f() # [] or [util.ShellCommandList]

        # We create a run_yosys.sh wrapping these scripts, but we do not run this one.
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_yosys.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                slang_command_list,
                synth_command_list,
            ] + sta_command_lists,
        )

        # Do not run this if args['stop-before-compile'] is True
        # TODO(drew): I could move this earlier if I ran this whole process out of
        # a side generated .py file, but we need to query things to generate the synth script.
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


    def _get_read_slang_cmd_str(self) -> str:

        read_slang_cmd = [
            'read_slang',
            '--ignore-unknown-modules',
            '--best-effort-hierarchy',
        ]

        read_slang_cmd += self.get_yosys_read_verilog_defines_incdirs_files()
        read_slang_cmd.append(f'--top {self.args["top"]}')
        return ' '.join(read_slang_cmd)


    def _create_and_run_yosys_slang_f(self) -> util.ShellCommandList:
        '''Runs, and Returns the util.ShellCommandList for: yosys --scriptfile yosys.slang.f'''

        script_slang_lines = [
            'plugin -i slang'
        ]

        script_slang_lines += [
            self._get_read_slang_cmd_str(), # one liner.
            # This line does the 'elaborate' step, and saves out a .v to slang_v_path.
            f'write_verilog {self.slang_v_path}',
            # this ls command will dump all the module instances, which we'll need to
            # know for blackboxing later. This is not in bash, this is within slang
            'tee -o post_slang_ls.txt ls',
        ]

        with open(os.path.join(self.full_work_dir, 'yosys.slang.f'), 'w',
                  encoding='utf-8') as f:
            f.write('\n'.join(script_slang_lines))

        # Run our created yosys.slang.f script
        # Note - this will always run, even if --stop-before-compile is set.
        slang_command_list = util.ShellCommandList(
            [self.yosys_exe, '--scriptfile', 'yosys.slang.f'],
            tee_fpath = 'yosys.slang.log'
        )
        self.exec(
            work_dir=self.full_work_dir,
            command_list=slang_command_list,
            tee_fpath=slang_command_list.tee_fpath
        )
        util.info('yosys.slang.f: wrote: ',
                  os.path.join(self.full_work_dir, 'post_slang_ls.txt'))

        # We create a run_slang.sh wrapping these scripts, but we do not run this one.
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_slang.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                slang_command_list,
            ],
        )
        return slang_command_list

    def get_yosys_blackbox_list(self) -> list:
        '''Based on the results in post_slang_ls.txt, create blackbox commands for

        yosys.synth.f script. Uses self.blackbox_list.
        '''
        yosys_blackbox_list = []
        with open(os.path.join(self.full_work_dir, 'post_slang_ls.txt'),
                  encoding='utf-8') as f:
            # compare these against our blackbox modules:
            for line in f.readlines():
                util.debug(f'post_slang_ls.txt: {line=}')
                if line.startswith('  '):
                    line = line.strip()
                    if len(line.split()) == 1:
                        # line has 1 word and starts with leading spaces:
                        # get the base module if it has parameters, etc:
                        # slang will output something like foo$various_parameters, so the base
                        # module is before the $ in their instance name.
                        base_module = line.split('$')[0]
                        if base_module in self.blackbox_list:
                            # we need the full (stripped whitespace) line
                            yosys_blackbox_list.append(line)
        return yosys_blackbox_list

    def create_yosys_synth_f(self) -> util.ShellCommandList:
        '''Overriden from CommonSynthYosys'''

        # Create yosys.synth.f
        yosys_synth_f_path = os.path.join(self.full_work_dir, 'yosys.synth.f')

        # Based on the results in post_slang_ls.txt, create blackbox commands for
        # yosys.synth.f script.
        yosys_blackbox_list = self.get_yosys_blackbox_list()

        if self.args['liberty-file'] and not os.path.exists(self.args['liberty-file']):
            self.error(f'--liberty-file={self.args["liberty-file"]} file does not exist')

        with open(yosys_synth_f_path, 'w', encoding='utf-8') as f:
            lines = [
                # Since we exited yosys, we have to re-open the slang .v file
                f'read_verilog -sv -icells {self.slang_v_path}',
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


class CommandElabSlangYosys(CommandSynthSlangYosys): # pylint: disable=too-many-ancestors
    '''CommandSynthSlangYosys is a command handler for: eda synth --tool=slang_yosys

    Runs slang-yosys as elab only (does not run the synthesis portion), but is
    run with SIMULATION not defined, SYNTHESIS defined.
    '''
    def __init__(self, config):
        super().__init__(config)
        self.command_name = 'elab'
        self.args.update({
            'stop-before-compile': True,
            'lint': True
        })

class CommandLecSlangYosys(CommandLecYosys, ToolSlangYosys): # pylint: disable=too-many-ancestors
    '''CommandHandler for: eda lec --tool=slang_yosys

    All steps from CommandLecYosys are re-used, except that using ToolSlangYosys
    instead of ToolYosys. This is necessary so the default --synth arg will
    synthesize the two designs using slang_yosys for the tool instead of yosys.
    '''

    def __init__(self, config: dict):
        CommandLecYosys.__init__(self, config)
        ToolSlangYosys.__init__(self, config=self.config)
