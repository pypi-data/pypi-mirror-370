#!/usr/bin/env python3

'''opencos.eda is an executable script (as `eda <command> ...`)

This is the entrypoint for tool discovery, and running targets from command line or DEPS
markup files
'''

import subprocess
import os
import sys
import shutil
import re
import signal
import argparse
import shlex
import importlib.util

from pathlib import Path

import opencos
from opencos import util, eda_config, eda_base
from opencos.eda_base import Tool, which_tool
from opencos.utils import vsim_helper, vscode_helper

# Configure util:
util.progname = "EDA"
util.global_log.default_log_enabled = True
util.global_log.default_log_filepath = os.path.join('eda.work', 'eda.log')


# ******************************************************************************
# MAIN

# Set config['command_handler'] entries for (command, Class) so we know which
# eda command (such as, command: eda sim) is handled by which class (such as class: CommandSim)
# These are also overriden depending on the tool, for example --tool verilator sets
# "sim": CommandSimVerilator.
def init_config(
        config: dict,  quiet: bool = False, tool=None, run_auto_tool_setup: bool = True
) -> dict:
    '''Sets or clears entries in config (dict) so tools can be re-loaded.'''

    # For key DEFAULT_HANDLERS, we'll update config['command_handler'] with
    # the actual class using importlib (via opencos.util)
    config['command_handler'] = {}
    for command, str_class in config['DEFAULT_HANDLERS'].items():
        cls = util.import_class_from_string(str_class)
        if not cls:
            util.error(f"config DEFAULT_HANDLERS {command=} {str_class=} could not import")
        else:
            config['command_handler'][command] = cls

    config['auto_tools_found'] = {}
    config['tools_loaded'] = set()
    if run_auto_tool_setup:
        config = auto_tool_setup(config=config, quiet=quiet, tool=tool)
    return config




def usage(tokens: list, config: dict, command="") -> int:
    '''Returns an int shell return code, given remaining args (tokens list) and eda command.

    config is the config dict. Used to check valid commands in config['command_handler']

    Note that we pass the command (str) if possible, so things like:
     > eda help sim --tool verilator
    Will still return this message. This allows args like --config-yml=<file> to work with
    the help message if command is blank, such as:
     > eda --config-yml=<file> help
    '''

    if command == "":
        print(
"""
Usage:
    eda [<options>] <command> [options] <files|targets, ...>

Where <command> is one of:

    sim          - Simulates a DEPS target
    elab         - Elaborates a DEPS target (sort of sim based LINT)
    synth        - Synthesizes a DEPS target
    flist        - Create dependency from a DEPS target
    proj         - Create a project from a DEPS target for GUI sim/waves/debug
    multi        - Run multiple DEPS targets, serially or in parallel
    tools-multi  - Same as 'multi' but run on all available tools, or specfied using --tools
    sweep        - Sweep one or more arguments across a range, serially or in parallel
    build        - Build for a board, creating a project and running build flow
    waves        - Opens waveform from prior simulation
    upload       - Uploads a finished design into hardware
    open         - Opens a project
    export       - Export files related to a target, tool independent
    shell        - Runs only commands for DEPS target (like sim or elab, but stops prior to tool)
    targets      - list all possible targets given glob path.
    help         - This help (without args), or i.e. "eda help sim" for specific help

And <files|targets, ...> is one or more source file or DEPS markup file target,
    such as .v, .sv, .vhd[l], .cpp files, or a target key in a DEPS.[yml|yaml|toml|json].
    Note that you can prefix source files with `sv@`, `v@`, `vhdl@` or `cpp@` to
    force use that file as systemverilog, verilog, vhdl, or C++, respectively.

"""
        )
        eda_base.print_base_help()
        return 0

    if command in config['command_handler'].keys():
        sco = config['command_handler'][command](config=config) # sub command object
        sco.help(tokens=tokens)
        return util.exit(0)

    util.info("Valid commands are:")
    for k in sorted(config['command_handler'].keys()):
        util.info(f"   {k:20}")
    return util.error(f"Cannot provide help, don't understand command: '{command}'")


