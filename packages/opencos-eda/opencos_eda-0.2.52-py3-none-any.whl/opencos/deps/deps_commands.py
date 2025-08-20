'''opencos.deps.deps_commands - pymodule for processing DEPS markup deps-commands

This supports things like:
my_target:
  - deps:
    - commands:
      - shell: <string>
      - peakrdl: <string>
      - work-dir-add-sources: <list>
'''


import os
from pathlib import Path
import re
import shutil

from opencos.util import debug, error, warning, ShellCommandList
from opencos.deps.defaults import SUPPORTED_COMMAND_KEYS

THISPATH = os.path.dirname(__file__)
PEAKRDL_CLEANUP_PY = os.path.join(THISPATH, '..', 'peakrdl_cleanup.py')

def path_substitutions_relative_to_work_dir(
        exec_list: list, info_str: str, target_path: str,
        enable_filepath_subst: bool, enable_dirpath_subst: bool
) -> list:
    '''For shell commands, since eda.py Command objects operate out of a "work-dir", it can
    make shell commands confusing with additional ../.. to get to the calling directory, and
    the original target directory is completely lost otherwise.

    By default, if a FILE exists in the calling target's path, we will substitute that file
    instead of looking in the work-dir. (can be disabled via filepath-subst-target-dir: False)

    Optionally if a DIR exists in the calling target's path, will will substitute that DIR
    instead of relative to work-dir. This can be annoying with relative paths like ../ (which
    would exist in both) so this is disabled by default (can be enabled with
    dirpath-subst-target-dir: True)
    '''

    if not enable_filepath_subst and not enable_dirpath_subst:
        return exec_list

    # Look for path substitutions, b/c we later "work" in self.args['work-dir'], but
    # files should be relative to our target_path.
    for i,word in enumerate(exec_list):
        m = re.search(r'(\.+\/+[^"\;\:\|\<\>\*]*)$', word)
        if m:
            # ./, ../, file=./../whatever  It might be a filepath.
            # [^"\;\:\|\<\>\*] is looking for non-path like characters, so we dont' have a trailing
            #  " : ; < > |
            # try and see if this file or dir exists. Note that files in the
            # self.args['work-dir'] don't need this, and we can't assume dir levels in the work-dir.
            try:
                try_path = os.path.abspath(os.path.join(os.path.abspath(target_path), m.group(1)))
                if enable_filepath_subst and  os.path.isfile(try_path):
                    # make the substitution
                    exec_list[i] = word.replace(m.group(1), try_path)
                    debug(f'file path substitution {info_str=} {target_path=}: replaced - {word=}'
                          f'is now ={exec_list[i]}. This can be disabled in DEPS with:',
                          '"filepath-subst-targetdir: false"')
                elif enable_dirpath_subst and os.path.isdir(try_path):
                    # make the substitution
                    exec_list[i] = word.replace(m.group(1), try_path)
                    debug(f'dir path substitution {info_str=} {target_path=}: replaced - {word=}'
                          f'is now ={exec_list[i]}. This can be disabled in DEPS with:',
                          '"dirpath-subst-targetdir: false"')
            except Exception:
                pass

    return exec_list


def line_with_var_subst( # pylint: disable=dangerous-default-value
        line : str, replace_vars_dict: dict = {},
        replace_vars_os_env: bool = False,
        target_node: str = '', target_path: str = ''
) -> str:
    '''Given a line (often from a shell style command) perform var substitution'''

    # We can try for replacing any formatted strings, using self.args, and os.environ?
    # We have to do this per-word, so that missing replacements or tcl-like things, such
    # as '{}' wouldn't bail if trying to do line.format(**dict)
    if '{' not in line:
        return line

    if replace_vars_os_env:
        replace_dict = {}
        replace_dict.update(os.environ)
        replace_dict.update(replace_vars_dict)
    else:
        replace_dict = replace_vars_dict

    words = line.split()
    for i,word in enumerate(words):
        try:
            words[i] = word.format(**replace_dict)
        except Exception:
            # this was an attempt, no need to catch exceptions if we couldn't replace the word.
            pass

    new_line = ' '.join(words)
    if new_line != line:
        debug(f'{target_node=} {target_path=} performed string format replacement,',
              f'{line=} {new_line=}')
        return new_line

    debug(f'{target_node=} {target_path=} string format replacement attempted,',
          f'no replacement. {line=}')
    return line


