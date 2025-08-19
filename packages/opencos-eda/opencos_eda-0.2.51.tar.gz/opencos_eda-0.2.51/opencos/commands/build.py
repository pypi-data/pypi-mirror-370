'''opencos.commands.build - Base class command handler for: eda build ...

Intended to be overriden by Tool based classes (such as CommandBuildVivado, etc)'''

# Note - similar code waiver, tricky to eliminate it with inheritance when
# calling reusable methods.
# pylint: disable=R0801

import os
from opencos import util
from opencos.eda_base import CommandDesign, Tool

class CommandBuild(CommandDesign):
    '''Base class command handler for: eda build ...'''

    CHECK_REQUIRES = [Tool]
    error_on_no_files_or_targets = True
    error_on_missing_top = True

    command_name = 'build'

    def __init__(self, config: dict):
        CommandDesign.__init__(self, config=config)
        self.args['build-script'] = "build.tcl"

    def process_tokens(
            self, tokens: list, process_all: bool = True, pwd: str = os.getcwd()
    ) -> list:

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
        else:
            util.warning(f'CommandBuild: {self.command_name=} not run due to lack of',
                         f'{self.args["top"]=} value')

        return unparsed
