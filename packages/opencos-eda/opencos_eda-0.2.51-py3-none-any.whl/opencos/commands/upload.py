'''opencos.commands.upload - Base class command handler for: eda upload ...

Intended to be overriden by Tool based classes (such as CommandUploadVivado, etc)
'''

import os

from opencos.eda_base import Command, Tool

class CommandUpload(Command):
    '''Base class command handler for: eda upload ...'''

    CHECK_REQUIRES = [Tool]

    command_name = 'upload'

    def __init__(self, config: dict):
        Command.__init__(self, config=config)
        self.unparsed_args = []

    def process_tokens(
            self, tokens: list, process_all: bool = True, pwd: str = os.getcwd()
    ) -> list:

        self.unparsed_args = Command.process_tokens(
            self, tokens=tokens, process_all=False, pwd=pwd
        )
        self.create_work_dir()
        self.do_it()
        return []
