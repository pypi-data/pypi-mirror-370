''' opencos.deps.deps_processor -- module is less about "parsing" and more about "processing"

a DEPS markup files targets (applying deps, reqs, commands, tags, incdirs, defines, etc) to a
CommandDesign ref object
'''

import os

from opencos import files
from opencos import eda_config
from opencos.util import debug, info, warning, error
from opencos.utils.str_helpers import dep_str2list
from opencos.deps.deps_file import deps_target_get_deps_list
from opencos.deps.deps_commands import deps_commands_handler

from opencos.deps.defaults import SUPPORTED_TARGET_TABLE_KEYS, SUPPORTED_TAG_KEYS, \
    SUPPORTED_DEP_KEYS_BY_TYPE

class DepsProcessor: # pylint: disable=too-many-instance-attributes
    '''DepsProcessor -- called by eda_base resolve_target_core(..)

    example usage:
    my_dp = DepsProcessor(
        command_design_ref = self, # aka, your CommandDesign obj
        deps_entry = <some-table-found-in-deps-data>,
        target = <target-str-we-were-looking-for>
        target_path = <filepath, for debug>
        target_node = <target leaf str, for debug>
        deps_file = <original DEPS.[markup-ext] for debug>
        caller_info = <str info for debug>
    )

    '''

    def __init__(self, command_design_ref, deps_entry: dict, target: str,
                 target_path: str, target_node: str, deps_file: str, caller_info: str):
        '''
        command_design_ref (eda.CommandDesign),
        deps_entry (dict, target in DEPS.yml file)
        target_node (str) -- key in DEPS.yml that got us the deps_entry, used for debug
        deps_file (str) -- file, used for debug
        caller_info (str) -- used for debug
        '''

        self.command_design_ref = command_design_ref
        self.deps_entry = deps_entry
        self.target = target
        self.target_path = target_path
        self.target_node = target_node # for debug
        self.deps_file = deps_file # for debug
        self.caller_info = caller_info

        assert isinstance(deps_entry, dict), \
            f'{deps_entry=} for {target_node=} in {deps_file=} must be a dict'
        assert command_design_ref is not None, \
            'called DepsProcessor.__init__, but no ref to CommandDesign object (is None)'

        # named eda commands in the target:
        # If this deps_entry has a 'sim', 'build', etc command entry for this target, grab that
        # because it can set defines or other things specific to an eda command ('sim', for example)
        self.entry_eda_command = self.deps_entry.get(command_design_ref.command_name, {})

        # alias some of the self.command_design_ref values
        self.command_name = self.command_design_ref.command_name # str, for debug
        self.args         = self.command_design_ref.args         # dict
        self.config       = self.command_design_ref.config       # dict
        self.set_arg      = self.command_design_ref.set_arg      # method
        self.error        = self.command_design_ref.error        # method.

        # If there are expanded eda commands in
        # self.command_design_ref.config['command_handler'].keys(), then make note of that now.
        self.known_eda_commands = getattr(
            self.command_design_ref, 'config', {}
        ).get('command_handler', {}).keys()


    def apply_defines(self, defines_dict: dict):
        '''Given defines_dict, applies them to our self.command_design_ref obj'''
        if not isinstance(defines_dict, dict):
            self.error(f"{defines_dict=} is not type dict, can't apply defines,",
                       f"in {self.caller_info}")
        for k,v in defines_dict.items():
            if v is None or v == '':
                self.command_design_ref.process_plusarg(f'+define+{k}')
            else:
                # %PWD% and %SEED% substiutions:
                if v and isinstance(v, str):
                    if v.startswith('%PWD%/') or v.startswith('"%PWD%/'):
                        v = v.replace('%PWD%', os.path.abspath(self.target_path))
                    if v.startswith('%SEED%') or v.startswith('"%SEED%'):
                        v = v.replace('%SEED%', str(self.args.get('seed', 1)))
                self.command_design_ref.process_plusarg(f'+define+{k}={v}')

    def apply_incdirs(self, incdirs_list:list):
        '''Given incdirs_list, applies them to our self.command_design_ref obj'''
        if not isinstance(incdirs_list, (str, list)):
            self.error(f"{incdirs_list=} is not type str/list, can't apply incdirs",
                       f"in {self.caller_info}")
        incdirs_list = dep_str2list(incdirs_list)
        for x in incdirs_list:
            abspath = os.path.abspath(os.path.join(self.target_path, x))
            if abspath not in self.command_design_ref.incdirs:
                self.command_design_ref.incdirs.append(abspath)
                debug(f'Added include dir {abspath} from {self.caller_info}')

    def apply_args(self, args_list:list) -> list:
        '''Given args_list, applies them to our self.command_design_ref obj

        This will return unparsed args that weren't in the self.command_design_ref.args keys
        unparsed args will show up as eda.py warnings, but will not fail. Most callers do not
        use the unparsed args from this method.
        '''
        if not isinstance(args_list, (str, list)):
            self.error(f"{args_list=} is not type str/list, can't apply args",
                       f"in {self.caller_info}")
        tokens = dep_str2list(args_list)
        # We're going to run an ArgumentParser here, which is not the most efficient
        # thing to do b/c it runs on all of self.command_design_ref.args (dict) even
        # if we're applying a single token.
        debug(f'deps_processor - custom apply_args with {tokens=}',
              f'from {self.caller_info}')
        _, unparsed = self.command_design_ref.run_argparser_on_list(
            tokens=tokens
        )
        # Annoying, but check for plusargs in unparsed, and have referenced CommandDesign
        # or CommandSim class handle it with process_plusarg.
        for arg in unparsed:
            if arg.startswith('+'):
                self.command_design_ref.process_plusarg(plusarg=arg, pwd=self.target_path)

        if unparsed:
            # This is only a warning - because things like CommandFlist may not have every
            # one of their self.args.keys() set for a given target, such as a 'sim' target that
            # has --optimize, which is not an arg for CommandFlist. But we'd still like to get an
            # flist from that target.
            warning(f'For {self.command_design_ref.command_name}:' \
                    + f' in {self.caller_info} has unknown args {unparsed=}')
        return unparsed

    def apply_reqs(self, reqs_list:list) -> None:
        '''Given reqs_list, applies them ot our self.command_design_ref obj'''
        for req in reqs_list:
            req_abspath = os.path.abspath(os.path.join(self.target_path, req))
            self.command_design_ref.add_file(
                req_abspath, use_abspath=False, add_to_non_sources=True,
                caller_info=self.caller_info
            )

    def process_deps_entry(self):
        '''Main entry point (after creating DepsProcessor obj) to resolve a deps target

        Example usage:
        deps_processor = DepsProcessor(...)
        deps_targets_to_resolve = deps_processor.process_deps_entry()

        This will return a list of "deps" that haven't been traversed, but are needed by
        the deps_processor entry (the target we're trying to resolve).

        This method will apply all target features to the CommandDesign ref object as
        we traverse.

        Supported target keys:
         -- tags (or equivalent, to support multiple define/incdir/deps for a target)
            -- supports tag-name, with-tools, with-args, args, defines, incdirs, deps
                 ** to be applied if a tool matches.
            -- TODO(drew): other features in docs/DEPS.md not yet implemented.
         -- multi: ignore-this-target: - commands (handled in eda.py CommandMulti.resolve_target)
         -- Named eda commands
            -- (partially done) sim or other eda commands (eda.py command specific things)
                basically, check the command, and apply/merge values to 'entry'?
         -- args
         -- defines
         -- incdirs
         -- top.
         -- commands (not in deps)
         -- deps

        TODO(drew): This does not yet support conditional inclusions based on defines,
         like the old DEPS files did with pattern:
            SOME_DEFINE ?  dep_if_define_present : dep_if_define_not_present
         I would like to deprecate that in favor of 'tags'. However, likely will need
         to walk the entire DEPS.yml once to populate all args/defines, and then re-
         walk them to add/prune the correct tag based dependencies, or rely on it being
         entirely top-down.
        '''

        # DEPS.yml entries have ordered keys, and process these in-order
        # with how the <target> defined it.
        remaining_deps_list = [] # deps items we find that are not yet processed.
        for key in self.deps_entry.keys():

            # Make sure DEPS target table keys are legal:
            if key not in SUPPORTED_TARGET_TABLE_KEYS and \
               key not in self.known_eda_commands:
                error(f'Unknown target {key=} in {self.caller_info},',
                      f' must be one of opencos.deps.defaults.{SUPPORTED_TARGET_TABLE_KEYS=}',
                      f' or an eda command: {self.known_eda_commands}')

            if key == 'tags':
                remaining_deps_list += self.process_tags()
            elif key == 'defines':
                self.process_defines()
            elif key == 'incdirs':
                self.process_incdirs()
            elif key == 'top':
                self.process_top()
            elif key == 'args':
                self.process_args()
            elif key == 'commands':
                self.process_commands()
            elif key == 'reqs':
                self.process_reqs()
            elif key == 'deps':
                remaining_deps_list += self.process_deps_return_discovered_deps()

        # We return the list of deps that still need to be resolved (['full_path/some_target', ...])
        return remaining_deps_list

    def process_tags( # pylint: disable=too-many-statements,too-many-branches,too-many-locals
            self
    ) -> list:
        '''Returns List of added deps, applies tags (dict w/ details, if any) to
        self.command_design_ref.

        Tags are only supported as a Table within a target. Current we only support:
        'args', 'replace-config-tools', 'additive-config-tools', 'with-tools', 'with-args'.
        '''

        deps_tags_enables = self.config.get('dep_tags_enables', {})
        ret_deps_added_from_tags = []

        entry_tags = {} # from yml table
        entry_tags.update(self.deps_entry.get('tags', {}))
        for tagname,value in entry_tags.items():
            debug(f'process_tags(): {tagname=} in {self.caller_info}' \
                  + f' observed: {value=}')
            assert isinstance(value, dict), \
                f'{tagname=} {value=} value must be a dict for in {self.caller_info}'
            tags_dict_to_apply = value.copy()

            for key in value.keys():
                if key not in SUPPORTED_TAG_KEYS:
                    self.error(f'{tagname=} in {self.caller_info}:',
                               f'has unsupported {key=} {SUPPORTED_TAG_KEYS=}')

            enable_tags_matched = False
            disable_tags_matched = False
            if tagname in self.command_design_ref.args['enable-tags']:
                # tagname was force enabled by --enable-tags=tagname.
                debug(f'process_tags(): {tagname=} in {self.caller_info=}',
                      'will be enabled, matched in --enable-tags:',
                      f'{self.command_design_ref.args["enable-tags"]}')
                enable_tags_matched = True
            if tagname in self.command_design_ref.args['disable-tags']:
                # tagname was force disabled by --disable-tags=tagname.
                debug(f'process_tags(): {tagname=} in {self.caller_info=}',
                      'will be disabled, matched in disable-tags:',
                      f'{self.command_design_ref.args["disable-tags"]}')
                disable_tags_matched = True


            apply_tag_items_tools = False
            apply_tag_items_with_args = False

            tool = self.args.get('tool', None)

            if disable_tags_matched or enable_tags_matched:
                # skip checking with-tools or with-args, b/c we are already
                # force matched by tagname from --enable-tags or --disable-tags.
                pass
            else:

                with_tools = dep_str2list(value.get('with-tools', []))
                if with_tools and not deps_tags_enables.get('with-tools', None):
                    with_tools = []
                    warning(f'{tagname=} in {self.caller_info}:',
                            ' skipped due to with-tools disabled.')

                with_args = value.get('with-args', {})
                if not isinstance(with_args, dict):
                    error(f'{tagname=} in {self.caller_info}:',
                          ' with-args must be a table (dict) of key-value pairs')
                if with_args and not deps_tags_enables.get('with-args', None):
                    with_args = {}
                    warning(f'{tagname=} in {self.caller_info}:',
                            ' skipped due to with-args disabled.')

                # check with-tools?
                if not with_tools:
                    apply_tag_items_tools = True # no with-tools present
                elif tool in with_tools:
                    apply_tag_items_tools = True # with-tools present and we matched.
                else:
                    # Each item of with-tools can also be in the form
                    # {tool (str)}:{TOOL.tool_version (str)}
                    # this matches Tool.get_full_tool_and_versions()
                    if getattr(self.command_design_ref, 'get_full_tool_and_versions', None):
                        tool_full_version = self.command_design_ref.get_full_tool_and_versions()
                        if tool_full_version and tool_full_version in with_tools:
                            apply_tag_items_tools = True

                # check with-args?
                with_args_matched_list = []
                for k,v in with_args.items():
                    with_args_matched_list.append(False)
                    if not apply_tag_items_tools:
                        # If we didn't previously match with-tools (if with-tools was present),
                        # then we may not match the args, b/c those are tool dependend in the
                        # Command handling class.
                        pass
                    elif k not in self.command_design_ref.args:
                        warning(f'{tagname=} in {self.caller_info}:',
                                f'with-args key {k} is not a valid arg for {tool=}')
                    elif not isinstance(v, type(self.command_design_ref.args[k])):
                        warning(f'{tagname=} in {self.caller_info}:',
                                f' with-args table key {k} value {v} (type {type(v)}) does not',
                                f' match type in args (type {self.command_design_ref.args[k]})')
                    elif self.command_design_ref.args[k] == v:
                        # set it as matched:
                        with_args_matched_list[-1] = True
                        debug(f'{tagname=} in {self.caller_info}:',
                              f' with-args table key {k} value {v} matched')
                    else:
                        debug(f'{tagname=} in {self.caller_info}:',
                              f'with-args table key {k} value {v} did not match args value: ',
                              f'{self.command_design_ref.args[k]}')

                if not with_args_matched_list:
                    apply_tag_items_with_args = True # no with-args set
                else:
                    apply_tag_items_with_args = all(with_args_matched_list)

            # Did we match all with-tools and with-args?
            if disable_tags_matched:
                apply_tag_items = False
            elif enable_tags_matched:
                apply_tag_items = True
            else:
                apply_tag_items = apply_tag_items_tools and apply_tag_items_with_args

            if not apply_tag_items:
                debug(f'process_tags(): {tagname=} in {self.caller_info}',
                      f'skipped for {tool=}, {with_args=}, {with_args_matched_list=}')
            elif apply_tag_items_tools or apply_tag_items_with_args:
                debug(f'process_tags(): {tagname=} in {self.caller_info=}',
                      f'applying tags for {tool=}, {with_args=}, {with_args_matched_list=},',
                      f'{tags_dict_to_apply.keys()=}')


            if apply_tag_items:
                # We have matched something (with-tools, etc).
                # apply these in the original order of the keys:
                for key in tags_dict_to_apply.keys():

                    if key == 'defines':
                        # apply defines:
                        self.apply_defines(value.get('defines', {}))

                    elif key == 'incdirs':
                        # apply incdirs:
                        self.apply_incdirs(value.get('incdirs', []))

                    elif key == 'args':
                        # apply args
                        args_list = dep_str2list(value.get('args', []))
                        if args_list and not deps_tags_enables.get('args', None):
                            args_list = []
                            warning(f'{tagname=} in {self.caller_info=}:',
                                    ' skipped args due to args disabled.')
                        if args_list:
                            # This will apply knowns args to the target dep:
                            info(f'{tagname=} in {self.caller_info=}:',
                                 f'applying args b/c {with_tools=} for {args_list=}')
                            self.apply_args(args_list)

                    elif key == 'reqs':
                        reqs_list = deps_target_get_deps_list(entry=value,
                                                              default_key='reqs',
                                                              target_node=self.target_node,
                                                              deps_file=self.deps_file)
                        self.apply_reqs(reqs_list)

                    elif key == 'deps':

                        # apply deps (includes commands, stray +define+ +incdir+)
                        # treat the same way we treat self.process_deps_return_discovered_deps
                        deps_list = deps_target_get_deps_list(entry=value,
                                                              default_key='deps',
                                                              target_node=self.target_node,
                                                              deps_file=self.deps_file)
                        ret_deps_added_from_tags += self.get_remaining_and_apply_deps(deps_list)

                # for replace-config-tools or additive-config-tools from tags, these don't need to
                # handle in order of tags keys:

                # apply replace-config-tools
                # This will replace lists (compile-waivers).
                tool_config = value.get('replace-config-tools', {}).get(tool, None)
                if tool_config and not deps_tags_enables.get('replace-config-tools', None):
                    tool_config = None
                    warning(f'{tagname=} in {self.caller_info}:',
                            ' skipped replace-config-tools b/c it is disabled.')
                if tool_config and isinstance(tool_config, dict):
                    # apply it to self.tool_config:
                    info(f'{tagname=} in {self.caller_info}:',
                         f'applying replace-config-tools for {tool=}: {tool_config}')
                    eda_config.merge_config(self.command_design_ref.tool_config, tool_config)
                    # Since we altered command_design_ref.tool_config, need to call update on it:
                    self.command_design_ref.update_tool_config()
                    debug(f'{tagname=} in {self.caller_info}:',
                          'Updated {self.command_design_ref.tool_config=}')

                # apply additive-config-tools
                # This will append to lists (compile-waivers)
                tool_config = value.get('additive-config-tools', {}).get(tool, None)
                if tool_config and not deps_tags_enables.get('additive-config-tools', None):
                    tool_config = None
                    warning(f'{tagname=} in {self.caller_info}:',
                            ' skipped additive-config-tools b/c it is disabled.')
                if tool_config and isinstance(tool_config, dict):
                    # apply it to self.tool_config:
                    info(f'{tagname=} in {self.caller_info}:',
                         f'applying additive-config-tools for {tool=}: {tool_config}')
                    eda_config.merge_config(self.command_design_ref.tool_config, tool_config,
                                            additive_strategy=True)
                    # Since we altered command_design_ref.tool_config, need to call update on it:
                    self.command_design_ref.update_tool_config()
                    debug(f'{tagname=} in {self.caller_info}:',
                          f'Updated {self.command_design_ref.tool_config=}')

        return ret_deps_added_from_tags


    def process_defines(self):
        '''Returns None, applies defines (dict, if any) from self.deps_entry to
        self.command_design_ref.'''

        # Defines:
        # apply command specific defines, with higher priority than the a
        # deps_entry['sim']['defines'] entry,
        # do this with dict1.update(dict2):
        entry_defines = {}
        entry_defines.update(self.deps_entry.get('defines', {}))
        entry_defines.update(self.entry_eda_command.get('defines', {}))
        assert isinstance(entry_defines, dict), \
            f'{entry_defines=} for in {self.caller_info} must be a dict'

        self.apply_defines(entry_defines)

    def process_incdirs(self) -> None:
        '''Returns None, applies incdirs (dict, if any) from self.deps_entry to
        self.command_design_ref.'''

        entry_incdirs = []
        # apply command specific incdirs, higher in the incdir list:
        entry_incdirs = dep_str2list(self.entry_eda_command.get('incdirs', []))
        entry_incdirs += dep_str2list(self.deps_entry.get('incdirs', []))
        assert isinstance(entry_incdirs, list), \
            f'{entry_incdirs=} for in {self.caller_info} must be a list'
        self.apply_incdirs(entry_incdirs)

    def process_top(self) -> None:
        '''Returns None, applies top (str, if any) from self.deps_entry to
        self.command_design_ref.'''

        if self.args['top'] != '':
            return # already set

        # For 'top', we overwrite it if not yet set.
        # the command specific 'top' has higher priority.
        entry_top = self.entry_eda_command.get('top', '') # if someone set target['sim']['top']
        if entry_top == '':
            entry_top = self.deps_entry.get('top', '') # if this target has target['top'] set

        if entry_top != '':
            if self.args['top'] == '':
                # overwrite only if unset - we don't want other deps overriding the topmost
                # target's setting for 'top'.
                self.set_arg('top', str(entry_top))

    def process_args(self) -> None:
        '''Returns None, applies args (list or str, if any) from self.deps_entry to
        self.command_design_ref.'''

        # for 'args', process each. command specific args take higher priority that target args.
        # run_argparser_on_list: uses argparse, which takes precedence on the last arg that is set,
        # so put the command specific args last.
        # Note that if an arg is already set, we do NOT update it
        args_list = dep_str2list(self.deps_entry.get('args', []))
        args_list += dep_str2list(self.entry_eda_command.get('args', []))

        # for args_list, re-parse these args to apply them to self.args.
        if not args_list:
            return

        debug(f'in {self.caller_info}: {args_list=}')
        self.apply_args(args_list)

        # TODO(drew): Currently, I can't support changing the 'config' via an arg encountered in
        # DEPS.yml. This is prevented b/c --config-yml appears as a modifed arg no matter what
        # (and we don't let DEPS.yml override modifed args, otherwise a target would override the
        # user command line).


    def get_commands( # pylint: disable=dangerous-default-value
            self, commands: list = [], dep: str = ''
    ) -> (list, list):
        '''Returns tuple of (shell_commands_list, work_dir_add_srcs_list).

        Does not have side effects on self.command_design_ref.
        '''

        default_ret = [], []

        if not commands:
            # if we weren't passed commands, then get them from our target (self.deps_entry)
            commands = self.deps_entry.get('commands', [])

        assert isinstance(commands, list), f'{self.deps_entry=} has {commands=} type is not list'

        if not commands: # No commands in this target
            return default_ret

        debug(f"Got {self.deps_entry=} for in {self.caller_info}, has {commands=}")
        shell_commands_list = [] # list of dicts
        work_dir_add_srcs_list = [] # list of dicts

        if not dep:
            # if we weren't passed a dep, then use our target_node (str key for our self.deps_entry)
            dep = self.target_node

        # Run handler for this to convert to shell commands in self.command_design_ref
        shell_commands_list, work_dir_add_srcs_list = deps_commands_handler(
            config=self.command_design_ref.config,
            eda_args=self.command_design_ref.args,
            dep=dep,
            deps_file=self.deps_file,
            target_node=self.target_node,
            target_path=self.target_path,
            commands=commands
        )

        return shell_commands_list, work_dir_add_srcs_list

    def process_commands( # pylint: disable=dangerous-default-value
            self, commands: list = [], dep: str = ''
    ) -> None:
        '''Returns None, handles commands (shell, etc) in the target that aren' in the 'deps' list.

        Applies these to self.command_design_ref.

        You can optionally call this with a commands list and a single dep, which we support for
        commands lists that exist within the 'deps' entry of a target.
        '''

        shell_commands_list, work_dir_add_srcs_list = self.get_commands(commands=commands, dep=dep)

        # add these commands lists to self.command_design_ref:
        # Process all shell_commands_list:
        # This will track each shell command with its target_node and target_path
        self.command_design_ref.append_shell_commands( cmds=shell_commands_list )
        # Process all work_dir_add_srcs_list:
        # This will track each added filename with its target_node and target_path
        self.command_design_ref.append_work_dir_add_srcs( add_srcs=work_dir_add_srcs_list,
                                                          caller_info=self.caller_info )


    def process_reqs(self) -> None:
        '''Process any 'reqs:' table in a DEPS markup entry'''
        reqs_list = deps_target_get_deps_list(entry=self.deps_entry,
                                              default_key='reqs',
                                              target_node=self.target_node,
                                              deps_file=self.deps_file)
        self.apply_reqs(reqs_list)


    def process_deps_return_discovered_deps(self) -> list:
        '''Returns list of deps targets to continue processing,

        -- iterates through 'deps' for this target (self.deps_entry['deps'])
        -- applies to self.command_design_ref
        '''

        # Get the list of deps from this entry (entry is a target in our DEPS.yml):
        deps = deps_target_get_deps_list(
            self.deps_entry,
            target_node=self.target_node,
            deps_file=self.deps_file
        )
        return self.get_remaining_and_apply_deps(deps)

    def get_remaining_and_apply_deps(self, deps:list) -> list:
        '''Given a list of deps, process what is supported in a "deps:" table in DEPS
        markup file.'''

        deps_targets_to_resolve = []

        # Process deps (list)
        for dep in deps:

            typ = type(dep)
            if typ not in SUPPORTED_DEP_KEYS_BY_TYPE:
                self.error(f'{self.target_node=} {dep=} in {self.deps_file=}:' \
                           + f'has unsupported {type(dep)=} {SUPPORTED_DEP_KEYS_BY_TYPE=}')

            for supported_values in SUPPORTED_DEP_KEYS_BY_TYPE.values():
                if '*' in supported_values:
                    continue
                if typ in [dict,list] and any(k not in supported_values for k in dep):
                    self.error(
                        f'{self.target_node=} {dep=} in {self.deps_file=}: has dict-key or',
                        f'list-item not in {SUPPORTED_DEP_KEYS_BY_TYPE[typ]=}'
                    )

            # In-line commands in the deps list, in case the results need to be in strict file
            # order for other deps
            if isinstance(dep, dict) and 'commands' in dep:

                commands = dep['commands']
                debug(f"Got commands {dep=} for in {self.caller_info}, {commands=}")

                assert isinstance(commands, list), \
                    f'dep commands must be a list: {dep=} in {self.caller_info}'

                # For this, we need to get the returned commands (to keep strict order w/ other
                # deps)
                command_tuple = self.get_commands( commands=commands, dep=dep )
                # TODO(drew): it might be cleaner to return a dict instead of list, b/c those
                # are also ordered and we can pass type information, something like:
                deps_targets_to_resolve.append(command_tuple)


            elif isinstance(dep, str) and any(dep.startswith(x) for x in ['+define+', '+incdir']):
                # Note: we still support +define+ and +incdir in the deps list.
                # check for compile-time Verilog style plusarg, which are supported under targets
                # These are not run-time Verilog style plusargs comsumable from within the .sv:
                debug(f"Got plusarg (define, incdir) {dep=} for {self.caller_info}")
                self.command_design_ref.process_plusarg(plusarg=dep, pwd=self.target_path)

            else:
                # If we made it this far, dep better be a str type.
                assert isinstance(dep, str), f'{dep=} {type(dep)=} must be str'
                dep_path = os.path.join(self.target_path, dep)
                debug(f"Got dep {dep_path=} for in {self.caller_info}")

                if dep_path in self.command_design_ref.targets_dict or \
                   dep_path in deps_targets_to_resolve:
                    debug(" - already processed, skipping")
                else:
                    file_exists, _, _ = files.get_source_file(dep_path)
                    if file_exists:
                        debug(" - raw file, adding to return list...")
                        deps_targets_to_resolve.append(dep_path) # append, keeping file order.
                    else:
                        debug(" - a target (not a file) needing to be resolved, adding to return",
                              "list...")
                        deps_targets_to_resolve.append(dep_path) # append, keeping file order.

        # We return the list of deps or files that still need to be resolved
        # (['full_path/some_target', ...])
        # items in this list are either:
        #  -- string (dep or file)
        #  -- tuple (unprocessed commands, in form: (shell_commands_list, work_dir_add_srcs_list))
        # TODO(drew): it might be cleaner to return a dict instead of list, b/c those are also
        # ordered and we can pass type information, something like:
        #  { dep1: 'file',
        #    dep2: 'target',
        #    dep3: 'command_tuple',
        #  }
        return deps_targets_to_resolve
