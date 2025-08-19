'''opencos.commands.multi - command handler for: eda multi ..., and eda tools-multi ...

These are not intended to be overriden by child classes. They do not inherit Tool classes.
'''

import argparse
import glob
import os
import shutil
from pathlib import Path

from opencos import util, eda_base, eda_config, export_helper, \
    eda_tool_helper
from opencos.eda_base import CommandParallel, get_eda_exec
from opencos.deps.deps_file import get_deps_markup_file, deps_markup_safe_load, \
    deps_data_get_all_targets, deps_list_target_sanitize
from opencos.utils.str_helpers import fnmatch_or_re, dep_str2list

class CommandMulti(CommandParallel):
    '''eda.py command handler for: eda multi <command> <args,targets,target-globs,...>'''

    command_name = 'multi'

    def __init__(self, config: dict):
        CommandParallel.__init__(self, config=config)

        self.multi_only_args = {
            'fake': False,
            'parallel': 1,
            'single-timeout': None,
            'fail-if-no-targets': False,
            'export-jsonl': False,
            'print-targets': False,
        }

        self.args.update(self.multi_only_args)
        self.args_help.update({
            'single-timeout': ('shell timeout on a single operation in multi, not the entire'
                               'multi command'),
            'fail-if-no-targets': 'fails the multi command if no targets were found',
            'export-jsonl': ('If set, generates export.jsonl if possible, spawns single commands'
                             'with --export-json'),
            'print-targets': 'Do not run jobs, prints targets to stdout',
        })
        self.single_command = ''
        self.targets = [] # list of tuples (target:str, tool:str)
        self.resolve_target_command = ''


    def path_hidden_or_work_dir(self, path: str) -> bool:
        '''Returns True if any portion of path is hidden file/dir or has a work-dir

        such as  "eda.work" (self.args['eda-dir'])'''

        path_obj = Path(os.path.abspath(path))
        if self.args['eda-dir'] in path_obj.parts:
            return True
        if any(x.startswith('.') and len(x) > 1 for x in path_obj.parts):
            return True
        return False


    def resolve_target_get_command_level(self, level: int = -1) -> (str, int):
        '''increments level, returns tuple of (command str, level int)'''
        command = self.resolve_target_command
        if level < 0:
            level = 1
        else:
            level += 1
        return command, level


    def resolve_path_and_target_patterns( # pylint: disable=too-many-locals
            self, base_path: str, target: str, level: int = -1
    ) -> dict:
        '''Returns a dict of: key = matching path, value = set of matched targets.

        Looks at globbed paths from base_path/target, and looks for DEPS markup targets
        matching target_pattern (using fnmatch or re.match)
        '''
        def debug(*text):
            util.debug(f'resolve_target() {level=} {base_path=}', *text)

        # join base_path / target
        #   - if target = ./some_path/**/*test
        # split them again so we can do all globbing on the path_pattern portion:
        path_pattern, target_pattern = os.path.split(os.path.join(base_path, target))
        debug(f'{path_pattern=}, {target_pattern=}')

        if target_pattern == '...':
            # replace bazel style target ... with '*' for fnmatch.
            target_pattern = '*'

        matching_targets_dict = {}

        # Let's not glob.glob if the path_pattern and target_pattern are
        # exact, aka if it does not have special characters for glob: * or ?
        # for the target, we also support re, so: * + ?
        if any(x in path_pattern for x in ['*', '?']):
            paths_from_pattern = list(glob.glob(path_pattern, recursive=True))
        else:
            paths_from_pattern = [path_pattern]

        target_pattern_needs_lookup = any(x in target_pattern for x in ['*', '?', '+'])

        # resolve the path_pattern portion using glob.
        # we'll have to check for DEPS markup files in path_pattern, to match the target_wildcard
        # using fnmatch or re.
        for path in paths_from_pattern:

            if self.path_hidden_or_work_dir(path):
                continue

            deps_markup_file = get_deps_markup_file(path)
            if deps_markup_file:
                data = deps_markup_safe_load(deps_markup_file)
                deps_targets = deps_data_get_all_targets(data)
                rel_path = os.path.relpath(path)

                debug(f'in {rel_path=} looking for {target_pattern=} in {deps_targets=}')

                for t in deps_targets:
                    if target_pattern_needs_lookup:
                        matched = fnmatch_or_re(pattern=target_pattern, string=t)
                    else:
                        matched = t == target_pattern
                    if matched:
                        if rel_path not in matching_targets_dict:
                            matching_targets_dict[rel_path] = set()
                        matching_targets_dict[rel_path].add(t)

        debug(f'Found potential targets for {target_pattern=}: {matching_targets_dict=}')
        return matching_targets_dict


    def resolve_target(self, base_path: str, target: str, level: int = -1) -> None:
        '''Returns None, recursively attempts to determine the validity of a base_path/target,

        and appends to self.targets. self.resolve_target_command (str) and level (int) exist
        for debug messaging. Auto-increments 'level' arg, so caller can invoke with
        level=(their_current_level).
        '''

        def debug(*text):
            util.debug(f'resolve_target() {level=} {base_path=}', *text)

        command, level = self.resolve_target_get_command_level(level)

        debug(f"Enter/Start: target={target}, command={command}")

        # Strip outer quote on target, in case it was passed this way from CLI:
        for x in ['"', "'"]:
            target = target.lstrip(x).rstrip(x)

        matching_targets_dict = self.resolve_path_and_target_patterns(
            base_path=base_path, target=target, level=level
        )

        for path, targets in matching_targets_dict.items():
            self.resolve_target_single_path(base_path=path, targets=targets, level=level)


    def resolve_target_single_path( # pylint: disable=too-many-locals
            self, base_path: str, targets: list, level: int = -1
    ) -> None:
        '''Returns None, called by resolve_target(..) if we have a single base_path,

        and multiple targets (list), and need to resolve it via base_path and DEPS.[markup]
        file information. There should be no remaining wildcard information in targets
        (that was handled earlier with fnmatch and re.)
        '''

        def debug(*text):
            util.debug(f'resolve_target() {level=} {base_path=}', *text)

        command, level = self.resolve_target_get_command_level(level)

        all_multi_tools = self.multi_which_tools(command)

        deps_file = get_deps_markup_file(base_path)
        data = {}
        if self.config['deps_markup_supported'] and deps_file:
            data = deps_markup_safe_load(deps_file)

        deps_targets = deps_data_get_all_targets(data)
        deps_file_defaults = data.get('DEFAULTS', {})

        # Loop through all the targets in DEPS.yml, skipping DEFAULTS
        for target_node in targets:
            if target_node not in deps_targets:
                continue

            entry = data[target_node]

            # Since we support a few schema flavors for a target (our
            # 'target_node' key in a DEPS.yml file) santize the entry
            # so it's a {} with a 'deps' key:
            entry_sanitized = deps_list_target_sanitize(
                entry, target_node=target_node, deps_file=deps_file
            )

            # Start with the defaults, and override with this entry_sanitized
            entry_with_defaults = deps_file_defaults.copy()
            entry_with_defaults.update(entry_sanitized)
            entry = entry_with_defaults

            # Because CommandMulti has child CommandToolsMulti, we support multiple tools
            # and have multi ignore waivers tha may only be some of those tools. Keep a list
            # of tools we skip for this target.
            multi_ignore_skip_this_target_node = set() # which tools we'll skip

            # Check if this target_node should be skipped due to:
            # multi - ignore-this-target (commands or tools)
            multi_ignore_commands_list = entry.get('multi', {}).get(
                'ignore-this-target', []
            )

            for x in multi_ignore_commands_list:
                if len(multi_ignore_skip_this_target_node) == len(all_multi_tools):
                    # If we already found a reason to not use this target due to multi - ignore,
                    # on all tools, then stop.
                    break

                assert isinstance(x, dict), \
                    (f'multi ignore-this-target: {x=} {multi_ignore_commands_list=}'
                     f' {deps_file_defaults=} This needs to be a dict entry with keys'
                     f'"commands" and "tools" {deps_file=} {target_node=}')

                commands = x.get('commands', [])
                tools = x.get('tools', [])
                ignore_commands_list = dep_str2list(commands)
                ignore_tools_list = dep_str2list(tools)

                debug(f"{ignore_tools_list=}, {ignore_commands_list=} {target_node=}")
                debug(f"{command=} --> {all_multi_tools=}")
                if not ignore_commands_list or \
                   command in ignore_commands_list or \
                   ignore_commands_list == ['None']:
                    # if commands: None, or commands is blank, then assume it is all commands.
                    # (note that yaml doesn't support *)

                    for tool in all_multi_tools:
                        if tool in ignore_tools_list or ignore_tools_list == ['None'] or \
                           len(ignore_tools_list) == 0:
                            # if tools: None, or is blank, then assume it is for all tools
                            debug(f"Skipping {target_node=} due to using {command=} {tool=}",
                                  f"given {ignore_tools_list=} and {ignore_commands_list=}")
                            multi_ignore_skip_this_target_node.add(tool)

            for tool in all_multi_tools:
                if tool not in multi_ignore_skip_this_target_node:
                    debug(f"Found dep {target_node=} {tool=} matching, {entry=}")
                    self.targets.append( tuple([os.path.join(base_path, target_node), tool]) )


    def process_tokens( # pylint: disable=too-many-locals, too-many-branches, too-many-statements
            self, tokens: list, process_all: bool = True, pwd: str = os.getcwd()
    ) -> list:
        '''CommandMulti.process_tokens(..) is likely the entry point for: eda multi <command> ...

        - handles remaining CLI arguments (tokens list)
        - builds list of jobs in self.jobs and runs them.
        '''
        # multi is special in the way it handles tokens, due to most of them being processed by
        # a subprocess to another eda.Command class (for the command)
        arg_tokens = [] # these are the tokens we will pass to the child eda processes
        command = ""
        target_globs = []
        tool = None
        orig_tokens = tokens.copy()

        # We want to run our built-in argparser on self.args keys, but that would end up
        # parsing args we'd like to pass to individual eda commands from multi, so instead
        # only run it on a subset of our self.args:
        parsed, unparsed = self.run_argparser_on_list(
            tokens=tokens,
            parser_arg_list=list(self.multi_only_args.keys()),
            apply_parsed_args=True
        )

        if parsed.parallel < 1 or parsed.parallel > 256:
            self.error("Arg 'parallel' must be between 1 and 256")

        command = self.get_command_from_unparsed_args(tokens=unparsed)

        # Need to know the tool for this command, either it was set correctly via --tool and/or
        # the command (class) will tell us.
        all_multi_tools = self.multi_which_tools(command)

        single_cmd_unparsed = self.get_unparsed_args_on_single_command(
            command=command, tokens=unparsed
        )

        util.debug(f"Multi: {unparsed=}, looking for target_globs")
        for token in unparsed:
            if token in single_cmd_unparsed:
                target_globs.append(token)
            else:
                arg_tokens.append(token)


        # now we need to expand the target list
        self.single_command = command
        util.debug(f"Multi: {orig_tokens=}")
        util.debug(f"Multi: {command=}")
        util.debug(f"Multi: {self.config=}")
        util.debug(f"Multi: {all_multi_tools=}")
        util.debug(f"Multi: {target_globs=}")
        util.debug(f"Multi: {arg_tokens=}")
        if self.args.get('export-jsonl', False):
            util.info("Multi: --export-jsonl")
        self.targets = []
        cwd = util.getcwd()
        current_targets = 0
        self.resolve_target_command = command
        for target in target_globs:
            self.resolve_target(base_path=cwd, target=target)
            if len(self.targets) == current_targets:
                # we didn't get any new targets, try globbing this one
                for f in glob.glob(target):
                    if os.path.isfile(f):
                        util.info(f"Adding raw file target: {f} for tools {all_multi_tools}")
                        for tool in all_multi_tools:
                            self.targets.append( tuple([f, tool]) )
            current_targets = len(self.targets)
        util.info(f"Multi: Expanded {target_globs} to {len(self.targets)} {command} targets")

        if parsed.fail_if_no_targets and len(self.targets) == 0:
            self.error(f'Multi: --fail-if-no-targets set, and {self.targets=}')
        util.info("Multi: About to run: ", end="")

        def get_pretty_targets_tuple_as_list(l:list):
            # prints 'a(b)', used for 'target(tool)' for tuples in self.targets
            if len(all_multi_tools) > 1:
                return [f'{a.split("/")[-1]}({b})' for a,b in l]

            # don't add the (tool) part if we're only running 1 tool
            return [f'{a.split("/")[-1]}' for a,b in l]

        if len(self.targets) > 20:
            mylist = get_pretty_targets_tuple_as_list(self.targets[:10])
            util.info( ", ".join(mylist), start="", end="")
            util.info( ", ... ", start="", end="")
            mylist = get_pretty_targets_tuple_as_list(self.targets[-10:])
            util.info( ", ".join(mylist), start="")
        else:
            mylist = get_pretty_targets_tuple_as_list(self.targets)
            util.info( ", ".join(mylist), start="")

        if self.args['print-targets']:
            util.info('Multi print-targets (will not run jobs): -->')
            for t in self.targets:
                # t = tuple of (target:str, tool:str), we just want the target.
                print(f'  {t[0]}')
        else:
            util.debug("Multi: converting list of targets into list of jobs")
            self.jobs = []
            self.append_jobs_from_targets(args=arg_tokens)
            self.run_jobs(command)

        # Because CommandMulti has a custom arg parsing, we do not have 'export' related
        # args in self.args (they are left as 'unparsed' for the glob'ed commands)
        # Note that --export-jsonl has already been removed from 'unparsed' and is in parsed,
        # and would already be set in self.args.
        bool_action_kwargs = util.get_argparse_bool_action_kwargs()
        export_parser = argparse.ArgumentParser(prog='eda', add_help=False, allow_abbrev=False)
        for arg,v in self.args.items():
            if arg.startswith('export') and isinstance(v, bool):
                export_parser.add_argument(f'--{arg}', **bool_action_kwargs)
        try:
            export_parsed, export_unparsed = export_parser.parse_known_args(unparsed + [''])
            unparsed = list(filter(None, export_unparsed))
        except argparse.ArgumentError:
            self.error(f'problem attempting to parse_known_args for {unparsed=}')

        for key,value in vars(export_parsed).items():
            if key not in self.args and '_' in key:
                # try with dashes instead of _
                key = key.replace('_', '-')
            if value is None:
                continue
            self.args[key] = value # set one of the parsed 'export' args
            util.info(f'Export: setting arg {key}={value}')

        if self.is_export_enabled():
            self.do_export()

    def which_tool(self, command):
        # Do not use for CommandMulti, b/c we support list of tools.
        raise NotImplementedError

    def multi_which_tools(self, command) -> list:
        '''returns a list, or None, of the tool that was already determined to run the command

        CommandToolsMulti will override and return its own list'''
        return [eda_base.which_tool(command, config=self.config)]

    def _append_job_command_args( # pylint: disable=R0913,R0917 # too-many-arguments
            self, command_list: list, tool: str, all_multi_tools: list, short_target: str,
            command: str
    ) -> None:

        super().update_args_list(args=command_list, tool=tool)
        if self.args.get('export-jsonl', False):
            # Special case for 'multi' --export-jsonl, run reach child with --export-json
            command_list.append('--export-json')
        if tool and len(all_multi_tools) > 1:
            jobname = f'{short_target}.{command}.{tool}'
        else:
            jobname = f'{short_target}.{command}'
        command_list.append(f'--job-name={jobname}')
        logfile = os.path.join(self.args['eda-dir'], f'eda.{jobname}.log')
        command_list.append(f'--force-logfile={logfile}')


    def append_jobs_from_targets(self, args:list):
        '''Helper method in CommandMulti to apply 'args' (list) to all self.targets,

        and add to self.jobs (list) to be run later.
        '''
        eda_path = get_eda_exec('multi')
        command = self.single_command
        timeout = shutil.which('timeout')

        # Built-in support for running > 1 tool.
        all_multi_tools = self.multi_which_tools(command)
        util.info(f'Multi - append_jobs_from_targets: {command=} {all_multi_tools=}')


        for target, tool in self.targets:
            command_list = [ eda_path, command ]

            assert target, f'{target=} {tool=}'

            _, short_target = os.path.split(target) # trim path info on left

            self._append_job_command_args(
                command_list=command_list, tool=tool, all_multi_tools=all_multi_tools,
                short_target=short_target, command=command
            )

            # if self.args['parallel']: command_list += ['--quiet']
            command_list += args # put the args prior to the target.
            command_list += [target]

            # prepend a nix-style 'timeout <seconds>' on the command_list if this was set:
            if timeout and \
               self.args.get('single-timeout', None) and \
               type(self.args['single-timeout']) in [int, str]:
                command_list = ['timeout', str(self.args['single-timeout'])] + command_list

            name = self.get_name_from_target(target)
            if tool and (len(all_multi_tools) > 1 or self.command_name == 'tools-multi'):
                name += f' ({tool})'

            this_job_dict = {
                'name' : name,
                'index' : len(self.jobs),
                'command': command,
                'target': target,
                'command_list' : command_list
            }
            if tool:
                util.debug(f'Multi: append_jobs_from_targets: {tool=} {this_job_dict=}')
            else:
                util.debug(f'Multi: append_jobs_from_targets: {this_job_dict=}')
            self.jobs.append(this_job_dict)


    def do_export(self):
        '''Perform export for a multi/tools-multi command

        For an example command:
            eda multi <command> --export[-jsonl] <args,targets,...>
        '''
        if self.args.get('work-dir', '') == '':
            self.args['work-dir'] = 'eda.work'

        util.info('Multi export: One of the --export[..] flag set, may examine',
                  f'{self.args["work-dir"]=}')
        self.collect_single_exported_export_jsonl()
        util.info('Mulit export: done')


    def collect_single_exported_export_jsonl(self) -> None:
        '''Create a single JSONL or JSON file for all multi jobs'''
        do_as_jsonl = self.args.get('export-jsonl', False)
        do_as_json = self.args.get('export-json', False)

        if not do_as_json and not do_as_jsonl:
            return

        if do_as_jsonl:
            outfile_str = 'export.jsonl'
        else:
            outfile_str = 'export.json'

        command = self.single_command
        all_multi_tools = self.multi_which_tools(command)

        json_file_paths = []
        for target, tool in self.targets:
            # Rather than glob out ALL the possible exported files in our work-dir,
            # only look at the multi targets:
            p, target_nopath = os.path.split(target)
            if not target_nopath:
                target_nopath = p # in case self.targets was missing path info

            if len(all_multi_tools) > 1:
                # Need to look in:
                #   eda.work/<shorttarget>.<command>.<tool>/export/export.json
                # If this was 'eda export' command, then need to look in:
                #   eda.export/......./export.json.
                single_pathname = os.path.join(
                    self.args['work-dir'],
                    f'{target_nopath}.{self.single_command}.{tool}',
                    'export', 'export.json'
                )
            else:
                # We only ran for 1 tool, so the tool value is a dontcare in the output path
                # Need to look in eda.work/<shorttarget>.<command>/export/export.json
                single_pathname = os.path.join(
                    self.args['work-dir'],
                    f'{target_nopath}.{self.single_command}',
                    'export', 'export.json'
                )
            util.debug(f'Looking for export.json in: {single_pathname=}')
            if os.path.exists(single_pathname):
                json_file_paths.append(single_pathname)


        output_json_path = os.path.join(self.args['work-dir'], 'export', outfile_str)
        if len(json_file_paths) == 0:
            self.error(f'{json_file_paths=} is empty list, no targets found to export',
                       f'for {output_json_path=}')
            return

        # TODO(drew): If we ran this w/ several tools from CommandToolsMulti, we'll end up
        # with tests having same name (but different tool). Might need to uniquify the names.
        util.debug(f'Multi export: {json_file_paths=}')
        if do_as_jsonl:
            util.info(f'Multi export: saving JSONL format to: {output_json_path=}')
            export_helper.json_paths_to_jsonl(json_file_paths=json_file_paths,
                                              output_json_path=output_json_path)
        else:
            util.info('Multi export: saving JSON format to: {output_json_path=}')
            export_helper.json_paths_to_single_json(json_file_paths=json_file_paths,
                                                    output_json_path=output_json_path)




