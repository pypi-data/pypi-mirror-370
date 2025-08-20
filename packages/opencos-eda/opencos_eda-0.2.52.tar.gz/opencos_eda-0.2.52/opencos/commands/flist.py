'''opencos.commands.flist - Base class command handler for: eda flist ...

Intended to be overriden by Tool based classes (such as CommandFListVivado, etc).'''

# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

import os

from opencos import util
from opencos.eda_base import CommandDesign
from opencos.utils.str_helpers import strip_all_quotes

class CommandFList(CommandDesign):
    '''Base class command handler for: eda flist ...'''

    command_name = 'flist'

    def __init__(self, config: dict):
        CommandDesign.__init__(self, config=config)
        self.args.update({
            'eda-dir'            : 'eda.flist', # user can specify eda-dir if files are generated.
            'out'                : "flist.out",
            'emit-define'        : True,
            'emit-incdir'        : True,
            'emit-v'             : True,
            'emit-sv'            : True,
            'emit-vhd'           : True,
            'emit-cpp'           : True,
            'emit-non-sources'   : True, # as comments, from DEPS 'reqs'
            'prefix-define'      : "+define+",
            'prefix-incdir'      : "+incdir+",
            'prefix-v'           : "",
            'prefix-sv'          : "",
            'prefix-vhd'         : "",
            'prefix-cpp'         : "",
            'prefix-non-sources' : "", # as comments anyway.
            # TODO(simon): make the define quoting work like the paths quoting
            'bracket-quote-define': False,
            'single-quote-define': False,
            'quote-define'       : True,
            'equal-define'       : True,
            'escape-define-value': False,
            'quote-define-value' : False,
            'bracket-quote-path' : False,
            'single-quote-path'  : False,
            'double-quote-path'  : False,
            'no-quote-path'      : False,
            'build-script'       : "", # we don't want this to error either

            'print-to-stdout': False,

            # ex: eda flist --print-to-stdout --emit-rel-path --quiet <target>
            'emit-rel-path'  : False,
        })
        self.args_help.update({
            'print-to-stdout': "do not save file, print to stdout",
        })

    def process_tokens(
            self, tokens: list , process_all: bool = True, pwd: str = os.getcwd()
    ) -> list:
        unparsed = CommandDesign.process_tokens(
            self, tokens=tokens, process_all=process_all, pwd=pwd
        )
        self.do_it()
        return unparsed

    def get_flist_dict(self) -> dict:
        '''Returns dict of some internal class member vars, ignores args

        Useful for an extneral caller to get details about this CommandDesign child
        object without generating a .f file, or having to know specifics about the
        class
        '''
        self.command_safe_set_tool_defines() # (Command.command_safe_set_tool_defines)

        ret = {}
        for key in ['files_sv', 'files_v', 'files_vhd', 'defines', 'incdirs']:
            # These keys must exist, all are lists, defines is a dict
            x = getattr(self, key, None)
            if isinstance(x, (dict, list)):
                ret[key] = x.copy()
            else:
                ret[key] = x
        return ret

    def do_it(self) -> None:
        '''do_it() is the main entry point for creating the flist(),

        Usually it is called from self.process_tokens()'''

        # add defines for this job
        self.command_safe_set_tool_defines() # (Command.command_safe_set_tool_defines)

        if not self.args['top']:
            util.warning(f'CommandFList: {self.command_name=} not run due to lack of',
                         f'{self.args["top"]=} value')
            self.write_eda_config_and_args()
            return

        # check if we're overwriting the output flist file.
        if self.args['print-to-stdout']:
            pass
        elif os.path.exists(self.args['out']):
            if self.args['force']:
                util.info(f"Removing existing {self.args['out']}")
                os.remove(self.args['out'])
            else:
                self.error(f"Not overwriting {self.args['out']} unless you specify --force")

        # Note - we create a work_dir in case any DEPS commands created files that need to be
        # added to our sources.
        self.create_work_dir()
        self.run_dep_commands()

        pq1 = ""
        pq2 = "" # pq = path quote
        if self.args['no-quote-path']:
            pass # if we decide to make one of the below default, this will override
        elif self.args['bracket-quote-path']:
            pq1 = "{"
            pq2 = "}"
        elif self.args['single-quote-path']:
            pq1 = "'"
            pq2 = "'"
        elif self.args['double-quote-path']:
            pq1 = '"'
            pq2 = '"'

        if self.args['print-to-stdout']:
            fo = None
            print()
        else:
            util.debug(f"Opening {self.args['out']} for writing")
            fo = open( # pylint: disable=consider-using-with
                self.args['out'], 'w', encoding='utf-8'
            )
            print(f"## {self.args=}", file=fo)

            if self.args['emit-non-sources']:
                if self.files_non_source:
                    print('## reqs (non-source files that are dependencies):', file=fo)
                    prefix = strip_all_quotes(self.args['prefix-non-sources'])
                    for f in self.files_non_source:
                        if self.args['emit-rel-path']:
                            f = os.path.relpath(f)
                        print('##    ' + prefix + pq1 + f + pq2, file=fo)

        if self.args['emit-define']:
            prefix = strip_all_quotes(self.args['prefix-define'])
            for d, value in self.defines.items():
                if value is None:
                    newline = prefix + d
                else:
                    if self.args['bracket-quote-define']:
                        qd1 = "{"
                        qd2 = "}"
                    elif self.args['single-quote-define']:
                        qd1 = "'"
                        qd2 = "'"
                    elif self.args['quote-define']:
                        qd1 = '"'
                        qd2 = '"' # rename this one when things calm down
                    else:
                        qd1 = ''
                        qd2 = ''
                    if self.args['equal-define']:
                        ed1 = '='
                    else:
                        ed1 = ' '
                    if self.args['escape-define-value']:
                        value = value.replace('\\', '\\\\').replace('"', '\\"')
                    if self.args['quote-define-value']:
                        value =f'"{value}"'
                    newline = prefix + qd1 + f"{d}{ed1}{value}" + qd2
                print(newline, file=fo)

        if self.args['emit-incdir']:
            prefix = strip_all_quotes(self.args['prefix-incdir'])
            for i in self.incdirs:
                if self.args['emit-rel-path']:
                    i = os.path.relpath(i)
                print(prefix + pq1 + i + pq2, file=fo)
        if self.args['emit-v']:
            prefix = strip_all_quotes(self.args['prefix-v'])
            for f in self.files_v:
                if self.args['emit-rel-path']:
                    f = os.path.relpath(f)
                print(prefix + pq1 + f + pq2, file=fo)
        if self.args['emit-sv']:
            prefix = strip_all_quotes(self.args['prefix-sv'])
            for f in self.files_sv:
                if self.args['emit-rel-path']:
                    f = os.path.relpath(f)
                print(prefix + pq1 + f + pq2, file=fo)
        if self.args['emit-vhd']:
            prefix = strip_all_quotes(self.args['prefix-vhd'])
            for f in self.files_vhd:
                if self.args['emit-rel-path']:
                    f = os.path.relpath(f)
                print(prefix + pq1 + f + pq2, file=fo)
        if self.args['emit-cpp']:
            prefix = strip_all_quotes(self.args['prefix-cpp'])
            for f in self.files_cpp:
                if self.args['emit-rel-path']:
                    f = os.path.relpath(f)
                print(prefix + pq1 + f + pq2, file=fo)

        if self.args['print-to-stdout']:
            print() # don't need to close fo (None)
        else:
            fo.close()
            util.info(f"Created {self.args['out']}")

        self.write_eda_config_and_args()