def parse_deps_shell_str(
        line: str, target_path: str, target_node: str,
        enable_filepath_subst_target_dir: bool = True,
        enable_dirpath_subst_target_dir: bool = False,
        enable: bool = True
) -> dict:
    '''Returns None or a dict of a possible shell command from line (str)

     Examples of 'line' str:
         shell@echo "hello world" > hello.txt
         shell@ generate_something.sh
         shell@ generate_this.py --input=some_data.json
         shell@ cp ./some_file.txt some_file_COPY.txt
         shell@ vivado -mode tcl -script ./some.tcl -tclargs foo_ip 1.2 foo_part foo_our_name \
                      {property value}

    Returns None if no parsing was performed, or if enable is False

    target_path (str) -- from dependency parsing (relative path of the DEPS file)
    target_node (str) -- from dependency parsing, the target containing this 'line' str.
    '''
    if not enable:
        return {}

    m = re.match(r'^\s*shell\@(.*)\s*$', line)
    if not m:
        return {}

    exec_str = m.group(1)
    exec_list = exec_str.split()

    # Look for path substitutions, b/c we later "work" in self.args['work-dir'], but
    # files should be relative to our target_path.
    # Note this can be disable in DEPS via path-subst-target-dir=False
    exec_list = path_substitutions_relative_to_work_dir(
        exec_list=exec_list, info_str='shell@', target_path=target_path,
        enable_filepath_subst=enable_filepath_subst_target_dir,
        enable_dirpath_subst=enable_dirpath_subst_target_dir
    )

    return {
        'target_path': os.path.abspath(target_path),
        'target_node': target_node,
        'run_from_work_dir': True, # may be overriden later.
        'exec_list': exec_list,
    }


def parse_deps_work_dir_add_srcs(
        line : str, target_path : str, target_node : str, enable : bool = True
) -> dict:
    '''Returns None or a dict describing source files to add from the work-dir path

     Examples of 'line' str:
         work_dir_add_srcs@ my_csrs.sv
         work_dir_add_srcs@ some_generated_file.sv some_dir/some_other.v ./gen-vhd-dir/even_more.vhd

    Returns None if no parsing was performed, or if enable is False

    target_path (str) -- from dependency parsing (relative path of the DEPS file)
    target_node (str) -- from dependency parsing, the target containing this 'line' str.
    '''
    if not enable:
        return {}

    m = re.match(r'^\s*work_dir_add_srcs\@(.*)\s*$', line)
    if not m:
        return {}

    files_str = m.group(1)
    file_list = files_str.split()

    d = {'target_path': os.path.abspath(target_path),
         'target_node': target_node,
         'file_list': file_list,
         }
    return d


