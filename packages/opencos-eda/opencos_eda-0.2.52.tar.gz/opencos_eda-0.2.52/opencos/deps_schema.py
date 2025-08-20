''' deps_schema

-----------------------------------------------------------------------------
common DEPS.yml pattern using FILE schema.

DEPS.yml:
--------------
                                     <---- FILE schema
my_target_name:
                                     <---- TARGET_CONTENTS schema
  defines:                           <---- defines, optional table
    USER_DEFINE_VALUE: 12

  incdirs:                           <---- incdirs, optional array (or string)
    - ./

  top: tb                            <---- top, optional string

  deps:
                                     <---- TARGET_DEPS_CONTENTS schema
    - dut.sv
    - tb.sv

-----------------------------------------------------------------------------
common DEPS.yml pattern using FILE_SIMPLIFIED schema.

DEPS.yml:
--------------
                                     <---- FILE_SIMPLIFIED schema
my_target_name:
                                     <---- target (str) key for table.
  defines:                           <---- defines, optional table of (key: str Or null)
    USER_DEFINE_VALUE: 12

  incdirs:                           <---- incdirs, optional array of strings
    - ./

  top: tb                            <---- top, optional string

  deps:
                                     <---- deps, optional array of strings
    - dut.sv
    - tb.sv

-----------------------------------------------------------------------------

all-features DEPS.yml pattern using FILE schema.

DEPS.yml:
--------------

DEFAULTS:                            <---- (optional) TARGET_DEPS_CONTENTS schema
                                           applied to all targets.
METADATA:                            <---- (optional) unstructured table

my_target_name:
  defines:                           <---- defines, optional table
  incdirs:                           <---- incdirs, optional array (or string)
  top: tb                            <---- top, optional string
  deps:                              <---- TARGET_DEPS_CONTENTS schema
    - some_file.sv                   <---- string file name
    - sv@some_sv.txt                 <---- string sv@ prefix force this file to be
                                           treated by eda as .sv. Also supports
                                           v@, vhdl@, cpp@.
    - some_other_target_name         <---- string target name to another table key
                                           or to another directory's DEPS target.
    - commands:                      <---- commands, optional table
                                           uses DEPS_COMMANDS_LIST schema.
      - shell:                       <---- string for shell command to be run
        var-subst-args:              <---- bool, perform var substitution using args
        var-subst-os-env:            <---- bool, perform var substitution using os.environ
        run-from-work-dir:           <---- bool, default True, if False runs from target dir
                                           instead of work-dir.
        filepath-subst-target-dir:   <---- bool, default True, if False does not perform
                                           file path substitution relative to target dir
                                           (if substituted file exists).
        dirpath-subst-target-dir:    <---- bool, default False, if True performs
                                           directory path substitution relative to target dir
                                           (if substituted directory exists).
        tee:                         <---- string, filename to write logs to
      - work-dir-add-sources:        <---- work-dir-add-sources, optional list (or string)
        - some_file_gen_from_sh.sv   <---- string filename that we created with sh command
      - peakrdl:                     <---- string peakrdl command for CSR generation
  reqs:                              <---- reqs, optional array or string, files required
                                           by the target that are not source files, such
                                           those used by systemverilog $readmemh, etc.
    - some_mem.txt                   <---- string filename
  multi:                             <---- optional table, uses TARGET_MULTI_TABLE schema.
    ignore-this-target:              <---- array, or commands and tools to apply to `eda multi`
                                           ignore list.
      - commands:                    <---- list (or string) of eda commands to ignore for
                                           `eda multi`
        tools:                       <---- list (or string) of tools to ignore for `eda multi`
    args:                            <---- optional array of args to be added to all `eda multi`
                                           commands on this target
      - --some-arg=value             <---- string arg value, as key=value
      - --some-arg2
      - value2                       <---- two strings used as POSIX args: --some-arg2 value2
  <str>:                             <---- string eda command, must be one of: sim, elab,
                                           synth, build, export, flist. Uses
                                           TARGET_EDA_COMMAND_ENTRY_TABLE schema.
    args:                            <---- optional array of args to be added to this target
                                           for this named eda command (sim, elab, etc)
    deps:                            <---- optional array of files or targets to be applied
                                           to the current target for this named eda command.
    defines:                         <---- optional table, defines to be applied to the current
                                           target for this named eda command.
    incdirs:                         <---- optional array (or string) incdirs to be applied to
                                           the current target for this named eda command.
  tags:                              <---- tags, optional table using TARGET_TAGS_TABLE schema.
    <str>:                           <---- string user name for this tag
      with-tools:                    <---- optional array (or string) of tools this tag requires
                                           for the tag to be applied.
      with-args:                     <---- optional table of args values that must match for
                                           this tag to be applied.
      args:                          <---- optional array of args to be applied to this target
                                           if the tag is applied.
      deps:                          <---- optional array of deps (files, other targets) to be
                                           applied to this target if the tag is applied.
      incdirs:                       <---- optional array (or string) incdirs to be applied to
                                           the current target if the tag is applied.
      replace-config-tools           <---- optional table, experimental.
      additive-config-tools          <---- optional table, experimental.
-----------------------------------------------------------------------------




'''

