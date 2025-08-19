'''opencos.commands.waves - command handler for: eda waves ...

Note this command is handled differently than others (such as CommandSim),
it is generally run as simply

    > eda waves

and attempts to auto-find the newest waveform in your work directories. As
a result, no Tool is bound to CommandWaves (there is no CommandWavesVivado
handler).
'''

# Note - similar code waiver, tricky to eliminate it with inheritance when
# calling reusable methods.
# pylint: disable=R0801

import os
import shutil

from opencos import util
from opencos.eda_base import CommandDesign


class CommandWaves(CommandDesign):
    '''command handler for: eda waves'''

    command_name = 'waves'

    SUPPORTED_WAVES_EXT = [
        '.wdb', '.vcd', '.wlf', '.fst'
    ]

    VSIM_TOOLS = set([
        'questa',
        'modelsim_ase',
    ])

    VSIM_VCD_TOOLS = set([
        'questa',
    ])

    def __init__(self, config: dict):
        CommandDesign.__init__(self, config=config)
        self.args.update({
            'test-mode': False,
        })
        self.args_help.update({
            'test-mode': 'Do not run the command to open the located wave file, instead print' \
            + ' to stdout',
        })


    def get_wave_files_in_dirs(self, wave_dirs: list, quiet: bool = False) -> list:
        '''Returns list of all wave files give wave_dirs (list)'''

        def info(*text):
            if not quiet:
                util.info(*text)

        all_files = []
        for d in wave_dirs:
            info(f"Looking for wavedumps below: {d}")
            for root, _, files in os.walk(d):
                for f in files:
                    for e in self.SUPPORTED_WAVES_EXT:
                        if f.endswith(e):
                            info(f"Found wave file: {os.path.join(root, f)}")
                            all_files.append(os.path.join(root, f))
        return all_files

    def process_tokens( # pylint: disable=too-many-branches,too-many-statements
            self, tokens: list, process_all: bool = True,
            pwd: str = os.getcwd()
    ) -> list:

        wave_file = None
        wave_dirs = []
        tokens = CommandDesign.process_tokens(self, tokens=tokens, process_all=False, pwd=pwd)

        if self.args['test-mode']:
            self.exec = self._test_mode_exec

        while tokens:
            if os.path.isfile(tokens[0]):
                if wave_file is not None:
                    self.error(f"Was already given {wave_file=}, not sure what",
                               f"to do with: {tokens[0]}")
                wave_file = os.path.abspath(tokens[0])
                tokens.pop(0)
                continue
            if os.path.isdir(tokens[0]):
                if wave_file is not None:
                    self.error(f"Was already given {wave_file=}, not sure what",
                               f"to do with {tokens[0]}")
                wave_dirs.append(tokens[0])
            self.error(f"Didn't understand command arg/token: '{tokens[0]}'",
                       "in CommandWaves")

        if not wave_file:
            util.info("need to look for wave file")
            # we weren't given a wave file, so we will look for one!
            if not wave_dirs and os.path.isdir(self.args['eda-dir']):
                wave_dirs.append(self.args['eda-dir'])
            if not wave_dirs:
                wave_dirs.append('.')
            all_files = self.get_wave_files_in_dirs(wave_dirs)
            if len(all_files) > 1:
                all_files.sort(key=os.path.getmtime)
                util.info(f"Choosing: {all_files[-1]} (newest)")
            if all_files:
                wave_file = all_files[-1]
            else:
                self.error(f"Couldn't find any wave files below: {','.join(wave_dirs)}")

        wave_file = os.path.abspath(wave_file)
        util.info(f"decided on opening: {wave_file}")

        # TODO(drew): this feels a little customized per-tool, perhaps there's a better
        # way to abstract this configuration for adding other waveform viewers.
        # For example for each command we also have to check shutil.which, because normal Tool
        # classs should work even w/out PATH, but these don't use Tool classes.
        if wave_file.endswith('.wdb'):
            if 'vivado' in self.config['tools_loaded'] and shutil.which('vivado'):
                tcl_name = wave_file + '.waves.tcl'
                with open( tcl_name, 'w', encoding='utf-8') as fo :
                    print( 'current_fileset', file=fo)
                    print( f'open_wave_database {wave_file}', file=fo)
                command_list = [ 'vivado', '-source', tcl_name]
                self.exec(os.path.dirname(wave_file), command_list)
            else:
                self.error(f"Don't know how to open {wave_file} without Vivado in PATH")
        elif wave_file.endswith('.wlf'):
            if self._vsim_available():
                command_list = ['vsim', wave_file]
                self.exec(os.path.dirname(wave_file), command_list)
            else:
                self.error(f"Don't know how to open {wave_file} without one of",
                           f"{self.VSIM_TOOLS} in PATH")
        elif wave_file.endswith('.fst'):
            if 'gtkwave' in self.config['tools_loaded'] and shutil.which('gtkwave'):
                command_list = ['gtkwave', wave_file]
                self.exec(os.path.dirname(wave_file), command_list)
            else:
                self.error(f"Don't know how to open {wave_file} without GtkWave in PATH")
        elif wave_file.endswith('.vcd'):
            if 'gtkwave' in self.config['tools_loaded'] and shutil.which('gtkwave'):
                command_list = ['gtkwave', wave_file]
                self.exec(os.path.dirname(wave_file), command_list)
            elif self._vsim_available(from_tools=self.VSIM_VCD_TOOLS):
                # TODO(drew): untested, may not work, may need to use fst2vcd converter first
                # (from gtkwave install)
                command_list = ['vsim', wave_file]
                self.exec(os.path.dirname(wave_file), command_list)
            else:
                self.error(f"Don't know how to open {wave_file} without Vivado,",
                           f"gtkwave, or {self.VSIM_VCD_TOOLS} in PATH")

        return tokens

    def _vsim_available( # pylint: disable=dangerous-default-value
            self, from_tools: list = VSIM_TOOLS
    ) -> bool:
        '''Returns True if 'vsim' is available (Questa or Modelsim)'''
        return bool(shutil.which('vsim')) and \
            any(x in self.config['tools_loaded'] for x in from_tools)


    def _test_mode_exec( # pylint: disable=unused-argument
            self, work_dir: str,
            command_list: list,
            **kwargs
    ) -> None:
        '''Override for Command.exec if arg --test-mode was set, does not run

        the command_list, instead prints to stdout'''

        util.info(f'waves.py: test_mode exec stdout: {" ".join(command_list)};',
                  f'   ({work_dir=}')
