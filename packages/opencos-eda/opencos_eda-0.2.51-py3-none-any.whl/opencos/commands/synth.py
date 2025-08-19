'''opencos.commands.synth - Base class command handler for: eda synth ...

Intended to be overriden by Tool based classes (such as CommandSynthVivado, etc)
'''

# Note - similar code waiver, tricky to eliminate it with inheritance when
# calling reusable methods.
# pylint: disable=R0801

import os

from opencos import util, export_helper
from opencos.eda_base import CommandDesign, Tool


class CommandSynth(CommandDesign):
    '''Base class command handler for: eda synth ...'''

    CHECK_REQUIRES = [Tool]
    error_on_no_files_or_targets = True
    error_on_missing_top = True

    command_name = 'synth'

    def __init__(self, config: dict):
        CommandDesign.__init__(self, config=config)
        self.args.update({
            'flatten-all': False,
            'flatten-none':  False,
            'clock-name': 'clock',
            'clock-ns': 5,
            'idelay-ns': 2,
            'odelay-ns': 2,
            'synth-blackbox': [],
        })
        self.defines['SYNTHESIS'] = None

    def do_it(self) -> None:
        '''Common do_it() method that child classes can use prior to customization'''

        # set_tool_defines() is from class Tool. Since that is not inherited yet, but
        # should be by any handlers like CommandSynthSlang, etc, check on the existence
        # of set_tool_defines, and error if not present.
        if not all(isinstance(self, x) for x in self.CHECK_REQUIRES):
            self.error('CommandSynth.do_it() requires a Tool to be in parent classes, but none is.',
                       f'{self.CHECK_REQUIRES=}')
            return

        # add defines for this job from Tool class if present
        self.command_safe_set_tool_defines() # (Command.command_safe_set_tool_defines)

        # dump our config to work-dir for debug
        self.write_eda_config_and_args()

        # optionally export
        if self.is_export_enabled():
            self.do_export()

        # Derived classes can do the rest, can call CommandSynth.do_it(self) as a first step.

    def process_tokens(self, tokens: list, process_all: bool = True,
                       pwd: str = os.getcwd()) -> list:
        unparsed = CommandDesign.process_tokens(
            self, tokens=tokens, process_all=process_all, pwd=pwd
        )

        if self.status_any_error():
            return unparsed

        # add defines for this job type
        if self.args['top']:
            # create our work dir
            self.create_work_dir()
            self.run_dep_commands()
            self.do_it()
        return unparsed

    def do_export(self):
        '''CommandSynth helper for handling args --export*

        We allow commands such as: eda synth --export <target>
        '''

        out_dir = os.path.join(self.args['work-dir'], 'export')

        target = self.target
        if not target:
            target = 'test'

        export_obj = export_helper.ExportHelper(
            cmd_design_obj=self,
            eda_command=self.command_name,
            out_dir=out_dir,
            # Note this may not be the correct target for debug infomation,
            # so we'll only have the first one.
            target=target
        )

        # Set things in the exported: DEPS.yml
        tool = self.args.get('tool', None)
        # Certain args are allow-listed here
        deps_file_args = []
        for a in self.get_command_line_args():
            if any(a.startswith(x) for x in [
                    '--optimize',
                    '--synth',
                    '--idelay',
                    '--odelay',
                    '--flatten',
                    '--clock',
                    '--yosys']):
                deps_file_args.append(a)

        export_obj.run(
            deps_file_args=deps_file_args,
            export_json_eda_config={
                'tool': tool,
            }
        )

        if self.args['export-run']:

            # remove the '--export' named args, we don't want those.
            args_no_export = self.get_command_line_args(remove_args_startswith=['export'])

            command_list = ['eda', self.command_name] + args_no_export + [target]

            util.info(f'export-run: from {export_obj.out_dir=}: {command_list=}')
            self.exec(
                work_dir=export_obj.out_dir,
                command_list=command_list,
            )
