'''opencos.commands.targets - command handler for: eda targets [args]

Note this command is handled differently than others (such as CommandSim),
it is generally run as simply

    > eda targets
    > eda targets <directory>
    > eda targets [directory/]<pattern> [directory2/]<pattern2> ...

uses no tools and will print a pretty list of targets to stdout.
'''

# Note - similar code waiver, tricky to eliminate it with inheritance when
# calling reusable methods.
# pylint: disable=R0801

import os

from opencos import eda_extract_targets
from opencos.eda_base import Command


class CommandTargets:
    '''command handler for: eda targets'''

    command_name = 'targets'

    def __init__(self, config: dict):
        # We don't inherit opencos.eda_base.Command, so we have to set a few
        # member vars for Command.help to work.
        self.args = {}
        self.args_help = {}
        self.config = config
        self.status = 0

    def process_tokens( # pylint: disable=unused-argument
        self, tokens: list, process_all: bool = True,
        pwd: str = os.getcwd()
    ) -> list:
        '''This is effectively our 'run' method, entrypoint from opencos.eda.main'''

        eda_extract_targets.run(partial_paths=tokens, base_path=pwd)
        return []

    def help(self, tokens: list) -> None:
        '''Since we don't inherit from opencos.eda_base.Command, need our own help
        method
        '''
        Command.help(self, tokens=tokens)
