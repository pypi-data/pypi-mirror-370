'''opencos.commands.elab - Base class command handler for: eda elab ...

Intended to be overriden by Tool based classes (such as CommandElabVivado, etc)

Note that many 'elab' command handlers that also can perform simulations, such
as VerilatorElab, will instead inherit from VerilatorSim and simply perform a
shortened sim as the elab, instead of inheriting CommandElab.

Tools that don't support a 'sim' command will generally use CommandElab, such
as CommandElabSlang.'''

from opencos.commands.sim import CommandSim

class CommandElab(CommandSim):
    '''Base class command handler for: eda elab ...'''

    command_name = 'elab'

    def __init__(self, config: dict):
        CommandSim.__init__(self, config=config)
        # add args specific to this simulator
        self.args['stop-after-elaborate'] = True
        self.args['lint'] = True
        self.args['verilate-args'] = []



    def compile(self) -> None:
        raise NotImplementedError

    def elaborate(self) -> None:
        raise NotImplementedError

    def get_compile_command_lists(self, **kwargs) -> list:
        ''' Returns a list of lists (list of command lists).'''
        raise NotImplementedError

    def get_elaborate_command_lists(self, **kwargs) -> list:
        ''' Returns a list of lists (list of command lists).'''
        raise NotImplementedError

    # CommandSim methods that elab does not use:

    def simulate(self):
        pass

    def get_simulate_command_lists(self, **kwargs) -> list:
        return []

    def get_post_simulate_command_lists(self, **kwargs) -> list:
        return []
