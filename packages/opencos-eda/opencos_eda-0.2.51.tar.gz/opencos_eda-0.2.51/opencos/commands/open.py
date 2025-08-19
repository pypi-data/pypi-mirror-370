'''opencos.commands.open - Base class command handler for: eda open ...

Intended to be overriden by Tool based classes (such as CommandOpenVivado, etc)
'''

import os

from opencos.eda_base import CommandDesign

class CommandOpen(CommandDesign):
    '''Base class command handler for: eda open ...'''

    command_name = 'open'

    def __init__(self, config: dict):
        CommandDesign.__init__(self, config=config)

    def process_tokens(
            self, tokens: list, process_all: bool = True,
            pwd: str = os.getcwd()
    ) -> list:

        unparsed = CommandDesign.process_tokens(
            self, tokens=tokens, process_all=process_all, pwd=pwd
        )
        self.do_it()
        return unparsed