class CommandToolsMulti(CommandMulti):
    '''eda.py command handler for: eda tools-multi <args,targets,target-globs,...>

    This class is used to support running a multi-style command, but on many
    tools, such as:
       eda tools-multi sim --tools=verilatr --tools=iverilog *test
    '''

    command_name = 'tools-multi'

    def __init__(self, config: dict):
        super().__init__(config=config)
        self.all_handler_commands = {} # cmd: [ordered list of tools]
        self.tools = set()
        self.args.update({
            'tools': [], # Used for help, will internally use self.tools from argparser.
        })
        self.args_help.update({
            'tools': 'list of tools to run for eda multi targets, such as' \
            + ' --tools=modelsim_ase --tools=verilator=/path/to/bin/verilator',
        })
        if 'tool' in self.args:
            self.args.pop('tool')

        self.update_all_known_tools()

    def update_all_known_tools(self):
        '''Checks whats tools are loaded by opencos.eda, and updates the

        command handlers. This is necessary otherwise we may not run the correct
        tools in a (eda tools-multi <command> --tools=tool1 --tools=tool2 ...) style
        command
        '''
        cfg, tools_loaded = eda_tool_helper.get_config_and_tools_loaded(quiet=True)
        self.all_handler_commands = eda_tool_helper.get_all_handler_commands(cfg, tools_loaded)
        util.debug(f'CommandToolsMulti: {self.all_handler_commands=}')

    def multi_which_tools(self, command):
        '''Overrides CommandMulti.multi_which_tool(command), return a list of all
        possible tools that can run this command'''
        if self.tools is None or not self.tools:
            # wasn't set via arg --tools, so use all if possible for this command.
            which_tools = self.all_handler_commands.get(command, [])
        else:
            # self.tools set from args --tools (list)
            which_tools = [tool for tool in self.all_handler_commands.get(command, []) \
                           if tool in self.tools]
        return which_tools

    def process_tokens(self, tokens: list, process_all: bool = True,
                       pwd: str = os.getcwd()) -> list:

        # setup an argparser to append tools to a list, if no tools set, then use
        # all possible tools (only do this for arg '--tools'):
        parsed, unparsed = self.run_argparser_on_list(
            tokens=tokens,
            parser_arg_list=[
                'tools',
            ],
            apply_parsed_args=False
        )

        if not parsed.tools:
            self.tools = set()
        else:
            # deal with --tools=name=/path/to/name (update config w/ path info):
            self.tools = set(
                eda_config.update_config_auto_tool_order_for_tools(
                    tools=parsed.tools, config=self.config
                )
            )
            util.info(f'CommandToolsMulti: {self.tools=}')
        self.args['tools'] = self.tools

        # Call ComamndMulti's process_tokens:
        return super().process_tokens(
            tokens=unparsed, process_all=process_all, pwd=pwd
        )

    def which_tool(self, command):
        # Do not use for CommandMulti, b/c we support list of tools.
        raise NotImplementedError
