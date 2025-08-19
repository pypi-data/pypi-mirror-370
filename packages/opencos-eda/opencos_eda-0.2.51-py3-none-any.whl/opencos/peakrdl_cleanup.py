#!/usr/bin/env python3

''' peakrdl_cleanup is intended as CLI or callable via run(file-in, file-out)

to apply verilator comment waivers to a SystemVerilog file
'''

import sys


def run(file_in: str, file_out: str) -> None:
    '''Returns None, writes file_out (filepath) with updates given file_in (filepath)'''

    with open(file_in, encoding='utf-8') as f:
        lines = f.readlines()

    with open(file_out, 'w', encoding='utf-8') as f:
        f.write('// verilator lint_off MULTIDRIVEN\n')
        for line in lines:
            f.write(line)
        f.write('// verilator lint_on  MULTIDRIVEN\n')


if __name__ == '__main__':
    assert len(sys.argv) == 3, f'{sys.argv=}'
    run(file_in=sys.argv[1], file_out=sys.argv[2])