def interactive(config: dict) -> int:
    '''Returns bash/sh return code, entry point for running interactively in CLI if

    args are not present to directly call a command handler, --help, etc
    '''
    rc = 0
    while True:
        line = input('EDA->')
        m = re.match(r'^([^\#]*)\#.*$', line)
        if m:
            line = m.group(1)
        tokens = line.split()
        original_args = tokens.copy()
        # NOTE: interactive will not correctly handle --config-yml arg (from eda_config.py),
        # but we should do a best effor to re-parse args from util.py, such as
        # --quiet, --color, --fancy, --logfile, --debug or --debug-level, etc
        _, tokens = util.process_tokens(tokens)
        rc = process_tokens(
            tokens=tokens, original_args=original_args, config=config, is_interactive=True
        )
    return rc


def auto_tool_setup( # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        warnings: bool = True, config = None, quiet: bool = False, tool: str = ''
) -> dict:
    '''Returns an updated config, uses config['auto_tools_order'][0] dict, calls tool_setup(..)

    -- adds items to config['tools_loaded'] set
    -- updates config['command_handler'][command] with a Tool class

    Input arg tool can be in the form (for example):
      tool='verlator', tool='verilator=/path/to/verilator.exe'
      If so, updates config['auto_tools_order'][tool]['exe']
    '''


    tool = eda_config.update_config_auto_tool_order_for_tool(
        tool=tool, config=config
    )

    assert 'auto_tools_order' in config
    assert isinstance(config['auto_tools_order'], list)
    assert isinstance(config['auto_tools_order'][0], dict)

    for name, value in config['auto_tools_order'][0].items():
        if tool and tool != name:
            continue # if called with tool=(some_name), then only load that tool.

        util.debug(f"Checking for ability to run tool: {name}")
        exe = value.get('exe', str())
        if isinstance(exe, list):
            exe_list = exe
        elif isinstance(exe, str):
            exe_list = [exe] # make it a list
        else:
            util.error(f'eda.py: config["auto_tools_order"][0] for {name=} {value=} has bad type'
                       f'for {exe=}')
            continue

        has_all_py = True
        requires_py_list = value.get('requires_py', [])
        for pkg in requires_py_list:
            spec = importlib.util.find_spec(pkg)
            if not spec:
                has_all_py = False
                util.debug(f"... No, missing pkg {spec}")

        has_all_env = True
        requires_env_list = value.get('requires_env', [])
        for env in requires_env_list:
            if not os.environ.get(env, ''):
                has_all_env = False
                util.debug(f"... No, missing env {env}")

        has_all_exe = True
        has_all_in_exe_path = True
        for exe in exe_list:
            assert exe != '', f'{name=} {value=} value missing "exe" {exe=}'
            p = shutil.which(exe)
            if not p:
                has_all_exe = False
                util.debug(f"... No, missing exe {exe}")
            for req in value.get('requires_in_exe_path', []):
                if p and req and str(Path(req)) not in str(Path(p)):
                    has_all_in_exe_path = False
                    util.debug(f"... No, missing path requirement {req}")

        has_vsim_helper = True
        if value.get('requires_vsim_helper', False):
            # This tool name must be in opencos.utils.vsim_helper.TOOL_IS[name].
            # Special case for vsim being used by a lot of tools.
            vsim_helper.init() # only runs checks once internally
            has_vsim_helper = vsim_helper.TOOL_IS.get(name, False)

        has_vscode_helper = True
        needs_vscode_extensions = value.get('requires_vscode_extension', None)
        if needs_vscode_extensions:
            if not isinstance(needs_vscode_extensions, list):
                util.error(
                    f'eda config issue, tool {name}: requires_vscode_extension must be a list'
                )
            else:
                vscode_helper.init() # only runs checks once internally
                has_vscode_helper = all(
                    x in vscode_helper.EXTENSIONS for x in needs_vscode_extensions
                )

        if has_all_exe:
            requires_cmd_list = value.get('requires_cmd', [])
            for cmd in requires_cmd_list:
                cmd_list = shlex.split(cmd)
                try:
                    proc = subprocess.run(cmd_list, capture_output=True, check=False,
                                          input=b'exit\n\n')
                    if proc.returncode != 0:
                        if not quiet:
                            util.debug(f"For tool {name} missing required command",
                                       f"({proc.returncode=}): {cmd_list=}")
                        has_all_exe = False
                except Exception as e:
                    has_all_exe = False
                    util.debug(f"... No, exception {e} running {cmd_list}")


        if all((has_all_py, has_all_env, has_all_exe, has_all_in_exe_path,
                has_vsim_helper, has_vscode_helper)):
            exe = exe_list[0]
            p = shutil.which(exe)
            config['auto_tools_found'][name] = exe # populate key-value pairs w/ first exe in list
            if not quiet:
                util.info(f"Detected {name} ({p}), auto-setting up tool {name}")
            tool_setup(tool=name, quiet=True, auto_setup=True, warnings=warnings, config=config)

    return config


