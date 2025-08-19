'''opencos.eda_base holds base classes for opencos.tools and opencos.commands

Note that opencos.Command.process_tokens (on a derived class) is the main entrypoint
from eda.py, it will find a command handler class for a command + tool, and call
its obj.process_tokens(args)
'''

# TODO(drew): Clean up the following pylint
# pylint: disable=too-many-lines

import argparse
import copy
import subprocess
import os
import queue
import re
import shutil
import signal
import sys
import threading
import time
from pathlib import Path

from opencos import seed, util, files
from opencos import eda_config

from opencos.util import Colors
from opencos.utils.str_helpers import sprint_time, strip_outer_quotes, string_or_space, \
    indent_wrap_long_text
from opencos.utils.subprocess_helpers import subprocess_run_background
from opencos.utils import status_constants

from opencos.deps.deps_file import DepsFile, deps_data_get_all_targets
from opencos.deps.deps_processor import DepsProcessor


def print_base_help() -> None:
    '''Prints help() information from other argparsers we use, without "usage"'''
    # using bare 'print' here, since help was requested, avoids --color and --quiet
    print(util.get_argparser_short_help())
    print(eda_config.get_argparser_short_help())
    print(get_argparser_short_help())


def get_argparser() -> argparse.ArgumentParser:
    '''Returns the ArgumentParser for general eda CLI'''
    parser = argparse.ArgumentParser(prog='eda options', add_help=False, allow_abbrev=False)
    parser.add_argument('-q', '--quit', action='store_true',
                        help=(
                            'For interactive mode (eda called with no options, command, or'
                            ' targets)'))
    parser.add_argument('--exit', action='store_true', help='same as --quit')
    parser.add_argument('-h', '--help', action='store_true')

    # Note - these top level eda.py args, that aren't from eda_config.py or util.py, need to
    # be fed back into CommandMulti or CommandSweep, since they re-invoke eda.
    parser.add_argument('--tool', type=str, default=None,
                        help='Tool to use for this command, such as: modelsim_ase, verilator,' \
                        + ' modelsim_ase=/path/to/bin/vsim, verilator=/path/to/bin/verilator')
    parser.add_argument('--eda-safe', action='store_true',
                        help=('disable all DEPS file deps shell commands, overrides values from'
                              ' --config-yml'))
    return parser


def get_argparser_short_help() -> str:
    '''Returns str for the eda_base argparser (--help, --tool, etc)'''
    return util.get_argparser_short_help(parser=get_argparser())


def get_eda_exec(command: str = '') -> str:
    '''Returns the full path of `eda` executable to be used for a given eda <command>'''
    # NOTE(drew): This is kind of flaky. 'eda multi' reinvokes 'eda'. But the executable for 'eda'
    # is one of:
    # 1. pip3 install opencos-eda
    #    -- script 'eda', installed from PyPi
    # 2. pip3 uninstall .; python3 -m build; pip3 install
    #    -- script 'eda' but installed from local.
    # 2. (opencos repo)/bin/eda - a python wrapper to link to (opencos repo)/opencos/eda.py, but
    #    packages cannot be run standalone, they need to be called as: python3 -m opencos.eda,
    #    and do not work with relative paths. This only works if env OC_ROOT is set or can be found.
    # 3. If you ran 'source bin/addpath' then you are always using the local (opencos repo)/bin/eda
    eda_path = shutil.which('eda')
    if not eda_path:
        # Can we run from OC_ROOT/bin/eda?
        oc_root = util.get_oc_root()
        if not oc_root:
            util.error(f"Need 'eda' in our path to run 'eda {command}', could not find env",
                       f"OC_ROOT, {eda_path=}, {oc_root=}")
        else:
            bin_eda = os.path.join(oc_root, 'bin', 'eda')
            if not os.path.exists(bin_eda):
                util.error(f"Need 'eda' in our path to run 'eda {command}', cound not find",
                           f"bin/, {eda_path=}, {oc_root=}, {bin_eda=}")
            else:
                util.info(f"'eda' not in path, using {bin_eda=} for 'eda' {command} executable")
                eda_path = os.path.abspath(bin_eda)

    return eda_path


def which_tool(command: str, config: dict) -> str:
    '''Returns which tool (str) will be used for a command, given the command_handlers in

    config dict.'''
    if config is None:
        util.error(f'which_tool({command=}) called w/out config')
    if not command in config.get('command_handler', {}):
        util.error("which_tool called with invalid command?")

    # Note: we could create a throw-away Command object using config, and check its
    # args['tool']:
    #    cmd_obj = config['command_handler'][command](config=config)
    #    return cmd_obj.args.get('tool', None)
    # But that has side effects and prints a lot of garbage, and does a lot
    # of loading and setting values to create that throw away Command object.

    # Instead, we'll directly look up at the class _TOOL w/out creating the obj.
    tool = getattr(config['command_handler'][command], '_TOOL', None)
    return tool


class Tool:
    '''opencos.eda_base.Tool is a base class used by opencos.tools.<name>.

    If you do not have a config (dict) for the contructor, please use Tool(config={})'''

    error = util.error # use that module's method
    _TOOL = '' # this is the only place a class._TOOL should be set to non-empty str
    _URL = None
    _EXE = None

    def __init__(self, config: dict):
        # Because Command child classes (CommandSimVerilator, for example), will
        # inherit both Command and Tool classes, we'd like them to reference
        # a Command object's self.args instead of the class Tool.args. Safely create it
        # if it doesn't exist:
        self._VERSION = None
        if getattr(self, 'args', None) is None:
            self.args = {}
        if getattr(self, 'args_help', None) is None:
            self.args_help = {}
        if getattr(self, 'defines', None) is None:
            self.defines = {}
        self.args.update({
            'tool':   self._TOOL, # Set for all derived classes.
        })
        self.args_help.update({
            'tool': 'Tool to use for this command, such as: verilator',
        })
        # update self._EXE if config says to:
        self.set_exe(config)
        self.get_versions()

        if getattr(self, 'set_tool_config_from_config', None):
            # Hook for classes like CommandSim that have a Tool derived class attached:
            # have the Tool constructor run set_tool_config_from_config(), otherwise
            # every derived class will have to do this.
            # Allows command handlers to make thier own customizations from --config-yaml=YAML.
            self.set_tool_config_from_config()

    def set_exe(self, config: dict) -> None:
        '''Sets self._EXE based on config'''
        if self._TOOL and self._TOOL in config.get('auto_tools_order', [{}])[0]:
            exe = config.get('auto_tools_order', [{}])[0][self._TOOL].get('exe', '')
            if exe and isinstance(exe, list):
                exe = exe[0] # pick first
            if exe and exe != self._EXE:
                util.info(f'Override for {self._TOOL} using exe {exe}')
                self._EXE = exe

    def get_full_tool_and_versions(self) -> str:
        '''Returns tool:version, such as: verilator:5.033'''
        if not self._VERSION:
            self.get_versions()
        return str(self._TOOL) + ':' + str(self._VERSION)

    def get_versions(self) -> str:
        '''Sets and returns self._VERSION'''
        return self._VERSION

    def set_tool_defines(self) -> None:
        '''Derived classes may override, sets any additional defines based on tool.'''
        return