def parse_deps_peakrdl( # pylint: disable=too-many-locals
        line: str, target_path: str, target_node: str, enable: bool = True,
        enable_filepath_subst_target_dir: bool = True,
        enable_dirpath_subst_target_dir: bool = False
) -> dict:
    '''Returns None or a dict describing a PeakRDL CSR register generator dependency

     Examples of 'line' str:
         peakrdl@ --cpuif axi4-lite-flat --top oc_eth_10g_1port_csrs ./oc_eth_10g_csrs.rdl

    Returns None if no parsing was performed, or if enable=False

    target_path (str) -- from dependency parsing (relative path of the DEPS file)
    target_node (str) -- from dependency parsing, the target containing this 'line' str.
    '''

    m = re.match(r'^\s*peakrdl\@(.*)\s*$', line)
    if not m:
        return None

    if not enable:
        warning(f'peakrdl: encountered peakrdl command in {target_path=} {target_node=},' \
                + ' however it is not enabled in edy.py - eda.config[dep_command_enables]')
        return None

    if not shutil.which('peakrdl'):
        error('peakrdl: is not present in shell path, or the python package is not avaiable,' \
              + f' yet we encountered a peakrdl command in {target_path=} {target_node=}')
        return None


    args_str = m.group(1)
    args_list = args_str.split()

    # Fish out the .rdl name
    # If there is --top=value or --top value, then fish out that value (that will be the
    # value.sv and value_pkg.sv generated names.

    sv_files = []
    top = ''
    for i,str_value in enumerate(args_list):
        if '--top=' in str_value:
            _, top = str_value.split('=')
        elif '--top' in str_value:
            if i + 1 < len(args_list):
                top = args_list[i + 1]

    for str_item in args_list:
        if str_item[-4:] == '.rdl':
            _, rdl_fileonly = os.path.split(str_item) # strip all path info
            rdl_filebase, _ = os.path.splitext(rdl_fileonly) # strip .rdl ext
            if not top:
                top = rdl_filebase

    assert top != '', \
        f'peakrdl@ DEP, could not determine value {top=}: {line=}, {target_path=}, {target_node=}'

    sv_files += [ f'peakrdl/{top}_pkg.sv', f'peakrdl/{top}.sv' ]


    shell_commands = [
        [ 'peakrdl', 'regblock', '-o', str(Path('peakrdl/'))] + args_list,
        # Edit file to apply some verilator waivers, etc, from peakrdl_cleanup.py:
        [ 'python3', PEAKRDL_CLEANUP_PY, str(Path(f'peakrdl/{top}.sv')),
          str(Path(f'peakrdl/{top}.sv')) ],
    ]

    ret_dict = {
        'shell_commands_list': [], # Entry needs target_path, target_node, exec_list
        'work_dir_add_srcs': {},   # Single dict needs target_path, target_node, file_list
    }

    # Make these look like a dep_shell_command:
    for one_cmd_as_list in shell_commands:
        ret_dict['shell_commands_list'].append(
            parse_deps_shell_str(
                line=(' shell@ ' + ' '.join(one_cmd_as_list)),
                target_path=target_path,
                target_node=target_node,
                enable_filepath_subst_target_dir=enable_filepath_subst_target_dir,
                enable_dirpath_subst_target_dir=enable_dirpath_subst_target_dir
            )
        )

    # Make the work_dir_add_srcs dict:
    ret_dict['work_dir_add_srcs'] = parse_deps_work_dir_add_srcs(
        line = ' work_dir_add_srcs@ ' + ' '.join(sv_files),
        target_path = target_path,
        target_node = target_node
    )

    return ret_dict



