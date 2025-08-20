''' opencos.seed handles getting a 'seed' int, and keeping a list of seeds.

Used by opencos.command.sim and opencos.tools, because some tools prefer 32-bit uint,
31-bit > 0, or want to avoid a seed=0
'''

import random
import time

seeds = []

def get_seed(style: str = "", limit_31bit: bool = True, avoid_zero: bool = True) -> int:
    '''Returns a random int, using python random or time.time, with constraints.

    Appends returned value to global list seeds.

    style (str)
      -- "", default: uses python random.randint 32-bit
      -- "time"     : uses python time.time_ns() 32-bit LSBs
    '''

    seed = 1

    if style.lower() == "time":
        # use the float value fractional portion
        seed = time.time_ns() & 0xFFFF_FFFF
    else:
        seed = random.randint(0, 0xFFFF_FFFF)

    if limit_31bit:
        seed &= 0x7FFF_FFFF
    if avoid_zero and seed == 0:
        seed = 1

    seeds.append(seed)
    return seed