class Command:
    '''Base class for all: eda <command>

    The Command class should be used when you don't require files, otherwise consider
    CommandDesign.
    '''

    command_name: str = ''

    def __init__(self, config:dict):
        if getattr(self, 'args', None) is None:
            self.args = {}
        if getattr(self, 'args_help', None) is None:
            self.args_help = {}
        self.args.update({
            "keep" : False,
            "force" : False,
            "fake" : False,
            "stop-before-compile": False,
            "stop-after-compile": False,
            "stop-after-elaborate": False,
            "lint": False, # Same as stop-after-elaborate
            "eda-dir" : "eda.work", # all eda jobs go in here
            "job-name" : "", # this is used to create a certain dir under "eda_dir"
            "work-dir" : "", # default is usually <eda-dir>/<job-name> or <eda-dir>/<target>.<cmd>
            "sub-work-dir" : "", # this can be used to name the dir built under <eda-dir>
            "work-dir-use-target-dir": False,
            "suffix" : "",
            "design" : "", # not sure how this relates to top
            'export':     False,
            'export-run': False,  # run from the exported location if possible
            'export-json': False, # generates an export.json suitable for a testrunner
            'enable-tags': [],
            'disable-tags': [],
            'test-mode': False,
        })
        self.args_help.update({
            'stop-before-compile': ('stop this run before any compile (if possible for tool) and'
                                    ' save .sh scripts in eda-dir/'),
            'eda-dir':     'relative directory where eda logs are saved',
            'export':      'export results for these targets in eda-dir',
            'export-run':  'export, and run, results for these targets in eda-dir',
            'export-json': 'export, and save a JSON file per target',
            'work-dir':    ('Optional override for working directory, often defaults to'
                            ' ./eda.work/<top>.<command>'),
            "work-dir-use-target-dir": ('Set the work-dir to be the same as the in-place location'
                                       ' where the target (DEPS) exists'),
            'enable-tags': ('DEPS markup tag names to be force enabled for this'
                            ' command (mulitple appends to list).'),
            'diable-tags': ('DEPS markup tag names to be disabled (even if they'
                            ' match the criteria) for this command (mulitple appends to list).'
                            ' --disable-tags has higher precedence than --enable-tags.'),
            'test-mode': ('command and tool dependent, usually stops the command early without'
                          ' executing.'),
        })
        self.modified_args = {}
        self.config = copy.deepcopy(config) # avoid external modifications.
        self.target = ""
        self.target_path = ""
        self.status = 0
        self.errors_log_f = None


    def error(self, *args, **kwargs) -> None:
        '''Returns None, child classes can call self.error(..) instead of util.error,

        which updates their self.status. Also will write out to eda.errors.log if the work-dir
        exists. Please consider using Command.error(..) (or self.error(..)) in place of util.error
        so self.status is updated.
        '''

        if self.args['work-dir']:
            if not self.errors_log_f:
                try:
                    fullpath = os.path.join(self.args['work-dir'], 'eda.errors.log')
                    self.errors_log_f = open( # pylint: disable=consider-using-with
                        fullpath, 'w', encoding='utf-8'
                    )
                    util.artifacts.add(
                        name=fullpath,
                        typ='text', description='EDA reported errors'
                    )

                except FileNotFoundError:
                    pass
            if self.errors_log_f:
                print(
                    f'ERROR: [eda] ({self.command_name}) {" ".join(list(args))}',
                    file=self.errors_log_f
                )

        self.status = util.error(*args, **kwargs) # error_code passed and returned via kwargs

    def status_any_error(self, report=True) -> bool:
        '''Used by derived classes process_tokens() to know an error was reached
        and to not perform the command. Necessary for pytests that use eda.main()'''
        if report and self.status > 0:
            util.error(f"command '{self.command_name}' has previous errors")
        return self.status > 0

    def which_tool(self, command:str) -> str:
        '''Returns a str for the tool name used for the requested command'''
        return which_tool(command, config=self.config)

    def create_work_dir( # pylint: disable=too-many-branches,too-many-statements
            self
    ) -> str:
        '''Creates the working directory and populates self.args['work-dir']

        Generally uses ./ self.args['eda-dir'] / <target-name>.<command> /
        however, self.args['job-name'] or ['sub-work-dir'] can override that.

        Additionally, the work-dir is attempted to be deleted if it already exists
        AND it is beneath the caller's original working directory. We also will
        not delete 'work-dir' that is ./ or $PWD.
        '''
        util.debug(f"create_work_dir: {self.args['eda-dir']=} {self.args['work-dir']=}")
        if self.args['work-dir-use-target-dir']:
            if not self.target_path:
                self.target_path = '.'
            util.info("create_work_dir: --work-dir-use-target-dir: using:",
                      f"{os.path.abspath(self.target_path)}",
                      f'target={self.target}')
            self.args['work-dir'] = self.target_path
            self.args['sub-work-dir'] = ''
            return self.args['work-dir']

        if not os.path.exists(self.args['eda-dir']):
            util.safe_mkdir(self.args['eda-dir'])
            util.info(f"create_work_dir: created {self.args['eda-dir']}")

        if self.args['design'] == "":
            if ('top' in self.args) and (self.args['top'] != ""):
                self.args['design'] = self.args['top']
                util.debug(f"create_work_dir: set {self.args['design']=} from",
                           f"{self.args['top']=}, since it was empty")
            else:
                self.args['design'] = "design" # generic, i.e. to create work dir "design_upload"
                util.debug(f"create_work_dir: set {self.args['design']=} to 'design', since it",
                           "was empty and we have no top")

        if self.target == "":
            self.target = self.args['design']
            util.debug(f"create_work_dir: set {self.target=} from design name, since it was empty")

        if self.args['work-dir'] == '':
            if self.args['sub-work-dir'] == '':
                if self.args['job-name'] != '':
                    self.args['sub-work-dir'] = self.args['job-name']
                    util.debug(f"create_work_dir: set {self.args['sub-work-dir']=} from",
                               f"{self.args['job-name']=}, since it was empty")
                else:
                    self.args['sub-work-dir'] = f'{self.target}.{self.command_name}'
                    util.debug(f"create_work_dir: set {self.args['sub-work-dir']=} from",
                               f"{self.target=} and {self.command_name=}, since it was empty and",
                               "we have no job-name")
            self.args['work-dir'] = os.path.join(self.args['eda-dir'], self.args['sub-work-dir'])
            util.debug(f"create_work_dir: set {self.args['work-dir']=}")

        keep_file = os.path.join(self.args['work-dir'], "eda.keep")
        if os.path.exists(self.args['work-dir']):
            if os.path.exists(keep_file) and not self.args['force']:
                self.error(f"Cannot remove old work dir due to '{keep_file}'")
            elif os.path.abspath(self.args['work-dir']) in os.getcwd():
                # This effectively checks if
                # --work-dir=.
                # --work-dir=$PWD
                # --work-dir=/some/path/almost/here
                # Allow it, but preserve the existing directory, we don't want to blow away
                # files up-hier from us.
                # Enables support for --work-dir=.
                util.info(f"Not removing existing work-dir: '{self.args['work-dir']}' is within",
                          f"{os.getcwd()=}")
            elif str(Path(self.args['work-dir'])).startswith(str(Path('/'))):
                # Do not allow other absolute path work dirs if it already exists.
                # This prevents you from --work-dir=~ and eda wipes out your home dir.
                self.error(f'Cannot use work-dir={self.args["work-dir"]} starting with',
                           'fabsolute path "/"')
            elif str(Path('..')) in str(Path(self.args['work-dir'])):
                # Do not allow other ../ work dirs if it already exists.
                self.error(f'Cannot use work-dir={self.args["work-dir"]} with up-hierarchy'
                           '../ paths')
            else:
                # If we made it this far, on a directory that exists, that appears safe
                # to delete and re-create:
                util.info(f"Removing previous '{self.args['work-dir']}'")
                shutil.rmtree(self.args['work-dir'])
                util.safe_mkdir(self.args['work-dir'])
                util.debug(f'create_work_dir: created {self.args["work-dir"]}')
        else:
            util.safe_mkdir(self.args['work-dir'])
            util.debug(f'create_work_dir: created {self.args["work-dir"]}')

        if self.args['keep']:
            open(keep_file, 'w', encoding='utf-8').close() # pylint: disable=consider-using-with
            util.debug(f'create_work_dir: created {keep_file=}')

        # Set the util.artifacts path with our work-dir:
        util.artifacts.set_artifacts_json_dir(self.args['work-dir'])

        return self.args['work-dir']

    def artifacts_add(self, name: str, typ: str, description: str) -> None:
        '''Adds a file to util.artifacts, derived classes may override'''
        util.artifacts.add(name=name, typ=typ, description=description)


    def exec(self, work_dir: str, command_list: list, background: bool = False,
             stop_on_error: bool = True, quiet: bool = False, tee_fpath: str = '',
             shell: bool = False) -> (str, str, int):
        '''Runs a command via subprocess and returns a tuple of (stderr, stdout, rc)

        - work_dir: is passed to the subprocess call, so os.chdir(..) is not invoked.
        - command_list: should be a list of individual strings w/out spaces.
        - background: if False, does not print to stdout (but will print to any
                      tee_fpath or the global log
        - shell: arg passed to subprocess, defaults to False.
        '''

        if not tee_fpath and getattr(command_list, 'tee_fpath', None):
            tee_fpath = getattr(command_list, 'tee_fpath', '')
        if not quiet:
            util.info(f"exec: {' '.join(command_list)} (in {work_dir}, {tee_fpath=})")

        stdout, stderr, return_code = subprocess_run_background(
            work_dir=work_dir,
            command_list=command_list,
            background=background,
            fake=self.args.get('fake', False),
            tee_fpath=tee_fpath,
            shell=shell
        )

        if return_code > 0:
            if return_code == 1:
                self.status = status_constants.EDA_EXEC_NONZERO_RETURN_CODE1
            if return_code == 255:
                self.status = status_constants.EDA_EXEC_NONZERO_RETURN_CODE255
            else:
                self.status = status_constants.EDA_EXEC_NONZERO_RETURN_CODE2
            if stop_on_error:
                self.error(f"exec: returned with error (return code: {return_code})",
                           error_code=self.status)
            else:
                util.debug(f"exec: returned with error (return code: {return_code})")
        else:
            util.debug(f"exec: returned without error (return code: {return_code})")
        return stderr, stdout, return_code

    def set_arg( # pylint: disable=too-many-branches
            self, key, value
    ) -> None:
        '''Sets self.args[key] with value, and self.modified_args[key]=True

        Does type checking, handles list type append
        '''

        # Do some minimal type handling, preserving the type(self.args[key])
        if key not in self.args:
            self.error(f'set_arg, {key=} not in self.args {value=}',
                       f'({self.command_name=}, {self.__class__.__name__=})',
                       error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)

        cur_value = self.args[key]

        if isinstance(cur_value, dict):
            # if dict, update
            self.args[key].update(value)

        elif isinstance(cur_value, list):
            # if list, append (no duplicates)
            if isinstance(value, list):
                # new value also a list
                for x in value:
                    if x not in self.args[key]:
                        self.args[key].append(x)
            elif value not in cur_value:
                self.args[key].append(value)

        elif isinstance(cur_value, bool):
            # if bool, then attempt to convert new value string or int --> bool
            if isinstance(value, (bool, int)):
                self.args[key] = bool(value)
            elif isinstance(value, str):
                if value.lower() in ['false', '0']:
                    self.args[key] = False
                else:
                    self.args[key] = True
            else:
                assert False, f'set_arg({key=}, {value=}) bool {type(cur_value)=} {type(value)=}'

        elif isinstance(cur_value, int):
            # if int, attempt to convert string or bool --> int
            if isinstance(value, (bool, int, str)):
                self.args[key] = int(value)
            else:
                assert False, f'set_arg({key=}, {value=}) int {type(cur_value)=} {type(value)=}'


        else:
            # else overwrite it as-is.
            self.args[key] = value

        self.modified_args[key] = True
        util.debug(f'Set arg["{key}"]="{self.args[key]}"')


    def get_argparser( # pylint: disable=too-many-branches
            self, parser_arg_list=None
    ) -> argparse.ArgumentParser:
        ''' Returns an argparse.ArgumentParser() based on self.args (dict)

        If parser_arg_list is not None, the ArgumentParser() is created using only the keys in
        self.args provided by the list parser_arg_list.
        '''

        # Preference is --args-with-dashes, which then become parsed.args_with_dashes, b/c
        # parsed.args-with-dashes is not legal python. Some of self.args.keys() still have - or _,
        # so this will handle both.
        # Also, preference is for self.args.keys(), to be str with - dashes
        parser = argparse.ArgumentParser(prog='eda', add_help=False, allow_abbrev=False)
        bool_action_kwargs = util.get_argparse_bool_action_kwargs()

        if not parser_arg_list:
            args = self.args
        else:
            args = {key: self.args[key] for key in parser_arg_list}

        for key,value in args.items():
            if '_' in key and '-' in key:
                assert False, f'{args=} has {key=} with both _ and -, which is not allowed'
            if '_' in key:
                util.warning(f'{key=} has _ chars, prefer -')

            keys = [key] # make a list
            if '_' in key:
                keys.append(key.replace('_', '-')) # switch to POSIX dashes for argparse
            elif '-' in key:
                keys.append(key.replace('-', '_')) # also support --some_arg_with_underscores

            arguments = [] # list supplied to parser.add_argument(..) so one liner supports both.
            for this_key in keys:
                arguments.append(f'--{this_key}')

            if self.args_help.get(key, ''):
                help_kwargs = {'help': self.args_help[key] + f' (default={value})'}
            elif value is None:
                help_kwargs = {'help': f'default={value}'}
            else:
                help_kwargs = {'help': f'{type(value).__name__} default={value}'}


            # It's important to set the default=None on these, except for list types where default
            # is []. If the parsed Namespace has values set to None or [], we do not update. This
            # means that as deps are processed that have args set, they cannot override the top
            # level args that were already set, nor be overriden by defaults.
            if isinstance(value, bool):
                # For bool, support --key and --no-key with action=argparse.BooleanOptionalAction.
                # Note, this means you cannot use --some-bool=True, or --some-bool=False, has to
                # be --some-bool or --no-some-bool.
                parser.add_argument(
                    *arguments, default=None, **bool_action_kwargs, **help_kwargs)
            elif isinstance(value, list):
                parser.add_argument(*arguments, default=value, action='append', **help_kwargs)
            elif isinstance(value, (int, str)):
                parser.add_argument(*arguments, default=value, type=type(value), **help_kwargs)
            elif value is None:
                parser.add_argument(*arguments, default=None, **help_kwargs)
            else:
                assert False, f'{key=} {value=} how do we do argparse for this type of value?'

        return parser


    def run_argparser_on_list(
            self, tokens: list, parser_arg_list=None, apply_parsed_args: bool = True
    ) -> (dict, list):
        ''' Creates an argparse.ArgumentParser() for all the keys in self.args, and attempts to
        parse from the provided list. Parsed args are applied to self.args.

        Returns a tuple of (parsed argparse.Namespace obj, list of unparsed args)

        If parser_arg_list is not None, the ArgumentParser() is created using only the keys in
        self.args provided by the list parser_arg_list.
        If apply_parsed_args=False, the parsed args were not applied.
        '''

        parser = self.get_argparser(parser_arg_list=parser_arg_list)
        try:
            parsed, unparsed = parser.parse_known_args(tokens + [''])
            unparsed = list(filter(None, unparsed))
        except argparse.ArgumentError:
            self.error(f'problem {self.command_name=} attempting to parse_known_args for {tokens=}',
                       error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)

        parsed_as_dict = vars(parsed)

        args_to_be_applied = {}

        for key, value in parsed_as_dict.items():
            # key currently has _ instead of POSIX dashes, so we convert to dashes, for
            # most self.args, like self.args['build-file'], etc.
            if key not in self.args and '_' in key:
                key = key.replace('_', '-')
            assert key in self.args, f'{key=} not in {self.args=}'

            args_to_be_applied[key] = value

        if apply_parsed_args:
            self.apply_args_from_dict(args_to_be_applied)

        return parsed, unparsed


    def apply_args_from_dict(self, args_to_be_applied: dict) -> list:
        '''Given a dict of key/value for self.args, apply them to self.args'''
        util.debug('apply_args_from_dict() -- called by:',
                   f'{self.command_name=}, {self.__class__.__name__=},',
                   f'{args_to_be_applied=}')
        for key, value in args_to_be_applied.items():

            if value is None:
                continue # don't update a self.args[key] to None
            if isinstance(value, list) and len(value) == 0:
                continue # don't update a self.args[key] that's a list --> to an empty list.
            if not isinstance(value, list) and self.args[key] == value:
                continue # don't update non list if the value already matches.
            if not isinstance(value, list) and self.modified_args.get(key, None):
                # For list types, we append. For all others they overwrite, so if we've already
                # modified the arg once, do not modify it again. Such as, command line set an arg,
                # but then a target tried to set it again; or a target set it, and then a dependent
                # target tried to set it again.
                util.warning(f"Command.run_argparser_on_list ({self.command_name}) -",
                             f"skipping {key=} {value=} b/c arg is already modified",
                             f"with different cur value (cur value={self.args.get(key, None)})")
                continue
            if self.args[key] != value:
                util.debug("Command.run_argparser_on_list - setting set_arg b/c",
                           f" argparse -- {key=} {value=} (cur value={self.args[key]})")
                self.set_arg(key, value) # Note this has special handling for lists already.
                self.modified_args[key] = True


    def process_tokens(self, tokens: list, process_all: bool = True,
                       pwd: str = os.getcwd()) -> list:
        '''Command.process_tokens(..) for all named self.args.keys() returns the
        unparsed tokens list

        Derived classes do not need to return a list of unparsed args, nor
        return self.status
        '''

        _, unparsed = self.run_argparser_on_list(tokens)
        if process_all and len(unparsed) > 0:
            self.error(f"Didn't understand argument: '{unparsed=}' in",
                       f" {self.command_name=} context, {pwd=}",
                       error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)

        return unparsed

    def get_command_from_unparsed_args(
            self, tokens: list, error_if_no_command: bool = True
    ) -> str:
        '''Given a list of unparsed args, try to fish out the eda <command> value.

        This will remove the value from the tokens list.
        '''
        ret = ''
        for value in tokens:
            if value in self.config['command_handler'].keys():
                ret = value
                tokens.remove(value)
                break

        if not ret and error_if_no_command:
            self.error(f"Looking for a valid eda {self.command_name} <command>",
                       f"but didn't find one in {tokens=}",
                       error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)
        return ret



    def set_tool_config_from_config(self) -> None:
        '''Returns None. Hook for classes like CommandSim that have a Tool derived class attached.

        Have the Tool constructor run set_tool_config_from_config() if it exists, otherwise every
        derived class will have to call this (error-prone if the omit it but needed it).

        Allows command handlers to make thier own customizations from --config-yaml=YAML.
        '''
        return

    def update_tool_config(self) -> None:
        '''Returns None. Hook for classes like CommandSim to make tool specific overrides.'''
        return

    def write_eda_config_and_args(self):
        '''Attempts to write eda_output_config.yml to our work-dir'''
        if not self.args.get('work-dir', None):
            util.warning(f'Ouput work-dir not set, saving ouput eda_config to {os.getcwd()}')
        eda_config.write_eda_config_and_args(
            dirpath=self.args.get('work-dir', os.getcwd()), command_obj_ref=self
        )

    def is_export_enabled(self) -> bool:
        '''Returns True if any self.args['export'] is set in any way (but not set to False
        or empty list)'''
        return any(arg.startswith('export') and v for arg,v in self.args.items())

    def run(self) -> None:
        '''Alias for do_it(self)'''
        self.do_it()

    def do_it(self) -> None:
        '''Main entrypoint of running a command, usually called by process_tokens.

        process_tokens(..) is the starting entrypoint from eda.py'''
        self.write_eda_config_and_args()
        self.error(f"No tool bound to command '{self.command_name}', you",
                   " probably need to setup tool, or use '--tool <name>'",
                   error_code=status_constants.EDA_CONFIG_ERROR)

    def command_safe_set_tool_defines(self) -> None:
        '''Safe wrapper for calling self.set_tool_defines() in case a Tool parent class is

        not yet present. If you have Tool parent, you can instead simply call:
           self.set_tool_defines()
        '''
        set_tool_defines = getattr(self, 'set_tool_defines', None)
        if set_tool_defines and callable(set_tool_defines):
            self.set_tool_defines()


    def help( # pylint: disable=dangerous-default-value,too-many-branches
            self, tokens: list = []
    ) -> None:
        '''Since we don't quite follow standard argparger help()/usage(), we'll format our own

        if self.args_help has additional help information.
        '''

        # Indent long lines (>100) to indent=56 (this is where we leave off w/ {vstr:12} below.
        def indent_me(text:str):
            return indent_wrap_long_text(text, width=100, indent=56)

        util.info('Help:')
        # using bare 'print' here, since help was requested, avoids --color and --quiet
        print()
        print('Usage:')
        print(f'    eda [options] {self.command_name} [options] [files|targets, ...]')
        print()

        print_base_help()
        lines = []
        if not self.args:
            print(f'Unparsed args: {tokens}')
            return

        if self.command_name:
            lines.append(f"Generic help for command='{self.command_name}'"
                         f" (using '{self.__class__.__name__}')")
        else:
            lines.append("Generic help (from class Command):")

        # Attempt to run argparser on args, but don't error if it fails.
        unparsed = []
        if tokens:
            try:
                _, unparsed = self.run_argparser_on_list(tokens=tokens)
            except Exception:
                pass

        for k in sorted(self.args.keys()):
            v = self.args[k]
            vstr = str(v)
            khelp = self.args_help.get(k, '')
            if khelp:
                khelp = f'  - {khelp}'
            if isinstance(v, bool):
                lines.append(indent_me(f"  --{k:20} : boolean    : {vstr:12}{khelp}"))
            elif isinstance(v, int):
                lines.append(indent_me(f"  --{k:20} : integer    : {vstr:12}{khelp}"))
            elif isinstance(v, list):
                lines.append(indent_me(f"  --{k:20} : list       : {vstr:12}{khelp}"))
            elif isinstance(v, str):
                vstr = "'" + v + "'"
                lines.append(indent_me(f"  --{k:20} : string     : {vstr:12}{khelp}"))
            else:
                lines.append(indent_me(f"  --{k:20} : <unknown>  : {vstr:12}{khelp}"))
        lines.append('')
        for line in lines:
            print(line)

        if unparsed:
            print(f'Unparsed args: {unparsed}')


