'''opencos.commands.proj - Base class command handler for: eda open ...

Intended to be overriden by Tool based classes (such as CommandOpenVivado, etc)
'''

# Note - similar code waiver, tricky to eliminate it with inheritance when
# calling reusable methods.
# pylint: disable=R0801

import os

from opencos.eda_base import CommandDesign

class CommandProj(CommandDesign):
    '''Base class command handler for: eda proj ...'''

    command_name = 'proj'

    def __init__(self, config:dict):
        CommandDesign.__init__(self, config=config)

    def process_tokens(
            self, tokens: list, process_all: bool = True,
            pwd: str = os.getcwd()
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

        return unparsed
