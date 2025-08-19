'''__init__ acts mostly a package convenience, so that the following works:

    from opencos.commands import CommandSim

without having to know that it's in opencos.commands.sim
'''

from .build import CommandBuild
from .elab import CommandElab
from .export import CommandExport
from .flist import CommandFList
from .multi import CommandMulti, CommandToolsMulti
from .open import CommandOpen
from .proj import CommandProj
from .sim import CommandSim
from .sweep import CommandSweep
from .synth import CommandSynth
from .upload import CommandUpload
from .waves import CommandWaves
from .shell import CommandShell
from .targets import CommandTargets
from .lec import CommandLec

__all__ = [
    'CommandBuild',
    'CommandElab',
    'CommandExport',
    'CommandFList',
    'CommandMulti',
    'CommandOpen',
    'CommandProj',
    'CommandSim',
    'CommandSweep',
    'CommandSynth',
    'CommandToolsMulti',
    'CommandUpload',
    'CommandWaves',
    'CommandShell',
    'CommandTargets',
    'CommandLec',
]