class CommandDesign(Command): # pylint: disable=too-many-instance-attributes
    '''CommandDesign is the eda base class for command handlers that need to track files.

    This is the base class for CommandSim, CommandSynth, and others.'''

    # Used by for DEPS work_dir_add_srcs@ commands, by class methods:
    #   update_file_lists_for_work_dir(..), and resolve_target(..)
    _work_dir_add_srcs_path_string = '@EDA-WORK_DIR@'

    # Optionally error in self.process_tokens, derived classes can override.
    error_on_no_files_or_targets = False
    error_on_missing_top = False

    def __init__(self, config: dict):
        Command.__init__(self, config=config)
        self.args.update({
            'seed': seed.get_seed(style="urandom"),
            'top': '',
            'all-sv': True,
            'unprocessed-plusargs': [],
        })
        self.args_help.update({
            'seed':   'design seed, default is 31-bit non-zero urandom',
            'top':    'TOP level verilog/SV module or VHDL entity for this target',
            'all-sv': (
                'Maintain .sv and .v in single file list.'
                ' False: .sv flist separate from .v flist and separate compile(s)'
                ' True: .sv and .v files compiled together if possible'
            ),
            'unprocessed-plusargs': (
                'Args that began with +, but were not +define+ or +incdir+, +<name>, '
                ' or +<name>=<value>. These become tool dependent, for example "sim" commands will'
                ' treat as sim-plusargs'
            ),
        })
        self.defines = {}
        self.incdirs = []
        self.files = {}
        self.files_v = []
        self.files_sv = []
        self.files_vhd = []
        self.files_cpp = []
        self.files_sdc = []
        self.files_non_source = []
        self.files_caller_info = {}
        self.dep_shell_commands = [] # each list entry is a {}
        self.dep_work_dir_add_srcs = set() # key: tuple (target_path, target_node, filename)
        self.oc_root = util.get_oc_root()
        for (d,v) in self.config.get('defines', {}).items():
            self.defines[d] = v

        # cached_deps: key = abspath of DEPS markup file, value is a dict with
        # keys 'data' and 'line_numbers'
        self.cached_deps = {}
        self.targets_dict = {} # key = targets that we've already processed in DEPS files
        self.last_added_source_file_inferred_top = ''


    def run_dep_commands(self) -> None:
        '''Run shell/peakrdl style commands from DEPS files

        These are deferred to maintain the deps ordering, and run in that order.
        '''
        self.run_dep_shell_commands()
        # Update any work_dir_add_srcs@ in our self.files, self.files_v, etc, b/c
        # self.args['work-dir'] now exists.
        self.update_file_lists_for_work_dir()
        # Link any non-sources to our work-dir:
        self.update_non_source_files_in_work_dir()


    def run_dep_shell_commands(self) -> None:
        '''Specifically runs shell command from DEPS files'''

        # Runs from self.args['work-dir']
        all_cmds_lists = []

        log_fnames_count = {} # count per target_node.

        for i, d in enumerate(self.dep_shell_commands):
            clist = util.ShellCommandList(d['exec_list'])
            run_from_work_dir = d['run_from_work_dir'] # default True
            log = clist.tee_fpath
            target_node = d["target_node"]
            if clist.tee_fpath is None:
                lognum = log_fnames_count.get(target_node, 0)
                log = f'{target_node}__shell_{lognum}.log' # auto log every shell command.
                clist.tee_fpath = log
                # In case some single target has N shell commands, give them unique log names.
                log_fnames_count.update({target_node: lognum + 1})
            all_cmds_lists += [
                [], # blank line
                # comment, where it came from, log to {node}__shell_{lognum}.log
                # (or tee name from DEPS.yml)
                [f'# command {i}: target: {d["target_path"]} : {target_node} --> {log}'],
            ]
            if not run_from_work_dir:
                all_cmds_lists.append([f'cd {d["target_path"]}'])

            # actual command (list or util.ShellCommandList)
            all_cmds_lists.append(clist)

            if not run_from_work_dir:
                all_cmds_lists.append([f'cd {os.path.abspath(self.args["work-dir"])}'])

            d['exec_list'] = clist # update to tee_fpath is set.

        util.write_shell_command_file(
            dirpath=self.args['work-dir'], filename='pre_compile_dep_shell_commands.sh',
            command_lists=all_cmds_lists
        )

        for i, d in enumerate(self.dep_shell_commands):
            util.info(f'run_dep_shell_commands {i=}: {d=}')
            clist = util.ShellCommandList(d['exec_list'])
            tee_fpath=clist.tee_fpath
            if d['run_from_work_dir']:
                run_from_dir = self.args['work-dir']
            else:
                # Run from the target's directory (not the `eda` caller $PWD)
                run_from_dir = d["target_path"]
                tee_fpath = os.path.abspath(os.path.join(self.args['work-dir'], tee_fpath))
            # NOTE(drew): shell=True subprocess call, can disable with self.config
            if sys.platform.startswith('win'):
                # for Windows, we run shell=True otherwise most built-in cmd.exe calls won't work.
                self.exec(run_from_dir, clist, tee_fpath=tee_fpath, shell=True)
            else:
                self.exec(run_from_dir, clist, tee_fpath=tee_fpath,
                          shell=self.config.get('deps_subprocess_shell', False))


    def update_file_lists_for_work_dir(self) -> None:
        '''Handles any source files that were creating by "shell" style commands in the

        work-dir, these need to be added via self.add_file(..) in the correct order
        of the dependencies. Basically, any files that were left with @EDA-WORK-DIR@ prefix
        need to be patched and added.
        '''
        if not self.dep_work_dir_add_srcs:
            return

        # If we encounter any @EDA-WORK_DIR@some_file.v in self.files, self.files_v, etc,
        # then replace it with: self.args['work-dir'] / some_file.v:
        _work_dir_add_srcs_path_string_len = len(self._work_dir_add_srcs_path_string)
        work_dir_abspath = os.path.abspath(self.args['work-dir'])
        for key in list(self.files.keys()): # list so it's not an iterator, updates self.files.
            if isinstance(key, str) and key.startswith(self._work_dir_add_srcs_path_string):
                new_key = os.path.join(work_dir_abspath, key[_work_dir_add_srcs_path_string_len :])
                self.files.pop(key)
                self.files[new_key] = True

        my_file_lists_list = [self.files_v, self.files_sv, self.files_vhd, self.files_cpp,
                              self.files_sdc]
        for my_file_list in my_file_lists_list:
            for i,value in enumerate(my_file_list):
                if value and isinstance(value, str) and \
                   value.startswith(self._work_dir_add_srcs_path_string):
                    new_value = os.path.join(
                        work_dir_abspath, value[_work_dir_add_srcs_path_string_len :]
                    )
                    my_file_list[i] = new_value
                    util.debug(f"file lists: replaced {value} with {new_value}")


    def update_non_source_files_in_work_dir(self) -> None:
        '''For non-source files (that are tracked as 'reqs' in DEPS markup files) these

        need to be copied or linked to the work-dir. For example, if some SV assumes it
        can $readmemh('file_that_is_here.txt') but we're running out of work-dir. Linking
        is the easy work-around vs trying to run-in-place of all SV files.
        '''

        for fname in self.files_non_source:
            _, leaf_fname = os.path.split(fname)
            destfile = os.path.join(self.args['work-dir'], leaf_fname)
            relfname = os.path.relpath(fname)
            caller_info = self.files_caller_info[fname]
            if not os.path.exists(fname):
                util.info(f'{fname=} {self.files_caller_info=}')
                self.error(f'Non-source file (reqs?) {relfname=} does not exist from {caller_info}')
            elif not os.path.exists(destfile):
                util.debug(f'updating non-source file to work-dir: Linked {fname=} to {destfile=},',
                           f'from {caller_info}')
                if sys.platform == "win32":
                    shutil.copyfile(fname, destfile) # On Windows, fall back to copying
                else:
                    os.symlink(src=fname, dst=destfile)

    @staticmethod
    def get_top_name(name: str) -> str:
        '''Attempt to get the 'top' module name from a file, such as path/to/mine.sv will

        return "mine"'''
        # TODO(drew): Use the helper method in util for this instead to peek in file contents?
        return os.path.splitext(os.path.basename(name))[0]


    def process_plusarg( # pylint: disable=too-many-branches
            self, plusarg: str, pwd: str = os.getcwd()
    ) -> None:
        '''Retuns str, parses a +define+, +incdir+, +key=value str; adds to internal.

        Adds to self.defines, self.incdirs,
        Or, adds to self.args['unprocessed-plusargs'] (list) and retuns value added
        to unprocessed-plusargs.
        '''

        # Since this may be coming from a raw CLI/bash/powershell argparser, we may have
        # args that come from shlex.quote(token), such as:
        #   token = '\'+define+OC_ROOT="/foo/bar/opencos"\''
        # So we strip all outer ' or " on the plusarg:
        plusarg = strip_outer_quotes(plusarg)
        if not pwd:
            pwd = ''

        if plusarg.startswith('+define+'):
            plusarg = plusarg[len('+define+'):]
            m = re.match(r'^(\w+)$', plusarg)
            if m:
                k = m.group(1)
                self.defines[k] = None
                util.debug(f"Defined {k}")
                return None
            m = re.match(r'^(\w+)\=(\S+)$', plusarg)
            if not m:
                m = re.match(r'^(\w+)\=(\"[^\"]*\")$', plusarg)
            if m:
                k = m.group(1)
                v = m.group(2)
                if v and isinstance(v, str):
                    if v.startswith('%PWD%/'):
                        v = v.replace('%PWD%', os.path.abspath(pwd))
                    if v.startswith('%SEED%'):
                        v = v.replace('%SEED%', str(self.args.get('seed', 1)))
                self.defines[k] = v
                util.debug(f"Defined {k}={v}")
                return None
            self.error(f"Didn't understand +define+: '{plusarg}'",
                       error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)
            return None

        if plusarg.startswith('+incdir+'):
            plusarg = plusarg[len('+incdir+'):]
            m = re.match(r'^(\S+)$', plusarg)
            if m:
                incdir = m.group(1)
                if incdir not in self.incdirs:
                    self.incdirs.append(os.path.abspath(incdir))
                    util.debug(f"Added include dir '{os.path.abspath(incdir)}'")
                return None
            self.error(f"Didn't understand +incdir+: '{plusarg}'",
                       error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)
            return None

        # remaining plusargs as stored in self.args['unprocessed-plusargs'] (list)
        if plusarg.startswith('+'):
            if not self.config.get('bare_plusarg_supported', False):
                self.error(f"bare plusarg(s) are not supported: {plusarg}'")
                return None
            if plusarg not in self.args['unprocessed-plusargs']:
                self.args['unprocessed-plusargs'].append(plusarg)
                # For anything added to unprocessed-plusarg, we have to return it, to let
                # derived classes have the option to handle it
                return plusarg

        self.error(f"Didn't understand +plusarg: '{plusarg}'",
                   error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)
        return None


    def append_shell_commands(self, cmds : list) -> None:
        ''' Given a cmds (list), where each item is a dict with:

        { 'target_node': str,
          'target_path': str,
          'exec_list': list
        }
        add to this class's dep_shell_commands for deferred processing
        '''

        for entry in cmds:
            if entry is None or not isinstance(entry, dict):
                continue
            if entry in self.dep_shell_commands:
                # we've already run this exact command (target node, target path, exec list),
                # don't run it again
                continue

            assert 'exec_list' in entry, f'{entry=}'
            util.debug(f'adding - dep_shell_command: {entry=}')
            self.dep_shell_commands.append(entry)


    def append_work_dir_add_srcs(self, add_srcs: list, caller_info: str) -> None:
        '''Given add_srcs (list), where each item is a dict with:

        { 'target_node': str,
          'target_path': str,
          'file_list': list
        }

        adds files to set self.dep_work_dir_add_src, and call add_file on it, basically
        resolving adding source files that were generated and residing in the work-dir.
        '''
        for entry in add_srcs:
            if entry is None or not isinstance(entry, dict):
                continue

            work_dir_files = entry['file_list']
            for filename in work_dir_files:
                # Unfortunately, self.args['work-dir'] doesn't exist yet and hasn't been set,
                # so we'll add these files as '@EDA-WORK_DIR@' + filename, and have to replace
                # the EDA-WORK_DIR@ string later in our flow.
                filename_use = self._work_dir_add_srcs_path_string + filename
                dep_key_tuple = (
                    entry['target_path'],
                    entry['target_node'],
                    filename_use
                )
                if filename_use not in self.files:
                    util.debug(f'work_dir_add_srcs@ {dep_key_tuple=} added file {filename_use=}')
                    self.add_file(filename=filename_use, use_abspath=False, caller_info=caller_info)
                    # avoid duplicate calls, and keep a paper trail of which DEPS added
                    # files from the self.args['work-dir'] using this method.
                    self.dep_work_dir_add_srcs.add(dep_key_tuple) # add to set()
                elif dep_key_tuple not in self.dep_work_dir_add_srcs:
                    # we've already added the file so this dep was skipped for this one file.
                    util.warning(f'work_dir_add_srcs@ {dep_key_tuple=} but {filename_use=}',
                                 'is already in self.files (duplicate dependency on generated',
                                 'file?)')


    def resolve_target(
            self, target: str, no_recursion: bool = False, caller_info: str = ''
    ) -> bool:
        '''Returns True if target is found. Entry point for resolving a CLI path based target name.

        Will recursively call resolve_target_core, looking for a filename existing
        or DEPS markup file in that path and a target (key) in the markup table.

        This will populate all source file dependencies, commands, and other DEPS markup
        features as the target is resolved.
        '''
        util.debug(f"Entered resolve_target({target})")
        # self.target is a name we grab for the job (i.e. for naming work dir etc).  we don't want
        # the path prefix.

        self.target_path, self.target = os.path.split(target)

        if target in self.targets_dict:
            # If we're encountered this target before, stop. We're not traversing again.
            return True

        self.targets_dict[target] = None
        file_exists, fpath, forced_extension = files.get_source_file(target)
        if file_exists:
            # If the target is a file (we're at the root here processing CLI arg tokens)
            # and that file exists and has an extension, then there's no reason to go looking
            # in DEPS files, add the file and return True.
            _, file_ext = os.path.splitext(fpath)
            if forced_extension or file_ext:
                self.add_file(fpath, caller_info=caller_info,
                              forced_extension=forced_extension)
                return True

        return self.resolve_target_core(target, no_recursion, caller_info)

    def resolve_target_core( # pylint: disable=too-many-locals,too-many-branches
            self, target: str, no_recursion: bool, caller_info: str = ''
    ) -> bool:
        '''Returns True if target is found. recursive point for resolving path or DEPS markup
        target names.'''

        util.debug(f"Entered resolve_target_core({target=})")
        found_target = False
        target_path, target_node = os.path.split(target)

        deps, data, deps_file = None, None, None
        found_deps_file = False

        if self.config['deps_markup_supported']:
            deps = DepsFile(
                command_design_ref=self, target_path=target_path, cache=self.cached_deps
            )
            deps_file = deps.deps_file
            data = deps.data

        # Continue if we have data, otherwise look for files other than DEPS.<yml|yaml>
        if data is not None:
            found_deps_file = True
            found_target = deps.lookup(target_node=target_node, caller_info=caller_info)

        if found_deps_file and found_target:

            entry = deps.get_entry(target_node=target_node)

            # For convenience, use an external class for this DEPS.yml table/dict
            # This could be re-used for any markup DEPS.json, DEPS.toml, DEPS.py, etc.
            deps_processor = DepsProcessor(
                command_design_ref = self,
                deps_entry = entry,
                target = target,
                target_path = target_path,
                target_node = target_node,
                deps_file = deps_file,
                # Update the caller_info for this DEPS.yml file's target_node, b/c we're now
                # examining this entry (target) in this deps_file.
                caller_info = deps.gen_caller_info(target_node)
            )

            # Process the target, and get new (unprocessed) deps entries list.
            # This updates self (for defines, incdirs, top, args, etc)
            # This will skip remaining deps in self.targets_dict
            deps_targets_to_resolve = deps_processor.process_deps_entry()
            util.debug(f'   ... for {target_node=} {deps_file=}, {deps_targets_to_resolve=}')

            # Recurse on the returned deps (ordered list), if they haven't already been traversed.
            for x in deps_targets_to_resolve:
                caller_info = deps.gen_caller_info(target_node)
                if x and isinstance(x, tuple):
                    # if deps_processor.process_deps_entry() gave us a tuple, it's an
                    # unprocessed 'command' that we kept in order until now. Append it.
                    assert len(x) == 2, \
                        f'command tuple {x=} must be len 2, {target_node=} {deps_file=}'
                    shell_commands_list, work_dir_add_srcs_list = x
                    self.append_shell_commands( cmds=shell_commands_list )
                    self.append_work_dir_add_srcs( add_srcs=work_dir_add_srcs_list,
                                                   caller_info=caller_info )

                elif x and x not in self.targets_dict:
                    self.targets_dict[x] = None # add it before processing.
                    file_exists, fpath, forced_extension = files.get_source_file(x)
                    if file_exists:
                        self.add_file(filename=fpath, caller_info=caller_info,
                                      forced_extension=forced_extension)
                    else:
                        util.debug(f'   ... Calling resolve_target_core({x=})')
                        found_target |= self.resolve_target_core(
                            x, no_recursion, caller_info=caller_info
                        )


        # Done with DEPS.yml if it existed.

        if not found_target:
            util.debug(f"Haven't been able to resolve {target=} via DEPS")
            known_file_extensions_for_source = []
            for x in ('verilog', 'systemverilog', 'vhdl', 'cpp'):
                known_file_extensions_for_source += self.config.get(
                    'file_extensions', {}).get(x, [])
            for e in known_file_extensions_for_source:
                try_file = target + e
                util.debug(f"Looking for file {try_file}")
                if os.path.exists(try_file):
                    self.add_file(try_file, caller_info=f'n/a::{target}::n/a')
                    found_target = True
                    break # move on to the next target
            if not found_target: # if STILL not found_this_target...
                self.error(f"Unable to resolve {target=}",
                           error_code=status_constants.EDA_DEPS_TARGET_NOT_FOUND)

        # if we've found any target since being called, it means we found the one we were called for
        return found_target

    def add_file(
            self, filename: str, use_abspath: bool = True, add_to_non_sources: bool = False,
            caller_info: str = '', forced_extension: str = ''
    ) -> str:
        '''Given a filename, add it to one of self.files_sv or similar lists

        based on file extension or prefix directive.'''
        _, file_ext = os.path.splitext(filename)
        if use_abspath:
            file_abspath = os.path.abspath(filename)
        else:
            file_abspath = filename


        if file_abspath in self.files:
            util.debug(f"Not adding file {file_abspath}, already have it")
            return ''

        known_file_ext_dict = self.config.get('file_extensions', {})
        v_file_ext_list = known_file_ext_dict.get('verilog', [])
        sv_file_ext_list = known_file_ext_dict.get('systemverilog', [])
        vhdl_file_ext_list = known_file_ext_dict.get('vhdl', [])
        cpp_file_ext_list = known_file_ext_dict.get('cpp', [])
        sdc_file_ext_list = known_file_ext_dict.get('synth_constraints', [])

        if forced_extension:
            # If forced_extension='systemverilog', then use the first known extension for
            # it ('.sv', from eda_config_defaults.yml), which will pick it up in the if-elif
            # below.
            file_ext = known_file_ext_dict.get(forced_extension, [''])[0]
            util.debug(f"{forced_extension=} for {filename=} as type '{file_ext}'")


        if not add_to_non_sources and \
           file_ext in known_file_ext_dict.get('inferred_top', []):
            self.last_added_source_file_inferred_top = file_abspath

        if add_to_non_sources:
            self.files_non_source.append(file_abspath)
            util.debug(f"Added non-source file file {filename} as {file_abspath}")
        elif file_ext in v_file_ext_list and not self.args['all-sv']:
            self.files_v.append(file_abspath)
            util.debug(f"Added Verilog file {filename} as {file_abspath}")
        elif file_ext in sv_file_ext_list or \
             ((file_ext in v_file_ext_list) and self.args['all-sv']):
            self.files_sv.append(file_abspath)
            util.debug(f"Added SystemVerilog file {filename} as {file_abspath}")
        elif file_ext in vhdl_file_ext_list:
            self.files_vhd.append(file_abspath)
            util.debug(f"Added VHDL file {filename} as {file_abspath}")
        elif file_ext in cpp_file_ext_list:
            self.files_cpp.append(file_abspath)
            util.debug(f"Added C++ file {filename} as {file_abspath}")
        elif file_ext in sdc_file_ext_list:
            self.files_sdc.append(file_abspath)
            util.debug(f"Added SDC file {filename} as {file_abspath}")
        else:
            # unknown file extension. In these cases we link the file to the working directory
            # so it is available (for example, a .mem file that is expected to exist with relative
            # path)
            self.files_non_source.append(file_abspath)
            util.debug(f"Added non-source file {filename} as {file_abspath}")

        self.files[file_abspath] = True
        self.files_caller_info[file_abspath] = caller_info
        return file_abspath

    def process_tokens( # pylint: disable=too-many-locals,too-many-branches,too-many-statements
            self, tokens: list, process_all: bool = True,
            pwd: str = os.getcwd()
    ) -> list:
        '''Returns a list of unparsed args (self.args did not have these keys present)

        Entrypoint from eda.py calling a command handler obj.process_tokens(args).
        Dervied classes are expected to call this parent process_tokens to parse and handle
        their self.args dict'''

        util.debug(f'CommandDesign - process_tokens start - {tokens=}')

        # see if it's a flag/option like --debug, --seed <n>, etc
        # This returns all unparsed args, and doesn't error out due to process_all=False
        orig_tokens = tokens.copy()
        unparsed = Command.process_tokens(self, tokens, process_all=False, pwd=pwd)
        util.debug(f'CommandDesign - after Command.process_tokens(..) {unparsed=}')

        # deal with +define+ or +incdir+, consume it and remove from unparsed
        # walk the list, remove all items after we're done.
        remove_list = []
        for token in unparsed:
            # Since this is a raw argparser, we may have args that come from shlex.quote(token),
            # such as:
            #   token = '\'+define+OC_ROOT="/foo/bar/opencos"\''
            # So we have to check for strings that have been escaped for shell with extra single
            # quotes.
            m = re.match(r"^\'?\+\w+", token)
            if m:
                # Copy and strip all outer ' or " on the plusarg:
                plusarg = strip_outer_quotes(token)
                self.process_plusarg(plusarg, pwd=pwd)
                remove_list.append(token)
        for x in remove_list:
            unparsed.remove(x)

        if not unparsed and self.error_on_no_files_or_targets:
            # derived classes can set error_on_no_files_or_targets=True
            # For example: CommandSim will error (requires files/targets),
            # CommandWaves does not (files/targets not required)
            # A nice-to-have: if someone ran: eda sim; without a file/target,
            # check the DEPS markup file for a single target, and if so run it
            # on the one and only target.
            if self.config['deps_markup_supported']:
                deps = DepsFile(
                    command_design_ref=self, target_path=os.getcwd(), cache=self.cached_deps
                )
                if deps.deps_file and deps.data:
                    all_targets = deps_data_get_all_targets(deps.data)
                    if all_targets:
                        target = all_targets[-1]
                        unparsed.append(target)
                        util.warning(f"For command '{self.command_name}' no files or targets were",
                                     f"presented at the command line, so using '{target}' from",
                                     f"{deps.deps_file}")
            if len(unparsed) == 0:
                # If unparsed is still empty, then error.
                self.error(f"For command '{self.command_name}' no files or targets were",
                           f"presented at the command line: {orig_tokens}",
                           error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)

        # by this point hopefully this is a target ... is it a simple filename?
        remove_list = []
        last_potential_top_file = ('', '')   # (top, fpath)
        last_potential_top_target = ('', '') # (top, path/to/full-target-name)
        last_potential_top_isfile = False
        caller_info = ''
        for token in unparsed:
            file_exists, fpath, forced_extension = files.get_source_file(token)
            if file_exists:
                file_abspath = os.path.abspath(fpath)
                _, file_ext = os.path.splitext(file_abspath)
                if not forced_extension and not file_ext:
                    # This probably isn't a file we want to use
                    util.warning(f'looking for deps {token=}, found {file_abspath=}' \
                                 + ' but has no file extension, we will not add this file')
                    # do not consume it, it's probably a named target in DEPS.yml
                else:
                    self.add_file(filename=fpath, caller_info=caller_info,
                                  forced_extension=forced_extension)
                    if not self.args['top']:
                        known_file_ext_dict = self.config.get('file_extensions', {})
                        if forced_extension:
                            file_ext = known_file_ext_dict.get(forced_extension, [''])[0]
                        if file_ext in known_file_ext_dict.get('inferred_top', []):
                            # last cmd line arg was a filename that could have inferred top.
                            last_potential_top_isfile = True

                    remove_list.append(token)
                    continue # done with token, consume it, we added the file.

            # we appear to be dealing with a target name which needs to be resolved (usually
            # recursively)
            if token.startswith(os.sep):
                target_name = token # if it's absolute path, don't prepend anything
            else:
                target_name = os.path.join(".", token) # prepend ./ to make it like: <path>/<file>

            util.debug(f'Calling self.resolve_target on {target_name=} ({token=})')
            if self.resolve_target(target_name, caller_info=caller_info):
                if not self.args['top']:
                    # last cmd line arg was a target that we'll likely use for inferred top.
                    last_potential_top_target = (self.get_top_name(target_name), target_name)
                    last_potential_top_isfile = False

                remove_list.append(token)
                continue # done with token

        for x in remove_list:
            unparsed.remove(x)

        # we were unable to figure out what this command line token is for...
        if process_all and len(unparsed) > 0:
            self.error(f"Didn't understand command remaining tokens {unparsed=} in CommandDesign",
                       error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)

        # handle a missing self.args['top'] with last filepath or last target:
        if not self.args.get('top', ''):
            if not last_potential_top_isfile and last_potential_top_target[0]:
                # If we have a target name from DEPS, prefer to use that.
                self.args['top'], self.args['top-path'] = last_potential_top_target
                util.info("--top not specified, inferred from target:",
                          f"{self.args['top']} ({self.args['top-path']})")

            else:
                best_top_fname = self.last_added_source_file_inferred_top
                if best_top_fname:
                    last_potential_top_file = (self.get_top_name(best_top_fname), best_top_fname)

            if not self.args['top'] and last_potential_top_file[0]:
                # If we don't have a target name, and no top name yet, then go looking for the
                # module name in the final source file added.
                self.args['top-path'] = last_potential_top_file[1] # from tuple: (top, fpath)
                self.args['top'] = util.get_inferred_top_module_name(
                    module_guess=last_potential_top_file[0],
                    module_fpath=last_potential_top_file[1]
                )
                if self.args['top']:
                    util.info("--top not specified, inferred from final source file:",
                              f"{self.args['top']} ({self.args['top-path']})")
                    # If top wasn't set, and we're using the final command-line 'arg' filename
                    # (not from DEPS.yml) we need to override self.target if that was set. Otherwise
                    # it won't save to the correct work-dir:
                    self.target = self.args['top']

        if self.error_on_missing_top and not self.args.get('top', ''):
            self.error("Did not get a --top or DEPS top, required to run command",
                       f"'{self.command_name}' for tool={self.args.get('tool', None)}",
                       error_code=status_constants.EDA_COMMAND_MISSING_TOP)

        return unparsed


    def get_command_line_args( # pylint: disable=dangerous-default-value
            self, remove_args: list = [], remove_args_startswith: list = []
    ) -> list:
        '''Returns a list of all the args if you wanted to re-run this command
        (excludes eda, command, target).'''

        # This will not set bool's that are False, does not add --no-<somearg>
        # nor --<somearg>=False (it's unclear which are 'store_true' v/ bool-action-kwargs)
        # This will not set str's that are empty
        # this will not set ints that are 0 (unless modified)
        # TODO(drew): we may want to revisit this if we tracked default arg values,
        # or perhaps if they have been "modified".
        ret = []
        for k,v in self.args.items():

            # Some args cannot be extracted and work, so omit these:
            if k in ['top-path'] + remove_args:
                continue
            if any(k.startswith(x) for x in remove_args_startswith):
                continue

            is_modified = self.modified_args.get(k, False)

            if isinstance(v, bool) and v:
                ret.append(f'--{k}')
            elif isinstance(v, int) and (bool(v) or is_modified):
                ret.append(f'--{k}={v}')
            elif isinstance(v, str) and v:
                ret.append(f'--{k}={v}')
            elif isinstance(v, list):
                for item in v:
                    if item or isinstance(item, (bool, str)):
                        # don't print bool/str that are blank.
                        ret.append(f'--{k}={item}') # lists append

        return ret


