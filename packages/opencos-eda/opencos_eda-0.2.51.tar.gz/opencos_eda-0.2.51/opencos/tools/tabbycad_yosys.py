''' tabbycad_yosys - eda support for: eda synth --tool=tabbycad_yosys

This will likely require licenses for the TabbyCAD suite'''

# pylint: disable=R0801 # (duplicate code in derived classes, such as if-condition return.)

# TOOD(drew): fix this pylint eventually:
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

import os

from opencos import util
from opencos.tools.yosys import ToolYosys, CommonSynthYosys


class ToolTabbyCadYosys(ToolYosys):
    '''ToolTabbyCadYosys - used as parent for CommandSynthTabbyCadYosys'''

    _TOOL = 'tabbycad_yosys'
    _URL = 'https://www.yosyshq.com/tabby-cad-datasheet'

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'OC_TOOL_TABBYCAD': None,
        })


class CommandSynthTabbyCadYosys(CommonSynthYosys, ToolTabbyCadYosys):
    '''Command handler for: eda synth --tool tabbycad_yosys.'''

    def __init__(self, config:dict):
        CommonSynthYosys.__init__(self, config)
        ToolTabbyCadYosys.__init__(self, config=self.config)


    def write_and_run_yosys_f_files(self) -> None:
        '''
        1. Creates and runs: yosys.verific.f
           -- should create post_verific_ls.txt
        2. python will examine this .txt file and compare to our blackbox_list (modules)
        3. Creates and runs: yosys.synth.f
           -- does blackboxing and synth steps
        4. Creates a wrapper for human debug and reuse: yosys.f
        '''

        # Note - big assumption here that "module myname" is contained in myname.[v|sv]:
        # Note - we use both synth-blackbox and yosys-blackbox lists to blackbox
        # modules in yosys (not verific)
        blackbox_list = self.args.get('yosys-blackbox', []) + self.args.get('synth-blackbox', [])
        blackbox_files_list = []
        for path in self.files_v + self.files_sv:
            leaf_filename = path.split('/')[-1]
            module_name = ''.join(leaf_filename.split('.')[:-1])
            if module_name in blackbox_list:
                blackbox_files_list.append(path)
        util.debug(f'tabbycad_yosys: {blackbox_list=}')

        # create {work_dir} / yosys
        work_dir = self.args.get('work-dir', '')
        assert work_dir
        work_dir = os.path.abspath(work_dir)
        verific_out_dir = os.path.join(work_dir, 'verific')
        yosys_out_dir = os.path.join(work_dir, 'yosys')
        for p in [verific_out_dir, yosys_out_dir]:
            util.safe_mkdir(p)

        verific_v_path = os.path.join(verific_out_dir, f'{self.args["top"]}.v')
        yosys_v_path = os.path.join(yosys_out_dir, f'{self.args["top"]}.v')


        script_verific_lines = []
        for name,value in self.defines.items():
            if not name:
                continue
            if name in ['SIMULATION']:
                continue

            if value is None:
                script_verific_lines.append(f'verific -vlog-define {name}')
            else:
                script_verific_lines.append(f'verific -vlog-define {name}={value}')

        # We must define SYNTHESIS for oclib_defines.vh to work correctly.
        if 'SYNTHESIS' not in self.defines:
            script_verific_lines.append('verific -vlog-define SYNTHESIS')

        for path in self.incdirs:
            script_verific_lines.append(f'verific -vlog-incdir {path}')

        for path in self.files_v:
            script_verific_lines.append(f'verific -sv {path}')

        for path in self.files_sv:
            script_verific_lines.append(f'verific -sv {path}')

        for path in self.files_vhd:
            script_verific_lines.append(f'verific -vhdl {path}')

        script_verific_lines += [
            # This line does the 'elaborate' step, and saves out a .v to verific_v_path.
            f'verific -import -vv -pp {verific_v_path} {self.args["top"]}',
            # this ls command will dump all the module instances, which we'll need to
            # know for blackboxing later.
            'tee -o post_verific_ls.txt ls',
        ]

        yosys_verific_f_path = os.path.join(work_dir, 'yosys.verific.f')
        with open(yosys_verific_f_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(script_verific_lines))

        # Run our created yosys.verific.f script
        # Note - this will always run, even if --stop-before-compile is set.
        self.exec(work_dir=work_dir, command_list=['yosys', '--scriptfile', yosys_verific_f_path],
                  tee_fpath='yosys.verific.log')
        util.info('yosys.verific.f: wrote: ' + os.path.join(work_dir, 'post_verific_ls.txt'))

        # Based on the results in post_verific_ls.txt, create blackbox commands for
        # yosys.synth.f script.
        yosys_blackbox_list = []
        with open(os.path.join(work_dir, 'post_verific_ls.txt'), encoding='utf-8') as f:
            # compare these against our blackbox modules:
            for line in f.readlines():
                util.debug(f'post_verific_ls.txt: {line=}')
                if line.startswith('  '):
                    line = line.strip()
                    if len(line.split()) == 1:
                        # line has 1 word and starts with leading spaces:
                        # get the base module if it has parameters, etc:
                        # verific in TabbyCAD will output something like
                        # foo(various_parameters...), so the base
                        # module is before the '(' in their instance name.
                        base_module = line.split('(')[0]
                        if base_module in blackbox_list:
                            # we need the full (stripped whitespace) line
                            yosys_blackbox_list.append(line)


        # Create yosys.synth.f
        yosys_synth_f_path = os.path.join(work_dir, 'yosys.synth.f')
        synth_command = self.args.get('yosys-synth', 'synth')

        with open(yosys_synth_f_path, 'w', encoding='utf-8') as f:
            lines = [
                # Since we exited yosys, we have to re-open the verific .v file
                f'verific -sv {verific_v_path}',
                # We also have to re-import it (elaborate) it.
                f'verific -import {self.args["top"]}',
            ]

            for inst in yosys_blackbox_list:
                lines.append('blackbox ' + inst)

            lines += self.args.get('yosys-pre-synth', [])
            lines += [
                synth_command,
                f'write_verilog {yosys_v_path}'
            ]
            f.write('\n'.join(lines))

        # We create a yosys.f wrapping these scripts, but we do not run this one.
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_yosys.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                util.ShellCommandList(
                    ['yosys', '--scriptfile', 'yosys.verific.f'],
                    tee_fpath='yosys.verific.log'
                ),
                util.ShellCommandList(
                    ['yosys', '--scriptfile', 'yosys.synth.f'],
                    tee_fpath='yosys.synth.log'
                ),
            ],
        )

        # Do not run this if args['stop-before-compile'] is True
        # TODO(drew): I could move this earlier if I ran this whole process out of
        # a side generated .py file.
        if self.args.get('stop-before-compile', False):
            return

        # Run these commands.
        self.exec(work_dir=work_dir, command_list=['yosys', '--scriptfile', yosys_synth_f_path],
                  tee_fpath='yosys.synth.log')
        if self.status == 0:
            util.info(f'yosys: wrote verilog to {yosys_v_path}')
        return