def deps_commands_handler( #pylint: disable=too-many-locals,too-many-branches
        config: dict, eda_args: dict,
        dep : str, deps_file : str, target_node : str, target_path : str,
        commands : list
) -> (list, list):
    ''' Returns a tuple of (shell_commands_list, work_dir_add_srcs_list), from processing
        a DEPS.yml entry for something like:

        target_foo:
          deps:
            - some_file
            - commands: # (list of dicts) These are directly in a 'deps' list.
                - shell: ...
                - peakrdl: ...
                - work-dir-add-sources: ...
                - shell: ...

        target_foo:
          commands: # (list of dicts) These are in a target, but not ordered with other deps
             - shell: ...
             - peakrdl: ...
             - work-dir-add-sources: ...
             - shell: ...

        We'd like to handle the list in a 'commands' entry, supporting it in a few places in a
        DEPS.yml, so this this a generic way to do that. Currently these are broken down into Shell
        commands and Files that will be later added to our sources (b/c we haven't run the Shell
        commands yet, and the Files aren't present yet but we'd like them in our eda.py filelist in
        order.

    '''

    shell_commands_list = []
    work_dir_add_srcs_list = []

    for command in commands:
        assert isinstance(command, dict), \
            (f'{type(command)=} must be dict, for {deps_file=} {target_node=} {target_path=} with'
             f'{commands=}')

        for key in command.keys():
            if key not in SUPPORTED_COMMAND_KEYS:
                error(f'deps_commands.process_commands - command {key=} not in',
                      f'{SUPPORTED_COMMAND_KEYS=}')

        var_subst_dict = {} # this is per-command.
        if config['dep_command_enables'].get('var_subst_os_env', False) and \
           command.get('var-subst-os-env', False):
            var_subst_dict.update(dict(os.environ))
        if config['dep_command_enables'].get('var_subst_args', False) and \
           command.get('var-subst-args', False):
            var_subst_dict = eda_args

        tee_fpath = command.get('tee', None)

        # These are both optional bools, default True, would have to explicitly be set to False
        # to take effect:
        run_from_work_dir = command.get('run-from-work-dir', True)
        filepath_subst_target_dir = command.get('filepath-subst-target-dir', True)
        dirpath_subst_target_dir = command.get('dirpath-subst-target-dir', False)

        for key,item in command.items():

            # skip the tee and var-subst-* keys, since these types are bools and not commands.
            if key in ['tee',
                       'var-subst-os-env',
                       'var-subst-args',
                       'run-from-work-dir',
                       'filepath-subst-target-dir',
                       'dirpath-subst-target-dir']:
                continue

            # Optional variable substituion in commands
            if isinstance(item, str):
                item = line_with_var_subst(item, replace_vars_dict=var_subst_dict,
                                           target_node=target_node, target_path=deps_file)

            if key == 'shell':
                # For now, piggyback on parse_deps_shell_str:
                ret_dict = parse_deps_shell_str(
                    line=('shell@ ' + item),
                    target_path=target_path,
                    target_node=target_node,
                    enable_filepath_subst_target_dir=filepath_subst_target_dir,
                    enable_dirpath_subst_target_dir=dirpath_subst_target_dir,
                    enable=config['dep_command_enables']['shell'],
                )
                # To support 'tee: <some-file>' need to append it to last
                # list item in ret_dict['exec_list'], and make it a util.ShellCommandList.
                if tee_fpath:
                    ret_dict['exec_list'] = ShellCommandList(
                        ret_dict['exec_list'], tee_fpath=tee_fpath
                    )
                ret_dict['run_from_work_dir'] = run_from_work_dir
                assert ret_dict, f'shell command failed in {dep=} {target_node=} in {deps_file=}'
                shell_commands_list.append(ret_dict) # process this later, append to ret tuple

            elif key in ['work-dir-add-srcs', 'work-dir-add-sources']:
                # For now, piggyback on parse_deps_work_dir_add_srcs:
                ret_dict = parse_deps_work_dir_add_srcs(
                    line = 'work_dir_add_srcs@ ' + item,
                    target_path = target_path,
                    target_node = target_node,
                    enable=config['dep_command_enables']['work_dir_add_srcs'],
                )
                assert ret_dict, \
                    f'work-dir-add-srcs command failed in {dep=} {target_node=} in {deps_file=}'

                work_dir_add_srcs_list.append(ret_dict) # process this later, append to ret tuple

            elif key == 'peakrdl':
                # for now, piggyback on parse_deps_peakrdl:
                ret_dict = parse_deps_peakrdl(
                    line = 'peakrdl@ ' + item,
                    target_path = target_path,
                    target_node = target_node,
                    enable_filepath_subst_target_dir=filepath_subst_target_dir,
                    enable_dirpath_subst_target_dir=dirpath_subst_target_dir,
                    enable=config['dep_command_enables']['peakrdl']
                )
                assert ret_dict, f'peakrdl command failed in {dep=} {target_node=} in {deps_file=}'

                # add all the shell commands:
                shell_commands_list += ret_dict['shell_commands_list'] # several entries.
                # all the work_dir_add_srcs:
                work_dir_add_srcs_list += [ ret_dict['work_dir_add_srcs'] ] # single entry append


            else:
                assert False, \
                    f'unknown {key=} in {command=}, {item=} {dep=} {target_node=} in {deps_file=}'

    return (shell_commands_list, work_dir_add_srcs_list)