#_THREADS_START = 0
#_THREADS_DONE = 0

class ThreadStats:
    '''To avoid globals for two ints, keep a class holder so CommandParallel and
    CommandParallelWorker can share values'''

    done = 0
    started = 0

    def all_done(self) -> bool:
        '''Returns True if all started jobs are done'''
        return self.started == self.done

    def get_remaining(self) -> int:
        '''Returns remaining number of jobs'''
        return max(self.started - self.done, 0)

    def __repr__(self) -> str:
        '''Pretty print DONE/STARTED'''
        return f'{self.done}/{self.started}'


class CommandParallelWorker(threading.Thread):
    '''Helper class for a single threaded job, often run by a CommandParallel command
    handler class'''

    def __init__(
            self, n, work_queue: queue.Queue, done_queue: queue.Queue,
            threads_stats: ThreadStats
    ):
        threading.Thread.__init__(self)
        self.n = n
        self.work_queue = work_queue
        self.done_queue = done_queue
        self.stop_request = False
        self.job_name = ""
        self.proc = None
        self.pid = None
        self.last_timer_debug = 0
        self.threads_stats = threads_stats # ref to shared object
        util.debug(f"WORKER_{n}: START")

    def run(self):
        '''Runs this single job via threading. This is typically created and called by

        a CommandParallel class handler
        '''

        while True:
            # Get the work from the queue and expand the tuple
            i, command_list, job_name, _ = self.work_queue.get()
            self.job_name = job_name
            try:
                util.debug(f"WORKER_{self.n}: Running job {i}: {job_name}")
                util.debug(f"WORKER_{self.n}: Calling Popen")
                proc = subprocess.Popen( # pylint: disable=consider-using-with
                    command_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
                self.proc = proc
                util.debug(f"WORKER_{self.n}: Opened process, PID={proc.pid}")
                self.pid = proc.pid
                self.threads_stats.started += 1
                while proc.returncode is None:
                    try:
                        if (time.time() - self.last_timer_debug) > 10:
                            util.debug(f"WORKER_{self.n}: Calling proc.communicate")
                        stdout, stderr = proc.communicate(timeout=0.5)
                        util.debug(f"WORKER_{self.n}: got: \n*** stdout:\n{stdout}\n***",
                                   f"stderr:{stderr}")
                    except subprocess.TimeoutExpired:
                        if (time.time() - self.last_timer_debug) > 10:
                            util.debug(f"WORKER_{self.n}: Timer expired, stop_request=",
                                       f"{self.stop_request}")
                            self.last_timer_debug = time.time()
                    if self.stop_request:
                        util.debug(f"WORKER_{self.n}: got stop request, issuing SIGINT")
                        proc.send_signal(signal.SIGINT)
                        util.debug(f"WORKER_{self.n}: got stop request, calling proc.wait")
                        proc.wait()

                util.debug(f"WORKER_{self.n}: -- out of while loop")
                self.pid = None
                self.proc = None
                self.job_name = "<idle>"
                util.debug(f"WORKER_{self.n}: proc poll returns is now {proc.poll()}")
                try:
                    util.debug(f"WORKER_{self.n}: Calling proc.communicate one last time")
                    stdout, stderr = proc.communicate(timeout=0.1)
                    util.debug(f"WORKER_{self.n}: got: \n*** stdout:\n{stdout}\n***",
                               f"stderr:{stderr}")
                except subprocess.TimeoutExpired:
                    util.debug(f"WORKER_{self.n}: timeout waiting for communicate after loop?")
                except Exception as e:
                    util.debug(f"WORKER_{self.n}: timeout with exception {e=}")

                return_code = proc.poll()
                util.debug(f"WORKER_{self.n}: Finished job {i}: {job_name} with return code",
                           f"{return_code}")
                self.done_queue.put((i, job_name, return_code))
            finally:
                util.debug(f"WORKER_{self.n}: -- in finally block")
                self.work_queue.task_done()
                self.threads_stats.done += 1


class CommandParallel(Command):
    '''Base class command handler for running multiple eda jobs, such as for child classes

    in commands.multi or commands.sweep
    '''
    def __init__(self, config: dict):
        Command.__init__(self, config=config)
        self.jobs = []
        self.jobs_status = []
        self.args['parallel'] = 1
        self.worker_threads = []
        self.threads_stats = ThreadStats()

    def __del__(self): # pylint: disable=too-many-branches
        util.debug(f"In Command.__del__, threads done/started: {self.threads_stats}")
        if self.threads_stats.all_done():
            return
        util.warning(f"Need to shut down {self.threads_stats.get_remaining()} worker threads...")
        for w in self.worker_threads:
            if w.proc:
                util.warning(f"Requesting stop of PID {w.pid}: {w.job_name}")
                w.stop_request = True
        for _ in range(10):
            util.debug(f"Threads done/started: {self.threads_stats}")
            if self.threads_stats.started == self.threads_stats.done:
                util.info("All threads done")
                return
            time.sleep(1)
        subprocess.Popen(['stty', 'sane']).wait() # pylint: disable=consider-using-with
        util.debug("Scanning workers again")
        for w in self.worker_threads:
            if w.proc:
                util.info(f"need to SIGINT WORKER_{w.n}, may need manual cleanup, check 'ps'")
                if w.pid:
                    os.kill(w.pid, signal.SIGINT)
        for _ in range(5):
            util.debug(f"Threads done/started: {self.threads_stats}")
            if self.threads_stats.all_done():
                util.info("All threads done")
                return
            time.sleep(1)
        subprocess.Popen(['stty', 'sane']).wait() # pylint: disable=consider-using-with
        util.debug("Scanning workers again")
        for w in self.worker_threads:
            if w.proc:
                util.info(f"need to TERM WORKER_{w.n}, probably needs manual cleanup, check 'ps'")
                if w.pid:
                    os.kill(w.pid, signal.SIGTERM)
        for _ in range(5):
            util.debug(f"Threads done/started: {self.threads_stats}")
            if self.threads_stats.all_done():
                util.info("All threads done")
                return
            time.sleep(1)
        subprocess.Popen(['stty', 'sane']).wait() # pylint: disable=consider-using-with
        util.debug("Scanning workers again")
        for w in self.worker_threads:
            if w.proc:
                util.info(f"need to KILL WORKER_{w.n}, probably needs manual cleanup, check 'ps'")
                if w.pid:
                    os.kill(w.pid, signal.SIGKILL)
        util.stop_log()
        subprocess.Popen(['stty', 'sane']).wait() # pylint: disable=consider-using-with

    def run_jobs( # pylint: disable=too-many-locals,too-many-branches,too-many-statements
            self, command: str
    ) -> None:
        '''Runs all "jobs" in self.jobs list, either serially or in parallel'''

        # this is where we actually run the jobs.  it's a messy piece of code and prob could use
        # refactoring but the goal was to share as much as possible (job start, end, pass/fail
        # judgement, etc) while supporting various mode combinations (parallel mode, verbose mode,
        # fancy mode, etc) and keeping the UI output functional and awesome sauce

        # walk targets to find the longest name, for display reasons
        longest_job_name = 0
        total_jobs = len(self.jobs)
        self.jobs_status = [None] * total_jobs
        for i in range(total_jobs):
            longest_job_name = max(longest_job_name, len(self.jobs[i]['name']))

        run_parallel = self.args['parallel'] > 1

        # figure out the width to print various numbers
        jobs_digits = len(f"{total_jobs}")

        job_done_return_code = None
        job_done_run_time = 0
        job_done_name = ''

        # run the jobs!
        running_jobs = {}
        passed_jobs = []
        failed_jobs = []
        workers = []
        jobs_complete = 0
        jobs_launched = 0
        num_parallel = min(len(self.jobs), self.args['parallel'])
        # 16 should really be the size of window or ?
        _, lines = shutil.get_terminal_size()
        # we will enter fancy mode if we are parallel and we can leave 6 lines of regular scrolling
        # output
        fancy_mode = all([util.args['fancy'], num_parallel > 1, num_parallel <= (lines-6)])
        multi_cwd = util.getcwd() + os.sep

        self.patch_jobs_for_duplicate_target_names()

        if run_parallel:
            # we are doing this multi-threaded
            util.info(f"Parallel: Running multi-threaded, starting {num_parallel} workers")
            work_queue = queue.Queue()
            done_queue = queue.Queue()
            for x in range(num_parallel):
                worker = CommandParallelWorker(
                    n=x, work_queue=work_queue, done_queue=done_queue,
                    threads_stats=self.threads_stats
                )
                # Setting daemon to True will let the main thread exit even though the workers are
                # blocking
                worker.daemon = True
                worker.start()
                self.worker_threads.append(worker)
                workers.append(x)
            if fancy_mode:
                # in fancy mode, we will take the bottom num_parallel lines to show state of workers
                util.fancy_start(fancy_lines=num_parallel)
                for x in range(num_parallel):
                    util.fancy_print(f"Starting worker {x}", x)

        while self.jobs or running_jobs:
            job_done = False
            job_done_quiet = False
            anything_done = False

            def sprint_job_line(job_number=0, job_name="", final=False, hide_stats=False):
                return (
                    "INFO: [EDA] " +
                    string_or_space(
                        f"[job {job_number:0{jobs_digits}d}/{total_jobs:0{jobs_digits}d} ",
                        final) +
                    string_or_space("| pass ", hide_stats or final) +
                    string_or_space(
                        f"{len(passed_jobs):0{jobs_digits}d}/{jobs_complete:0{jobs_digits}d} ",
                        hide_stats) +
                    string_or_space(f"@ {(100 * (jobs_complete)) / total_jobs : 5.1f}%",
                                         hide_stats or final) +
                    string_or_space("] ", final) +
                    f"{command} {(job_name+' ').ljust(longest_job_name+3,'.')}"
                )

            # for any kind of run (parallel or not, fancy or not, verbose or not) ...
            # can we launch a job?
            if self.jobs and (len(running_jobs) < num_parallel):
                # we are launching a job
                jobs_launched += 1
                anything_done = True
                job = self.jobs.pop(0)
                # TODO(drew): it might be nice to pass more items on 'job' dict, like
                # logfile or job-name, so CommandSweep or CommandMulti don't have to set
                # via args. on their command_list.
                if job['name'].startswith(multi_cwd):
                    job['name'] = job['name'][len(multi_cwd):]
                # in all but fancy mode, we will print this text at the launch of a job.  It may
                # get a newline below
                job_text = sprint_job_line(jobs_launched, job['name'], hide_stats=run_parallel)
                command_list = job['command_list']
                cwd = util.getcwd()

                if run_parallel:
                    # multithreaded job launch: add to queue
                    worker = workers.pop(0)
                    running_jobs[str(jobs_launched)] = { 'name' : job['name'],
                                                         'number' : jobs_launched,
                                                         'worker' : worker,
                                                         'start_time' : time.time(),
                                                         'update_time' : time.time()}
                    work_queue.put((jobs_launched, command_list, job['name'], cwd))
                    suffix = "<START>"
                    if fancy_mode:
                        util.fancy_print(job_text+suffix, worker)
                    elif failed_jobs:
                        # if we aren't in fancy mode, we will print a START line, periodic RUNNING
                        # lines, and PASS/FAIL line per-job
                        util.print_orange(job_text + Colors.yellow + suffix)
                    else:
                        util.print_yellow(job_text + Colors.yellow + suffix)
                else:
                    # single-threaded job launch, we are going to print out job info as we start
                    # each job... no newline. since non-verbose silences the job and prints only
                    # <PASS>/<FAIL> after the trailing "..." we leave here
                    if failed_jobs:
                        util.print_orange(job_text, end="")
                    else:
                        util.print_yellow(job_text, end="")
                    job_done_number = jobs_launched
                    job_done_name = job['name']
                    job_start_time = time.time()
                    if util.args['verbose']:
                        # previous status line gets a \n, then job is run passing
                        # stdout/err, then print 'job_text' again with pass/fail
                        util.print_green("")
                        # run job, sending output to the console
                        _, _, job_done_return_code = self.exec(
                            cwd, command_list, background=False, stop_on_error=False, quiet=False
                        )
                        # reprint the job text previously printed before running job (and given
                        # "\n" after the trailing "...")
                    else:
                        # run job, swallowing output (hope you have a logfile)
                        _, _, job_done_return_code = self.exec(
                            cwd, command_list, background=True, stop_on_error=False, quiet=True
                        )
                        # in this case, we have the job start text (trailing "...", no newline)
                        # printed
                        job_done_quiet = True
                    job_done = True
                    job_done_run_time = time.time() - job_start_time
                    # Since we consumed the job, use the job['index'] to track the per-job status:

            if run_parallel:
                # parallel run, check for completed job
                if done_queue.qsize():
                    # we're collecting a finished job from a worker thread.  note we will only
                    # reap one job per iter of the big loop, so as to share job completion code
                    # at the bottom
                    anything_done = True
                    job_done = True
                    job_done_number, job_done_name, job_done_return_code = done_queue.get()
                    t = running_jobs[str(job_done_number)]
                    # in fancy mode, we need to clear the worker line related to this job.
                    if fancy_mode:
                        util.fancy_print("INFO: [EDA] Parallel: Worker Idle ...", t['worker'])
                    job_done_run_time = time.time() - t['start_time']
                    util.debug(f"removing job #{job_done_number} from running jobs")
                    del running_jobs[str(job_done_number)]
                    workers.append(t['worker'])

            if run_parallel:
                # parallel run, update the UI on job status
                for _,t in running_jobs.items():
                    if (fancy_mode or (time.time() - t['update_time']) > 30):
                        t['update_time'] = time.time()
                        job_text = sprint_job_line(t['number'], t['name'], hide_stats=True)
                        suffix = f"<RUNNING: {sprint_time(time.time() - t['start_time'])}>"
                        if fancy_mode:
                            util.fancy_print(f"{job_text}{suffix}", t['worker'])
                        elif failed_jobs:
                            util.print_orange(job_text + Colors.yellow + suffix)
                        else:
                            util.print_yellow(job_text + Colors.yellow + suffix)

            # shared job completion code
            # single or multi-threaded, we can arrive here to harvest <= 1 jobs, and need
            # {job, return_code} valid, and we expect the start of a status line to have been
            # printed, ready for pass/fail
            if job_done:
                jobs_complete += 1
                if job_done_return_code is None or job_done_return_code:
                    # embed the color code, to change color of pass/fail during the
                    # util.print_orange/yellow below
                    if job_done_return_code == 124:
                        # bash uses 124 for bash timeout errors, if that was preprended to the
                        # command list.
                        suffix = f"{Colors.red}<TOUT: {sprint_time(job_done_run_time)}>"
                    else:
                        suffix = f"{Colors.red}<FAIL: {sprint_time(job_done_run_time)}>"
                    failed_jobs.append(job_done_name)
                else:
                    suffix = f"{Colors.green}<PASS: {sprint_time(job_done_run_time)}>"
                    passed_jobs.append(job_done_name)
                # we want to print in one shot, because in fancy modes that's all that we're allowed
                job_done_text = "" if job_done_quiet else sprint_job_line(job_done_number,
                                                                          job_done_name)
                if failed_jobs:
                    util.print_orange(f"{job_done_text}{suffix}")
                else:
                    util.print_yellow(f"{job_done_text}{suffix}")
                self.jobs_status[job_done_number-1] = job_done_return_code

            if not anything_done:
                time.sleep(0.25) # if nothing happens for an iteration, chill out a bit

        if total_jobs:
            emoji = "< :) >" if (len(passed_jobs) == total_jobs) else "< :( >"
            util.info(sprint_job_line(final=True, job_name="jobs passed") + emoji, start="")
        else:
            util.info("Parallel: <No jobs found>")
        # Make sure all jobs have a set status:
        for i, rc in enumerate(self.jobs_status):
            if rc is None or not isinstance(rc, int):
                self.error(f'job {i=} {rc=} did not return a proper return code')
                self.jobs_status[i] = 2

        # if self.status > 0, then keep it non-zero, else set it if we still have running jobs.
        if self.status == 0:
            if self.jobs_status:
                self.status = max(self.jobs_status)
            # else keep at 0, empty list.
        util.fancy_stop()

    @staticmethod
    def get_name_from_target(target: str) -> str:
        '''Given a target path, strip leftmost path separators to get a shorter string name'''
        return target.replace('../', '').lstrip('./').lstrip(os.path.sep)


    def update_args_list(self, args: list, tool: str) -> None:
        '''Modfies list args, using allow-listed known top-level args:

        --config-yml
        --eda-safe
        --tool

        Many args were consumed by eda before CommandParallel saw them
        (for commands like 'multi' or 'sweep'). Some are in self.config.
         We need to apply those eda level args to each single exec-command
        '''
        if any(a.startswith('--config-yml') for a in self.config['eda_original_args']):
            cfg_yml_fname = self.config.get('config-yml', None)
            if cfg_yml_fname:
                args.append(f'--config-yml={cfg_yml_fname}')
        if '--eda-safe' in self.config['eda_original_args']:
            args.append('--eda-safe')
        if tool:
            # tool can be None, if so we won't add it to the command (assumes default from
            # config-yml auto load order)
            args.append('--tool=' + tool)


    def get_unparsed_args_on_single_command(self, command: str, tokens: list) -> list:
        '''Returns a list of args that the single (non-multi) command cannot parse

        This will error on bad --args or -arg, such as:
          eda multi sim --seeeed=1
        is not a valid arg in CommandSim

        +arg=value, +arg+value will not be included in the return list, those are
        intended to be consumed by the single/job command downstream (anything starting
        with '+')

        Used by CommandMulti and CommandSweep.
        '''
        single_cmd_handler = self.config['command_handler'][command](config=self.config)
        single_cmd_parsed, single_cmd_unparsed = single_cmd_handler.run_argparser_on_list(
            tokens=tokens.copy(),
            apply_parsed_args=False,
        )
        util.debug(f'{self.command_name}: {single_cmd_parsed=}, {single_cmd_unparsed=}')

        # There should not be any single_cmd_unparsed args starting with '-'
        bad_remaining_args = [x for x in single_cmd_unparsed if x.startswith('-')]
        if bad_remaining_args:
            self.error(f'for {self.command_name} {command=} the following args are unknown',
                       f'{bad_remaining_args}',
                       error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)

        # Remove unparsed args starting with '+', since those are commonly sent downstream to
        # single job (example, CommandSim plusargs).
        return [x for x in single_cmd_unparsed if not x.startswith('+')]


    def patch_jobs_for_duplicate_target_names(self) -> None:
        '''Examines list self.jobs, and if leaf target names are duplicate will
        patch each command's job-name to:
            --job-name=path.leaf.command[.tool]

        Also do for --force-logfile
        '''

        def get_job_arg(job_dict: dict, arg_name: str) -> str:
            '''Fishes the arg_name out of an entry in self.jobs'''
            for i, item in enumerate(job_dict['command_list']):
                if item.startswith(f'--{arg_name}='):
                    _, name = item.split(f'--{arg_name}=')
                    return name
                if item == f'--{arg_name}':
                    return job_dict['command_list'][i + 1]
            return ''

        def replace_job_arg(job_dict: dict, arg_name: str, new_value: str) -> bool:
            '''Replaces the arg_name's value in an entry in self.jobs'''
            for i, item in enumerate(job_dict['command_list']):
                if item.startswith(f'--{arg_name}='):
                    job_dict['command_list'][i] = f'--{arg_name}=' + new_value
                    return True
                if item == f'--{arg_name}':
                    job_dict['command_list'][i + 1] = new_value
                    return True
            return False


        job_names_count_dict = {}
        for job_dict in self.jobs:

            key = get_job_arg(job_dict, arg_name='job-name')
            if not key:
                self.error(f'{job_dict=} needs to have a --job-name= arg attached',
                           error_code=status_constants.EDA_COMMAND_OR_ARGS_ERROR)
            if key not in job_names_count_dict:
                job_names_count_dict[key] = 1
            else:
                job_names_count_dict[key] += 1

        for i, job_dict in enumerate(self.jobs):
            key = get_job_arg(job_dict, 'job-name')
            if job_names_count_dict[key] < 2:
                continue

            tpath, _ = os.path.split(job_dict['target'])

            # prepend path information to job-name:
            patched_target_path = os.path.relpath(tpath).replace(os.sep, '_')
            new_job_name = f'{patched_target_path}.{key}'
            replace_job_arg(job_dict, arg_name='job-name', new_value=new_job_name)

            # prepend path information to force-logfile (if present):
            force_logfile = get_job_arg(job_dict, arg_name='force-logfile')
            if force_logfile:
                left, right = os.path.split(force_logfile)
                new_force_logfile = os.path.join(left, f'{patched_target_path}.{right}')
                replace_job_arg(
                    job_dict, arg_name='force-logfile', new_value=new_force_logfile
                )
                util.debug(
                    f'Patched job {job_dict["name"]}: --force-logfile={new_force_logfile}'
                )


            self.jobs[i] = job_dict
            util.debug(f'Patched job {job_dict["name"]}: --job-name={new_job_name}')