def tool_setup(tool: str, config: dict, quiet: bool = False, auto_setup: bool = False,
               warnings: bool = True):
    ''' Adds items to config["tools_loaded"] (set) and updates config['command_handler'].

    config is potentially updated for entry ['command_handler'][command] with a Tool class.

    Input arg tool can be in the form (for example):
      tool='verlator', tool='verilator=/path/to/verilator.exe'

    '''

    tool = eda_config.update_config_auto_tool_order_for_tool(
        tool=tool, config=config
    )

    if not quiet and not auto_setup:
        util.info(f"Setup for tool: '{tool}'")

    if not tool:
        return

    if tool not in config['auto_tools_order'][0]:
        tools = list(config.get('auto_tools_order', [{}])[0].keys())
        cfg_yaml_fname = config.get('config-yml', None)
        util.error(f"Don't know how to run tool_setup({tool=}), is not in",
                   f"config['auto_tools_order'] for {tools=}",
                   f"from {cfg_yaml_fname}")
        return

    if tool not in config['auto_tools_found']:
        cfg_yaml_fname = config.get('config-yml', None)
        util.error(f"Don't know how to run tool_setup({tool=}), is not in",
                   f"{config['auto_tools_found']=} from {cfg_yaml_fname}")
        return

    if auto_setup and tool is not None and tool in config['tools_loaded']:
        # Do I realy need to warn if a tool was loaded from auto_tool_setup(),
        # but then I also called it via --tool verilator? Only warn if auto_setup=True:
        if warnings:
            util.warning(f"tool_setup: {auto_setup=} already setup for {tool}?")

    entry = config['auto_tools_order'][0].get(tool, {})
    tool_cmd_handler_dict = entry.get('handlers', {})

    for command, str_class_name in tool_cmd_handler_dict.items():
        current_handler_cls = config['command_handler'].get(command, None)

        if auto_setup and current_handler_cls is not None and issubclass(current_handler_cls, Tool):
            # If we're not in auto_setup, then always override (aka arg --tool=<this tool>)
            # skip, already has a tool associated with it, and we're in auto_setup=True
            continue

        cls = util.import_class_from_string(str_class_name)

        assert issubclass(cls, Tool), \
            f'{str_class_name=} is does not have Tool class associated with it'
        util.debug(f'Setting {cls=} for {command=} in config.command_handler')
        config['command_handler'][command] = cls

    config['tools_loaded'].add(tool)