import os
import sys

from schema import Schema, Or, Optional, SchemaError

from opencos import util
from opencos.deps import deps_file

# Because we deal with YAML, where a Table Key with dangling/empty value is allowed
# and we have things like SystemVerilog defines where there's a Table key with no Value,
# most Tables have to allow type str or value None:
STR_OR_NONE = Or(
    type(None),
    str
)

# DEPS specific feature to save typing for human written markup - allow for space separated
# strings to also be interpretted as lists:
ARRAY_OR_SPACE_SEPARATED_STRING = Or(
    type(None),
    str,
    [str],
)



DEPS_COMMANDS_LIST = [
    {
        Optional('shell'): str,
        Optional('var-subst-args'): bool,
        Optional('var-subst-os-env'): bool,
        Optional('run-from-work-dir'): bool,
        Optional('filepath-subst-target-dir'): bool,
        Optional('dirpath-subst-target-dir'): bool,
        Optional('tee'): Or(str, type(None)),
    },
    {
        Optional('peakrdl'): str,
    },
    {
        Optional('work-dir-add-sources'): ARRAY_OR_SPACE_SEPARATED_STRING,
    },
]

TARGET_DEPS_CONTENTS = Or(
    type(None),
    str,
    [
        str,
        {
            Optional('commands'): DEPS_COMMANDS_LIST,
        },
    ],
)

# within a <target> table -
TARGET_MULTI_TABLE = {
    Optional('ignore-this-target'): [
        {
            Optional('commands'): Or(str, type(None)),
            Optional('tools'): Or(str, type(None)),
        }
    ],
    Optional('args'): ARRAY_OR_SPACE_SEPARATED_STRING
}

TARGET_EDA_COMMAND_ENTRY_TABLE = {
    Optional('disable-tools'): type(None), # Not implemented in spec yet
    Optional('only-tools'): type(None), # Not implemented in spec yet
    Optional('args'): ARRAY_OR_SPACE_SEPARATED_STRING,
    Optional('deps'): type(None), # Not implemented in spec yet
    Optional('defines'): {
        Optional(str): Or(str, int, type(None)),
    },
    Optional('incdirs'): ARRAY_OR_SPACE_SEPARATED_STRING,
}

TARGET_EDA_COMMAND = {
    Optional('sim'): TARGET_EDA_COMMAND_ENTRY_TABLE,
    Optional('elab'): TARGET_EDA_COMMAND_ENTRY_TABLE,
    Optional('build'): TARGET_EDA_COMMAND_ENTRY_TABLE,
    Optional('synth'): TARGET_EDA_COMMAND_ENTRY_TABLE,
    Optional('export'): TARGET_EDA_COMMAND_ENTRY_TABLE,
    Optional('flist'): TARGET_EDA_COMMAND_ENTRY_TABLE,
}

TARGET_TAGS_TABLE = {
    Optional(str): {
        Optional('with-tools'): ARRAY_OR_SPACE_SEPARATED_STRING,
        Optional('with-args'): dict,
        Optional('args'): ARRAY_OR_SPACE_SEPARATED_STRING,
        Optional('deps'): ARRAY_OR_SPACE_SEPARATED_STRING,
        Optional('defines'): {
            Optional(str): Or(str, int, type(None)),
        },
        Optional('incdirs'): ARRAY_OR_SPACE_SEPARATED_STRING,
        Optional('replace-config-tools'): dict,
        Optional('additive-config-tools'): dict,
    }
}


TARGET_CONTENTS = Or(
    ARRAY_OR_SPACE_SEPARATED_STRING,
    {
        # args: array
        Optional('args'): ARRAY_OR_SPACE_SEPARATED_STRING,
        # commands: array
        Optional('commands'): DEPS_COMMANDS_LIST,
        # defines: table of key-value; value null or string
        Optional('defines'): {
            Optional(str): Or(str, int, type(None)),
        },
        # incdirs: array
        Optional('incdirs'): ARRAY_OR_SPACE_SEPARATED_STRING,
        # top: string
        Optional('top'): str,
        # deps: array
        Optional('deps'): TARGET_DEPS_CONTENTS,
        # reqs: array
        Optional('reqs'): ARRAY_OR_SPACE_SEPARATED_STRING,
        # multi: table
        Optional('multi'): TARGET_MULTI_TABLE,
        # tags: table
        Optional('tags'): TARGET_TAGS_TABLE,
        # optional eda command customization for this target
        Optional(str): TARGET_EDA_COMMAND,
    },
)

