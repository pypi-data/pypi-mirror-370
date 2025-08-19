'''opencos.commands.lec - Base class command handler for: eda lec ...

Intended to be overriden by Tool based classes (such as CommandLecYosys, etc)
'''

# Note - similar code waiver, tricky to eliminate it with inheritance when
# calling reusable methods.
# pylint: disable=R0801

import os

from opencos import eda_extract_targets
from opencos.eda_base import CommandDesign, Tool


class CommandLec(CommandDesign):
    '''Base class command handler for: eda lec ...'''

    CHECK_REQUIRES = [Tool]
    error_on_no_files_or_targets = False
    error_on_missing_top = False # we'll override it.

    command_name = 'lec'

    def __init__(self, config: dict):
        CommandDesign.__init__(self, config=config)
        self.args.update({
            'designs': [],
            'synth': True,
        })
        self.args_help.update({
            'designs': (
                'Set the two LEC comparison designs: --designs=<target1> --designs=<target2>,'
                ' use this arg twice'
            ),
            'synth': 'run synthesis on the two designs prior to running LEC',
        })

        self.synth_design_verilog_fpaths = ['', '']


    def do_it(self) -> None:
        '''Common do_it() method that child classes can use prior to customization'''

        # set_tool_defines() is from class Tool. Since that is not inherited yet, but
        # should be by any handlers, check on the existence of set_tool_defines, and
        # error if not present.
        if not all(isinstance(self, x) for x in self.CHECK_REQUIRES):
            self.error('CommandLec.do_it() requires a Tool to be in parent classes, but none is.',
                       f'{self.CHECK_REQUIRES=}')
            return

        # add defines for this job from Tool class if present
        self.command_safe_set_tool_defines() # (Command.command_safe_set_tool_defines)

        # dump our config to work-dir for debug
        self.write_eda_config_and_args()

        # Note - we do not support --export in LEC.
        # Derived classes can do the rest, can call CommandLec.do_it(self) as a first step.


    def process_tokens(self, tokens: list, process_all: bool = True,
                       pwd: str = os.getcwd()) -> list:
        unparsed = CommandDesign.process_tokens(
            self, tokens=tokens, process_all=process_all, pwd=pwd
        )

        if self.status_any_error():
            return unparsed

        # we require there to be two --designs set.
        if not self.args['designs'] and len(self.args['designs']) != 2:
            self.error('Requires two designs via --designs=<target1> --designs=<target2>',
                       f'designs={self.args["designs"]}')
            return []


        # Before we do anything else, make sure the two designs actually exist.
        for design in self.args['designs']:
            # maybe it's a file?
            if os.path.isfile(design):
                pass
            elif design in eda_extract_targets.get_targets(partial_paths=[design], base_path=pwd):
                pass
            else:
                self.error(f'--designs={design}, value is not a file or target')

        if not self.args['top']:
            # Correct the 'top' name so it's eda.<target1>.<target2>.lec (shortnames)
            _, short_target1 = os.path.split(self.args['designs'][0])
            _, short_target2 = os.path.split(self.args['designs'][1])
            self.args['top'] = f'eda.{short_target1}.{short_target2}'

        # create our work dir
        self.create_work_dir()
        self.run_dep_commands()
        self.do_it()
        return unparsed


    def get_synth_result_fpath(self, target: str) -> str:
        '''Derived classes must define. Given a synth target for one of the two

        designs to compare, return the location of the synthesis file'''
        raise NotImplementedError