def process_tokens( # pylint: disable=too-many-branches,too-many-statements
        tokens: list, original_args: list, config: dict, is_interactive=False
) -> int:
    '''Returns bash/sh style return code int (0 pass, non-zero fail).

    This is the top level token processing function, and entry point (after util and eda_config
    have performed their argparsing). Tokens can come from command line, DEPS target markup file,
    or interactively. We do one pass through all the tokens, triaging them into:
     - those we can execute immediate (help, quit, and global opens like --debug, --color)
        -- some of this has already been performed in main() by util for --color.
    - a command (sim, synth, etc)
    - command arguments (--seed, +define, +incdir, etc) which will be deferred and processed by
      the command. Some are processed here (--tool)
    '''

    deferred_tokens = []
    command = ""
    run_auto_tool_setup = True

    parser = eda_base.get_argparser()
    try:
        parsed, unparsed = parser.parse_known_args(tokens + [''])
        unparsed = list(filter(None, unparsed))
    except argparse.ArgumentError:
        return util.error(f'problem attempting to parse_known_args for {tokens=}')

    config['tool'] = parsed.tool

    # We support a few way of handling quit, exit, or --quit, --exit, -q
    if parsed.quit or parsed.exit or 'exit' in unparsed or 'quit' in unparsed:
        return util.exit(0)
    if parsed.help or 'help' in unparsed:
        if 'help' in unparsed:
            # We'll figure out the command first before applying help, so
            # usage(tokens, config, command) doesn't have a custom argparser guessing.
            unparsed.remove('help')
            parsed.help = True
    if parsed.eda_safe:
        eda_config.update_config_for_eda_safe(config)

    util.debug(f'eda process_tokens: {parsed=} {unparsed=}')

    # Attempt to get the 'command' in the unparsed args before we've even
    # set the command handlers (some commands don't use tools).
    for value in unparsed:
        if value in config['DEFAULT_HANDLERS'].keys():
            command = value
            if not parsed.tool and value in config['command_tool_is_optional']:
                # only do this if --tool was not set.
                run_auto_tool_setup = False
            unparsed.remove(value) # remove command (flist, export, targets, etc)
            break

    if not is_interactive:
        # Run init_config() now, we deferred it in main(), but only run it
        # for this tool (or tool=None to figure it out)
        config = init_config(
            config, tool=parsed.tool,
            run_auto_tool_setup=run_auto_tool_setup
        )
        if not config:
            util.error(f'eda.py main: problem loading config, {tokens=}')
            return 3

    # Deal with help, now that we have the command (if it was set).
    if parsed.help:
        if not command:
            # if we didn't find the command in config['command_handler'], and
            # since we're entering help anyway (will exit) set command to the
            # first unparsed word looking arg:
            for arg in unparsed:
                if not arg.startswith('-'):
                    command = arg
        return usage(tokens=unparsed, config=config, command=command)

    if parsed.tool:
        tool_setup(parsed.tool, config=config)

    deferred_tokens = unparsed
    if not command:
        util.error("Didn't get a command!")
        return 2

    sco = config['command_handler'][command](config=config) # sub command object
    util.debug(f'{command=}')
    util.debug(f'{sco.config=}')
    util.debug(f'{type(sco)=}')
    if not parsed.tool and \
       command not in config.get('command_determines_tool', []) and \
       command not in config.get('command_tool_is_optional', []):
        use_tool = which_tool(command, config)
        util.info(f"--tool not specified, using default for {command=}: {use_tool}")

    rc = check_command_handler_cls(command_obj=sco, command=command, parsed_args=parsed)
    if rc > 0:
        util.debug(f'Return from main process_tokens({tokens=}), {rc=}, {type(sco)=},'
                   f'unparsed={deferred_tokens}')
        return rc

    # Add the original, nothing-parsed args to the Command.config dict.
    sco.config['eda_original_args'] = original_args

    setattr(sco, 'command_name', command) # as a safeguard, 'command' is not always passed to 'sco'
    unparsed = sco.process_tokens(tokens=deferred_tokens, pwd=os.getcwd())

    # query the status from the Command object (0 is pass, > 0 is fail, but we'd prefer to avoid
    # rc=1 because that's the python exception rc)
    rc = getattr(sco, 'status', 2)
    util.debug(f'Return from main process_tokens({tokens=}), {rc=}, {type(sco)=}, {unparsed=}')
    return rc


