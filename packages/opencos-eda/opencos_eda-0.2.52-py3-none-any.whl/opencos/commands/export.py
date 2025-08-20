'''opencos.commands.export - Base class command handler for: eda export ...

Intended to be overriden by Tool based classes (such as CommandExportVivado, etc), although
`eda export` can be run without --tool.'''

# Note - similar code waiver, tricky to eliminate it with inheritance when
# calling reusable methods.
# pylint: disable=R0801

import os

from opencos import util, export_helper
from opencos.eda_base import CommandDesign

class CommandExport(CommandDesign):
    '''Base class command handler for: eda export ...'''

    error_on_no_files_or_targets = True
    error_on_missing_top = True

    command_name = 'export'

    def __init__(self, config: dict):
        CommandDesign.__init__(self, config=config)
        self.args.update({
            'output': "",

            # flatten mode is envisioned to remove all the dir hierarchy and write files
            # into a single dir, good for squeezing down into a simple extracted case
            # (perhaps to create a bug report).  This is envisioned as part of getting "eda"
            # sims running through a testrunner API.
            'flatten': False,
        })


    def process_tokens(
            self, tokens: list, process_all: bool = True, pwd: str = os.getcwd()
    ) -> list:

        unparsed = CommandDesign.process_tokens(
            self, tokens=tokens, process_all=process_all, pwd=pwd
        )
        if self.status_any_error():
            return unparsed
        if self.args['top']:
            # create our work dir, b/c top is set. We do this so any shell or peakrdl style
            # commands from DEPS can run in eda.work/{target}.export/
            # The final exported output (files and/or linked files) will be in
            # eda.export/{target}.export/
            self.create_work_dir()
            self.run_dep_commands()
            self.do_it()
        else:
            util.warning(f'CommandExport: {self.command_name=} not run due to lack of',
                         f'{self.args["top"]=} value')
        return unparsed

    def do_it(self) -> None:

        # decide output dir name
        if not self.args['output']:
            self.args['output'] = os.path.join('.', 'eda.export', self.args['top'] + '.export')
        out_dir = self.args['output']

        if not self.target:
            target = 'export'
        else:
            # Note this may not be the correct target for debug infomation,
            # for example if you passed several files as targets on the
            # command line, so we'll fall back to using self.target
            target = self.target

        export_obj = export_helper.ExportHelper(
            cmd_design_obj=self,
            eda_command=self.command_name,
            out_dir=out_dir,
            target=target
        )

        self.write_eda_config_and_args()
        export_obj.run(check_if_overwrite=True)

    # Methods that derived classes may override:

    def prepare_compile(self) -> None:
        '''Returns None, sets defines and other tasks prior to running an 'export' command

        This is Tool dependent, derived classes may override. A command pattern may be:
            ToolClass.set_tool_defines(self)
            self.defines.update({...}) # manually set some defines
            self.defines.update(
                self.tool_config.get('defines', {}) # update from --config-yml YAML file.
            )
        '''
        self.command_safe_set_tool_defines() # (Command.command_safe_set_tool_defines)