# -----------------------------------------------------------------------------
#
# DEPS markup (DEPS.yml) schema!
#
# -----------------------------------------------------------------------------
FILE = Schema(
    Or(
        type(None), # Empty file is allowed.
        {
            #
            # DEFAULTS: <table>
            #    defaults applied to ALL targets in this file, local targets
            #    ** override ** the defaults.
            #
            Optional('DEFAULTS'): TARGET_CONTENTS,
            #
            # METADATA: <table>
            #    unstructured data, any UPPERCASE first level key is not
            #    considered a target.TARGET_CONTENTS,
            #
            Optional('METADATA'): dict,
            #
            # targets - user named Tables with markup file.
            #
            Optional(str): TARGET_CONTENTS,
        },
    )
)

FILE_SIMPLIFIED = Schema(
    Or(
        type(None), # Empty file is allowed.
        {

            Optional('METADATA'): dict,
            Optional(str): Or( # User named target contents
                {
                    Optional('args'): [str],
                    Optional('defines'): {
                        Optional(str): Or(type(None), str),
                    },
                    Optional('incdirs'): [str],
                    Optional('top'): str,
                    Optional('deps'): [str],
                    Optional('reqs'): [str],
                }
            )
        }
    )
)



def check(data: dict, schema_obj=FILE) -> (bool, str):
    '''Returns (bool, str) for checking dict against FILE schema'''
    try:
        schema_obj.validate(data)
        return True, None
    except SchemaError as e:
        return False, f'SchemaError: {e}'
    except Exception as e:
        return False, str(e)


def deps_markup_safe_load(deps_filepath: str) -> (bool, dict):
    '''Returns tuple (bool False if took errors, dict of markp data)'''
    current_errors = util.args['errors']
    data = deps_file.deps_markup_safe_load(deps_filepath)
    if util.args['errors'] > current_errors:
        return False, data
    return True, data


def check_file(filepath: str, schema_obj=FILE) -> (bool, str, str):
    '''Returns tuple (bool pass/fail, str error retdata, str deps_filepath)'''

    deps_filepath = filepath
    if os.path.isdir(filepath):
        deps_filepath = deps_file.get_deps_markup_file(base_path=filepath)

    # get deps file
    if not os.path.isfile(deps_filepath):
        print(f'ERROR: internal error(s) no DEPS.[yml|..] found in {filepath=}')
        return False, '', deps_filepath

    passes, data = deps_markup_safe_load(deps_filepath)
    if not passes:
        print(f'ERROR: internal error(s) from deps_markup_safe_load({deps_filepath=})')
        return False, '', deps_filepath

    passes, retdata = check(data, schema_obj)
    return passes, retdata, deps_filepath



def check_files(files, schema_obj=FILE) -> bool:
    '''Returns True if files lint cleanly in the FILE schema.'''

    if isinstance(files, str):
        files = [files]

    passes_list = []
    error_files = []
    for filepath in files:

        passes, retdata, deps_filepath = check_file(filepath, schema_obj)
        passes_list.append(passes)
        if passes:
            print(f'{deps_filepath}: [PASS]')
        if not passes:
            print(f'ERROR: {deps_filepath}:')
            if retdata:
                print('-- retdata --')
                print(retdata)
            print(f'    previous error on: {deps_filepath}\n')
            error_files.append(deps_filepath)


    ret = all(passes_list)
    if not ret:
        print(f'ERROR: files with problems (see above): {error_files}')
    return ret

def main( # pylint: disable=dangerous-default-value
        filepaths: list = []
) -> None:
    '''Returns None, will exit on completion, checks all DEPS schema in list filepaths

    If filepaths is empty, uses sys.argv[1:]'''

    fpaths = filepaths
    if not fpaths:
        assert len(sys.argv) >= 2, 'Need 1 or more args - DEPS file to check'
        fpaths = sys.argv[1:]

    assert fpaths and isinstance(fpaths, list), \
        f'Need 1 or more files to check: {fpaths=}'

    for filepath in fpaths:
        assert os.path.exists(filepath), f'{filepath=} does not exist'
    ret = check_files(fpaths)
    sys.exit(int(not ret))

if __name__ == '__main__':
    main()