def check_command_handler_cls(command_obj:object, command:str, parsed_args) -> int:
    '''Returns bash/sh return code, checks that a command handling class has all

    internal CHECK_REQUIRES list items. For example, sim.py has CHECK_REQUIRES=[Tool],
    so if a 'sim' command handler does not also inherit a Tool class, then reports this as an
    error.
    '''
    sco = command_obj
    for cls in getattr(sco, 'CHECK_REQUIRES', []):
        if not isinstance(sco, cls):
            # If someone set --tool verilator for command=synth, then our 'sco' will have defaulted
            # to CommandSynth with no tool attached. If we don't have a tool set, error and return.
            util.warning(f"{command=} is using handling class '{type(sco)}' (but missing",
                         f"requirement {cls}, likely because we aren't using a derived class",
                         "for a specific tool)")
            parsed_tool = getattr(parsed_args, 'tool', '??')
            return util.error(f"EDA {command=} for tool '{parsed_tool}' is not",
                              f"supported (this tool '{parsed_tool}' cannot run {command=})")
    return 0


# **************************************************************
# **** Interrupt Handler

def signal_handler(sig, frame) -> None: # pylint: disable=unused-argument
    '''Handles Ctrl-C, called by main_cli() if running from command line'''
    util.fancy_stop()
    util.info('Received Ctrl+C...', start='\nINFO: [EDA] ')
    util.exit(-1)

# **************************************************************
# **** Startup Code


def main(*args):
    ''' Returns return code (int), entry point for calling eda.main(*list) directly in py code'''

    args = list(args)
    if len(args) == 0:
        # If not one passed args, then use sys.argv:
        args = sys.argv[1:]

    original_args = args.copy() # save before any parsing.

    # Set global --debug, --quiet, --color  early before parsing other args:
    util_parsed, unparsed = util.process_tokens(args)

    util.debug(f"main: file: {os.path.realpath(__file__)}")
    util.debug(f"main: args: {args=}")

    if util_parsed.version:
        # Do not consider parsed.quiet, print the version and exit:
        print(f'eda {opencos.__version__} ({opencos.__pyproject_name__})')
        sys.exit(0)

    if not util.args['quiet']:
        util.info(f'eda: version {opencos.__version__}')
        # And show the command that was run (all args):
        util.info(f"main: eda {' '.join(args)}; (run from {os.getcwd()})")

    # Handle --config-yml= arg
    config, unparsed = eda_config.get_eda_config(unparsed)

    # Note - we used to call: config = init_config(config=config)
    # However, we now defer calling init_config(..) until eda.process_tokens(..)

    util.info("*** OpenCOS EDA ***")

    if len(args) == 0 or (len(args) == 1 and '--debug' in args):
        # special snowflake case if someone called with a singular arg --debug
        # (without --help or exit)
        util.debug("Starting automatic tool setup: init_config()")
        config = init_config(config=config)
        if not config:
            util.error(f'eda.py main: problem loading config, {args=}')
            return 3
        main_ret = interactive(config=config)
    else:
        main_ret =  process_tokens(
            tokens=list(unparsed), original_args=original_args, config=config
        )
    # Stop the util log, needed for pytests that call eda.main directly that otherwise
    # won't close the log file via util's atexist.register(stop_log)
    util.global_log.stop()
    return main_ret


def main_cli() -> None:
    ''' Returns None, will exit with return code. Entry point for package script or __main__.'''
    signal.signal(signal.SIGINT, signal_handler)
    util.global_exit_allowed = True
    # Strip eda or eda.py from sys.argv, we know who we are if called from __main__:
    rc = main()
    util.exit(rc)


if __name__ == '__main__':
    main_cli()
