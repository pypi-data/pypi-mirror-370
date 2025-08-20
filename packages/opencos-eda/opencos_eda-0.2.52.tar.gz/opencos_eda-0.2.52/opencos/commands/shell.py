'''opencos.commands.shell - Base class command handler for: eda shell ...

Not intended to be overriden by Tool based classes.'''

# Note - tricky to eliminate it with inheritance when calling reusable methods.
# pylint: disable=R0801

# TODO(drew): clean up CommandShell.check_logs_for_errors and CommandShell.run_commands_check_logs
#   These also share a lot with CommandSim.* methods, so consider refactoring to share code,
#   for example, CommandShell.do_export could move to CommandDesign, and derived classes
#   set the allow-listed args to pass to export.
# pylint: disable=too-many-arguments,too-many-positional-arguments

import os

from opencos import util, export_helper
from opencos.eda_base import CommandDesign

from opencos.utils import status_constants


class CommandShell(CommandDesign):
    '''Base class command handler for: eda sim ...'''

    command_name = 'shell'

    def __init__(self, config: dict):
        CommandDesign.__init__(self, config=config)
        self.args.update({
            'pass-pattern': "",
            'log-bad-strings': [],
            'log-must-strings': [],
        })
        self.args_help.update({
            'log-bad-strings': (
                'strings that if present in the log will cause an `eda shell` error'
            ),
            'log-must-strings': (
                'strings that are required by the log to not-fail the `eda shell` call'
            ),
            'pass-pattern': (
                'Additional string required to pass the `eda shell` call, appends to'
                ' log-must-strings'
            ),
        })

    def process_tokens(self, tokens: list, process_all: bool = True,
                       pwd: str = os.getcwd()) -> list:
        unparsed = CommandDesign.process_tokens(
            self, tokens=tokens, process_all=process_all, pwd=pwd
        )

        if self.status_any_error():
            return unparsed

        if self.args['top']:
            # create our work dir
            self.create_work_dir()
            self.run_dep_commands()
            self.do_it()
        return unparsed


    def run_commands_check_logs( # pylint: disable=dangerous-default-value
            self, commands: list , check_logs: bool = True, log_filename=None,
            bad_strings: list = [],
            must_strings: list = [],
            use_bad_strings: bool = True, use_must_strings: bool = True
    ) -> None:
        '''Returns None, runs all commands (each element is a list) and checks logs

        for bad-strings and must-strings (args or class member vars)
        '''

        for obj in commands:

            assert isinstance(obj, list), \
                (f'{self.target=} command {obj=} is not a list or util.ShellCommandList,'
                 ' not going to run it.')

            clist = list(obj).copy()
            tee_fpath = getattr(obj, 'tee_fpath', None)

            util.debug(f'run_commands_check_logs: {clist=}, {tee_fpath=}')

            log_fname = None
            if tee_fpath:
                log_fname = tee_fpath
            if log_filename:
                log_fname = log_filename

            self.exec(work_dir=self.args['work-dir'], command_list=clist, tee_fpath=tee_fpath)

            if check_logs and log_fname:
                self.check_logs_for_errors(
                    filename=log_fname, bad_strings=bad_strings, must_strings=must_strings,
                    use_bad_strings=use_bad_strings, use_must_strings=use_must_strings
                )


    def do_export(self) -> None:
        '''CommandShell helper for handling args --export*

        We allow commands such as: eda shell --export <target>
        '''

        out_dir = os.path.join(self.args['work-dir'], 'export')

        target = self.target
        if not target:
            target = 'test'

        export_obj = export_helper.ExportHelper(
            cmd_design_obj=self,
            eda_command=self.command_name,
            out_dir=out_dir,
            # Note this may not be the correct target for debug infomation,
            # so we'll only have the first one.
            target=target
        )

        # Set things in the exported: DEPS.yml
        tool = self.args.get('tool', None)
        # Certain args are allow-listed here
        deps_file_args = []
        for a in self.get_command_line_args():
            if any(a.startswith(x) for x in [
                    '--log-must',
                    '--log-bad',
                    '--pass-pattern']):
                deps_file_args.append(a)

        export_obj.run(
            deps_file_args=deps_file_args,
            export_json_eda_config={
                'tool': tool,
            }
        )

        if self.args['export-run']:

            # remove the '--export' named args, we don't want those.
            args_no_export = self.get_command_line_args(remove_args_startswith=['export'])

            command_list = ['eda', self.command_name] + args_no_export + [target]

            util.info(f'export-run: from {export_obj.out_dir=}: {command_list=}')
            self.exec(
                work_dir=export_obj.out_dir,
                command_list=command_list,
            )


    def do_it(self) -> None:
        self.write_eda_config_and_args()

        if self.is_export_enabled():
            # If we're exporting the target, we do NOT run the test here
            # (do_export() may run the test in a separate process and
            # from the out_dir if --export-run was set)
            self.do_export()


    def check_logs_for_errors( # pylint: disable=dangerous-default-value
            self, filename: str,
            bad_strings: list = [], must_strings: list = [],
            use_bad_strings: bool = True, use_must_strings: bool = True
    ) -> None:
        '''Returns None, checks logs using args bad_strings, must_strings,

        and internals self.args["log-[bad|must]-strings"] (lists).
        '''

        _bad_strings = bad_strings
        _must_strings = must_strings
        # append, if not they would 'replace' the args values:
        if use_bad_strings:
            _bad_strings = bad_strings + self.args.get('log-bad-strings', [])
        if use_must_strings:
            _must_strings = must_strings + self.args.get('log-must-strings', [])

        if self.args['pass-pattern'] != "":
            _must_strings.append(self.args['pass-pattern'])

        if len(_bad_strings) > 0 or len(_must_strings) > 0:
            hit_must_string_dict = dict.fromkeys(_must_strings)
            fname = os.path.join(self.args['work-dir'], filename)
            with open(fname, 'r', encoding='utf-8') as f:
                for lineno, line in enumerate(f):
                    if any(must_str in line for must_str in _must_strings):
                        for k, _ in hit_must_string_dict.items():
                            if k in line:
                                hit_must_string_dict[k] = True
                    if any(bad_str in line for bad_str in _bad_strings):
                        self.error(
                            f"log {fname}:{lineno} contains one of {_bad_strings=}",
                            error_code=status_constants.EDA_SHELL_LOG_HAS_BAD_STRING
                        )

            if any(x is None for x in hit_must_string_dict.values()):
                self.error(
                    f"Didn't get all passing patterns in log {fname}: {_must_strings=}",
                    f" {hit_must_string_dict=}",
                    error_code=status_constants.EDA_SHELL_LOG_MISSING_MUST_STRING
                )
