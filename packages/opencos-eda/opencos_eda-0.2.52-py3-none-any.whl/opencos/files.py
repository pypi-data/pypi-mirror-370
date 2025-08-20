'''Helper for adding source files:

Allows user to explicitly add systemverilog files that don't end in .sv using

sv@my_module.txt
v@my_verilog_module.txt
vhdl@my_vhdl_code.log

Otherwise eda.py can't know if a .txt (or .pcap, etc) file is a source file
to be part of compilation, or a file needed for simulation (.txt, .pcap, .mem
as part of a verilog $readmemh, etc)

'''

import os

# Ways to force files not ending in .sv to be systemverilog (for tools
# that require -sv vs Verilog-2001'''
FORCE_PREFIX_DICT = {
    # The values must match what's expected by eda.CommandDesign.add_file,
    # which are named in eda_config_defaults.yml - file_extensions:
    'sv@': 'systemverilog',
    'v@': 'verilog',
    'vhdl@': 'vhdl',
    'cpp@': 'cpp',
    'sdc@': 'synth_constraints',
}

ALL_FORCED_PREFIXES = set(list(FORCE_PREFIX_DICT.keys()))

def get_source_file(target:str) -> (bool, str, str):
    '''Returns tuple: bool if file exists, filepath str, and optional forced file type str'''
    if os.path.isfile(target):
        # target exists as a file, return True w/ original target:
        return True, target, ''

    if '@' in target:
        for p in ALL_FORCED_PREFIXES:
            if p in target:
                # essentially removing the leading "sv@" or whatever prefix.
                fpath = ''.join(target.split(p))
                if os.path.isfile(fpath):
                    return True, fpath, FORCE_PREFIX_DICT.get(p)

    # target or fpath didn't exist, return False with the original target:
    return False, target, ''
