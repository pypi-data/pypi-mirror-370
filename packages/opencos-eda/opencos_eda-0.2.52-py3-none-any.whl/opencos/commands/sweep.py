'''opencos.commands.sweep - command handler for: eda sweep ...

These are not intended to be overriden by child classes. They do not inherit Tool classes.
'''

import os
import re

from opencos import util
from opencos.eda_base import CommandDesign, CommandParallel, get_eda_exec, which_tool
from opencos.utils.str_helpers import strip_outer_quotes

class CommandSweep(CommandDesign, CommandParallel):
    '''Command handler for: eda sweep ...'''

    command_name = 'sweep'

    def __init__(self, config:dict):
        CommandDesign.__init__(self, config=config)
        CommandParallel.__init__(self, config=config)
        self.sweep_target = ''
        self.single_command = ''
        self.args.update({
            'sweep': []
        })
        self.args_help.update({
            "sweep": ("List append arg, where range or value expansion is peformed on the RHS:"
                      " --sweep='--arg0=(start,last,iter=1)' "
                      " --sweep='--arg1=[val0,val1,val2,...]' "
                      " --sweep='+define+NAME0=(start,last,iter=1)' "
                      " --sweep='+define+NAME1=[val0,val1,val2,...]' "
                      " --sweep='+define+[NAME0,NAME1,NAME2,...]' ."
                      " Note that range expansion of (1,4) will expand to values [1,2,3,4]."
                      ),
        })


    def check_args(self) -> None:
        '''Returns None, checks self.args (use after args parsed)'''
        if self.args['parallel'] < 1 or self.args['parallel'] > 256:
            self.error(f"Arg {self.args['parallel']=} must be between 1 and 256")

    def _append_sweep_args(self, arg_tokens: list) -> None:
        '''Modifies list arg_tokens, using known top-level args'''
        tool = which_tool(command=self.single_command, config=self.config)
        super().update_args_list(args=arg_tokens, tool=tool)


    def process_tokens(
            self, tokens: list, process_all: bool = True,
            pwd: str = os.getcwd()
    ) -> list:
        '''CommandSweep.process_tokens(..) is likely the entry point for: eda sweep <command> ...

        - handles remaining CLI arguments (tokens list)
        - builds sweep_axis_list to run multiple jobs for the target
        '''

        # 'sweep' is special in the way it handles tokens, due to most of them being processed by
        # a sub instance
        sweep_axis_list = []
        arg_tokens = []

        _, unparsed = self.run_argparser_on_list(
            tokens=tokens,
            parser_arg_list=[
                'parallel',
                'sweep',
            ],
            apply_parsed_args=True
        )

        self.check_args()

        self.single_command = self.get_command_from_unparsed_args(tokens=unparsed)

        self._append_sweep_args(arg_tokens=arg_tokens)

        for sweep_arg_value in self.args['sweep']:
            # Deal with --sweep= args we already parsed, but haven't expanded yet.
            sweep_arg_value = strip_outer_quotes(sweep_arg_value)
            sweep_axis_list_entry = self._process_sweep_arg(sweep_arg_value=sweep_arg_value)
            if sweep_axis_list_entry:
                sweep_axis_list.append(sweep_axis_list_entry)


        # command, --parallel, and --sweep already processed by argparse,
        # let's tentatively parse what the child jobs cannot consume.
        # Whatever is leftover is either an eda target, or another unparsed token.
        single_cmd_unparsed = self.get_unparsed_args_on_single_command(
            command=self.single_command, tokens=unparsed
        )

        for token in unparsed:
            if token in single_cmd_unparsed:

                if self.resolve_target(token, no_recursion=True):
                    if self.sweep_target:
                        self.error("Sweep can only take one target, already got",
                                   f"{self.sweep_target} now getting {token}")
                    self.sweep_target = token
                else:
                    # If we don't know what to do with it, pass it to downstream
                    arg_tokens.append(token)

            else:
                # If it wasn't in single_cmd_unparsed, then it can definitely be
                # consumed downstream
                arg_tokens.append(token)


        # now we need to expand the target list
        util.debug(f"Sweep: command:    '{self.single_command}'")
        util.debug(f"Sweep: arg_tokens: '{arg_tokens}'")
        util.debug(f"Sweep: target:     '{self.sweep_target}'")

        if not self.sweep_target:
            self.error(f"Sweep can only take one target, found none, args: {unparsed}")

        # now create the list of jobs, support one axis
        self.jobs = []

        self.expand_sweep_axis(arg_tokens=arg_tokens, sweep_axis_list=sweep_axis_list)
        self.run_jobs(command=self.single_command)
        return [] # we used all of unparsed.


    @staticmethod
    def _process_sweep_arg(sweep_arg_value: str) -> dict:
        '''If processed, returns a non-empty dict. Handles processing of --sweep=VALUE

        Where VALUE could be one of:
           --arg0=(1,4)
           --arg1=[val0,val1]
           +define+NAME0=[val0,val1]

        Return value is {} or {'lhs': str, 'operator': str (+ or =), 'values': list}
        '''

        sweep_arg_value = strip_outer_quotes(sweep_arg_value)

        util.debug(f'{sweep_arg_value=}')
        # Try to match a sweep range expansion:
        #   --sweep='--arg0=(1,4)'
        #   --sweep='--arg0=(1,4,1)'
        #   --sweep='+define+NAME0=(1,4,1)'
        m = re.match(
            r'(.*)(\=) \(  ([\d\.]+)  \,  ([\d\.]+)  (\, ([\d\.]+) )?  \)'.replace(' ',''),
            sweep_arg_value
        )
        if m:
            lhs = m.group(1)
            operator = m.group(2)
            sweep_axis_values = []
            if m.group(5):
                rhs_range_iter = int(m.group(6))
            else:
                rhs_range_iter = 1
            for v in range(int(m.group(3)), int(m.group(4)) + 1, rhs_range_iter):
                sweep_axis_values.append(v)
            util.debug(f"Sweep axis: {lhs} {operator} {sweep_axis_values}")
            return {
                'lhs': lhs,
                'operator': operator,
                'values': sweep_axis_values,
            }

        # Try to match a sweep list value expansion:
        #   --sweep='--arg0=[1,2]'
        #   --sweep='--arg1=[3,4,5,6]'
        #   --sweep='+define+NAME=[8,9]'
        #   --sweep='+define+[NAME0,NAME1,NAME2]'
        #   --sweep='+define+[NAME0=1,NAME1=22,NAME2=46]'
        m = re.match(
            r'(.*)([\=\+]) \[  ([^\]]+) \] '.replace(' ',''),
            sweep_arg_value
        )
        if m:
            sweep_axis_values = []
            lhs = m.group(1)
            operator = m.group(2)
            for v in m.group(3).split(','):
                sweep_axis_values.append(v)
            util.debug(f"Sweep axis: {lhs} {operator} {sweep_axis_values}")
            return {
                'lhs': lhs,
                'operator': operator,
                'values': sweep_axis_values,
            }

        util.warning(f'Ignored unprocessed expansion for --sweep={sweep_arg_value}')
        return {}


    def expand_sweep_axis(
            self, arg_tokens: list, sweep_axis_list: list, sweep_string: str = ""
    ) -> None:
        '''Returns None, appends jobs to self.jobs to be run by CommandParallel.run_jobs(..)'''

        util.debug(f"Entering expand_sweep_axis: command={self.single_command},",
                   f"target={self.sweep_target}, arg_tokens={arg_tokens},",
                   f"sweep_axis_list={sweep_axis_list}")
        if not sweep_axis_list:
            # we aren't sweeping anything, create one job:
            # name {target}.{command}[.sweep_value,.sweep_value,...]
            snapshot_name = self.get_name_from_target(self.sweep_target)
            snapshot_name = snapshot_name.replace(os.sep, '_') \
                + f'.{self.single_command}{sweep_string}'
            eda_path = get_eda_exec('sweep')
            logfile = os.path.join(self.args['eda-dir'], f'eda.{snapshot_name}.log')
            self.jobs.append({
                'name' : snapshot_name,
                'index' : len(self.jobs),
                'command': self.single_command,
                'target': self.sweep_target,
                'command_list' : (
                    [
                        eda_path, self.single_command, self.sweep_target,
                        f'--job-name={snapshot_name}',
                        f'--force-logfile={logfile}',
                    ] + arg_tokens
                )
            })
            return

        sweep_axis = sweep_axis_list.pop(0)
        lhs = sweep_axis['lhs']
        operator = sweep_axis['operator']

        lhs_trimmed = lhs.replace('-', '').replace('+', '').replace('=', '')

        for v in sweep_axis['values']:
            this_arg_tokens = arg_tokens.copy()
            this_arg_tokens.append(f'{lhs}{operator}{v}')

            v_string = f"{v}".replace('.','p')
            this_sweep_string = sweep_string + f".{lhs_trimmed}_{v_string}"

            self.expand_sweep_axis(
                arg_tokens=this_arg_tokens,
                sweep_axis_list=sweep_axis_list,
                sweep_string=this_sweep_string
            )
