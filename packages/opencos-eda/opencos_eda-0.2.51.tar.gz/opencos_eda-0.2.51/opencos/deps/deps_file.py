'''deps_file -- functions and DepsFile class (for holding info and getting data from a
DEPS markup file.)

Performs no procesing.
'''

import json
import os
from pathlib import Path

import toml

from opencos import util
from opencos.deps.defaults import DEPS_FILE_EXTS, ROOT_TABLE_KEYS_NOT_TARGETS
from opencos.util import debug, error
from opencos.utils.markup_helpers import yaml_safe_load, toml_load_only_root_line_numbers, \
    markup_writer, markup_dumper
from opencos.utils.str_helpers import fnmatch_or_re, dep_str2list
from opencos.utils.subprocess_helpers import subprocess_run_background
from opencos.utils.status_constants import EDA_DEPS_FILE_NOT_FOUND, EDA_DEPS_TARGET_NOT_FOUND


def deps_data_get_all_targets(data: dict) -> list:
    '''Given extracted DEPS data (dict) get all the root level keys that aren't defaults'''
    if data is None:
        return []
    return [x for x in data.keys() if x not in ROOT_TABLE_KEYS_NOT_TARGETS]


def get_deps_markup_file(base_path: str) -> str:
    '''Returns one of DEPS.yml, DEPS.yaml, DEPS.toml, DEPS.json'''
    for suffix in DEPS_FILE_EXTS:
        deps_file = os.path.join(base_path, 'DEPS' + suffix)
        if os.path.isfile(deps_file):
            return deps_file
    return ''


def deps_markup_safe_load(
        filepath: str, assert_return_types: tuple = (type(None), dict),
        only_root_line_numbers: bool = False
) -> dict:
    '''Returns dict (may return {}) from filepath (str), errors if return type not in
    assert_return_types.

    (assert_return_types can be empty tuple, or any type to avoid check.)

    only_root_line_numbers -- if True, will return a dict of {key: line number (int)} for
                              all the root level keys. Used for debugging DEPS.yml in
                              eda.CommandDesign.resolve_target_core
    '''
    data = {}
    _, file_ext = os.path.splitext(filepath)
    if file_ext in ['', '.yml', 'yaml']:
        # treat DEPS as YAML.
        data = yaml_safe_load(filepath=filepath, only_root_line_numbers=only_root_line_numbers)
    elif file_ext == '.toml':
        if only_root_line_numbers:
            data = toml_load_only_root_line_numbers(filepath)
        else:
            data = toml.load(filepath)
    elif file_ext == '.json':
        if only_root_line_numbers:
            data = {}
        else:
            with open(filepath, encoding='utf=8') as f:
                data = json.load(f)

    if assert_return_types and not isinstance(data, assert_return_types):
        error(f'deps_markeup_safe_load: {filepath=} loaded type {type(data)=} is not in',
              f'{assert_return_types=}')

    return data


def get_all_targets( # pylint: disable=dangerous-default-value,too-many-locals,too-many-branches
        dirs: list = [os.getcwd()],
        base_path: str = os.getcwd(),
        filter_str: str = '',
        filter_using_multi: str = '',
        error_on_empty_return: bool = True,
        lstrip_path: bool = True
) -> list:
    '''Returns a list of [dir/target, ... ] using relpath from base_path

    If using filter_using_multi (str), dirs (list) is not required. Example:
        filter_using_multi='sim --tool vivado path/to/*test'
    and filter_str is applied to all resulting targets.

    If not using filter_using_multi, dirs is required, and filter_str is applied
    To all targets from dirs.
    '''

    _path_lprefix = str(Path('.')) + os.path.sep

    if filter_using_multi:
        targets = []
        orig_dir = os.path.abspath(os.getcwd())
        os.chdir(base_path)
        cmd_str = 'eda multi --quiet --print-targets ' + filter_using_multi
        stdout, _, rc = subprocess_run_background(
            work_dir='.', command_list=cmd_str.split()
        )
        os.chdir(orig_dir)
        if rc != 0:
            error(f'get_all_targets: {base_path=} {filter_using_multi=} {cmd_str=} returned:',
                  f'{rc=}, {stdout=}')

        multi_filtered_targets = stdout.split()
        if not filter_str:
            targets = multi_filtered_targets
        else:
            targets = set()
            for target in multi_filtered_targets:
                this_dir, leaf_target = os.path.split(target)
                if fnmatch_or_re(pattern=filter_str,
                                 string=leaf_target):
                    t = os.path.join(os.path.relpath(this_dir, start=base_path), leaf_target)
                    if lstrip_path:
                        t = t.removeprefix(_path_lprefix)
                    targets.add(t)
            targets = list(targets)
        if not targets and error_on_empty_return:
            error(f'get_all_targets: {base_path=} {filter_using_multi=} returned no targets')
        return targets

    targets = set()
    for this_dir in dirs:
        this_dir = os.path.join(base_path, this_dir)
        deps_file = get_deps_markup_file(this_dir)
        if not deps_file:
            continue
        data = deps_markup_safe_load(filepath=deps_file)

        for leaf_target in deps_data_get_all_targets(data):
            if not filter_str or fnmatch_or_re(pattern=filter_str,
                                               string=leaf_target):
                t = os.path.join(os.path.relpath(this_dir, start=base_path), leaf_target)
                if lstrip_path:
                    t = t.removeprefix(_path_lprefix)
                targets.add(t)

    if not targets and error_on_empty_return:
        error(f'get_all_targets: {base_path=} {dirs=} {filter_str=} returned no targets')
    return list(targets)


def deps_target_get_deps_list(
        entry, default_key: str = 'deps', target_node: str = '',
        deps_file: str = '', entry_must_have_default_key: bool = False
) -> list:
    '''Given a DEPS table entry (str, list, dict) return the 'deps:' list'''

    # For convenience, if key 'deps' in not in an entry, and entry is a list or string, then
    # assume it's a list of deps
    debug(f'{deps_file=} {target_node=}: {entry=} {default_key=}')
    deps = []
    if isinstance(entry, str):
        deps = dep_str2list(entry)
    elif isinstance(entry, list):
        deps = entry # already a list
    elif isinstance(entry, dict):

        if entry_must_have_default_key:
            assert default_key in entry, \
                f'{target_node=} in {deps_file=} does not have a key for {default_key=} in {entry=}'
        deps = entry.get(default_key, [])
        deps = dep_str2list(deps)

    # Strip commented out list entries, strip blank strings, preserve non-strings
    ret = []
    for dep in deps:
        if isinstance(dep, str):
            if not dep or dep.startswith('#'):
                continue
        ret.append(dep)
    return ret


def deps_list_target_sanitize(
        entry, default_key: str = 'deps', target_node: str = '', deps_file: str = '',
        entry_fix_deps_key: bool = True
) -> dict:
    '''Returns a sanitized DEPS markup table entry (dict --> dict)

    Since we support target entries that can be dict, list, or str(), sanitize
    them so they are a dict, with a key named 'deps' that has a list of deps.
    '''
    ret = None
    if isinstance(entry, dict):
        ret = entry

    if isinstance(entry, str):
        mylist = dep_str2list(entry) # convert str to list
        ret = {default_key: mylist}

    if isinstance(entry, list):
        # it's already a list
        ret = {default_key: entry}

    if ret is not None:
        if entry_fix_deps_key and 'deps' in ret:
            ret['deps'] = deps_target_get_deps_list(
                entry=ret, default_key='deps', deps_file=deps_file,
                entry_must_have_default_key=True
            )
    else:
        assert False, f"Can't convert to list {entry=} {default_key=} {target_node=} {deps_file=}"

    return ret


class DepsFile:
    '''A Container for a DEPS.yml or other Markup file

    References the original CommandDesign object and its cache

    Used for looking up a target, getting its line number in the original file, and
    merging contents with a DEFAULTS key if present.
    '''

    def __init__(  # pylint: disable=dangerous-default-value
            self, command_design_ref: object, target_path: str, cache: dict = {}
    ):
        self.target_path = target_path
        self.deps_file = get_deps_markup_file(target_path)
        self.rel_deps_file = self.deps_file

        if not self.deps_file:
            # didn't find it, file doesn't exist.
            self.data = {}
            self.line_numbers = {}
        elif self.deps_file in cache:
            self.data = cache[self.deps_file].get('data', {})
            self.line_numbers = cache[self.deps_file].get('line_numbers', {})
        else:
            self.data = deps_markup_safe_load(self.deps_file)
            self.line_numbers = deps_markup_safe_load(self.deps_file, only_root_line_numbers=True)
            cache[self.deps_file] = {
                'data': self.data,
                'line_numbers': self.line_numbers,
            }

        if self.deps_file:
            deps_path, deps_leaf = os.path.split(self.deps_file)
            if deps_path and os.path.exists(deps_path):
                self.rel_deps_file = os.path.join(os.path.relpath(deps_path), deps_leaf)

        self.error = getattr(command_design_ref, 'error', None)
        if not self.error:
            self.error = util.error


    def found(self) -> bool:
        '''Returns true if this DEPS file exists and extracted non-empty data'''
        return bool(self.deps_file) and bool(self.data)

    def get_approx_line_number_str(self, target) -> str:
        '''Given a full target name, get the approximate line numbers in the DEPS file if
        available in self.line_numbers'''
        _, target_node = os.path.split(target)
        if not self.line_numbers:
            return ''

        return f'line={self.line_numbers.get(target_node, "")}'

    def gen_caller_info(self, target: str) -> str:
        '''Given a full target name (path/to/my_target) return caller_info str for debug'''
        return '::'.join([
            self.rel_deps_file,
            target,
            self.get_approx_line_number_str(target)
        ])

    def lookup(self, target_node: str, caller_info: str) -> bool:
        '''Returns True if the target_node is in the DEPS markup file. If not, error with

        some caller_info(str). This is more useful for YAML or TOML markup where we have
        caller_info.
        '''
        if target_node not in self.data:
            found_target = False
            # For error printing, prefer relative paths:
            t_path = os.path.relpath(self.target_path) + os.path.sep
            t_node = target_node
            t_full = os.path.join(t_path, t_node)
            if not caller_info:
                # If we don't have caller_info, likely came from command line (or DEPS JSON data):
                if '.' in target_node:
                    # Likely a filename (target_node does not include path)
                    self.error(f'Trying to resolve command-line target={t_full} (file?):',
                               f'File={t_node} not found in directory={t_path}',
                               error_code=EDA_DEPS_FILE_NOT_FOUND)
                elif not self.rel_deps_file:
                    # target, but there's no DEPS file
                    self.error(f'Trying to resolve command-line target={t_full}:',
                               f'but path {t_path} has no DEPS markup file (DEPS.yml)',
                               error_code=EDA_DEPS_FILE_NOT_FOUND)
                else:
                    self.error(f'Trying to resolve command-line target={t_full}:',
                               f'was not found in deps_file={self.rel_deps_file},',
                               f'possible targets in deps file = {list(self.data.keys())}',
                               error_code=EDA_DEPS_TARGET_NOT_FOUND)
            else:
                # If we have caller_info, then this was a recursive call from another
                # DEPS file. It should already have the useful error messaging:

                if '.' in target_node:
                    # Likely a filename (target_node does not include path)
                    self.error(f'Trying to resolve target={t_full} (file?):',
                               f'called from {caller_info},',
                               f'File={t_node} not found in directory={t_path}',
                               error_code=EDA_DEPS_FILE_NOT_FOUND)
                elif not self.rel_deps_file:
                    # target, but there's no DEPS file
                    self.error(f'Trying to resolve target={t_full}:',
                               f'called from {caller_info},',
                               f'but {t_path} has no DEPS markup file (DEPS.yml)',
                               error_code=EDA_DEPS_FILE_NOT_FOUND)
                else:
                    self.error(f'Trying to resolve target={t_full}:',
                               f'called from {caller_info},',
                               f'Target not found in deps_file={self.rel_deps_file}',
                               error_code=EDA_DEPS_TARGET_NOT_FOUND)
        else:
            debug(f'Found {target_node=} in deps_file={self.rel_deps_file}')
            found_target = True

        return found_target


    def get_entry(self, target_node) -> dict:
        '''Returns the DEPS markup table "entry" (dict) for a target

        This has DEFAULTS applied, and is converted to a dict if it wasn't already
        '''

        # Start with the defaults
        entry = self.data.get('DEFAULTS', {}).copy()

        # Lookup the entry from the DEPS dict:
        entry_raw = self.data[target_node]

        entry_sanitized = deps_list_target_sanitize(
            entry_raw, target_node=target_node, deps_file=self.deps_file
        )

        # Finally update entry (defaults) with what we looked up:
        entry.update(entry_sanitized)

        return entry

    def get_all_targets(self) -> list:
        '''Returns list of all targets in this obj, skipping keys like DEFAULTS and METADATA'''
        return deps_data_get_all_targets(self.data)

    def get_sanitized_data(self) -> dict:
        '''Returns a sanitized dict of self.data, resolves DEFAULTS, METADATA, and implicit

        space-separated-str, lists for 'deps' in a target entry
        '''
        new_data = {}
        targets = self.get_all_targets()
        for target in targets:
            new_data[target] = self.get_entry(target)
        return new_data

    def write_sanitized_markup(self, filepath: str) -> None:
        '''Writes the sanitized dict of self.data as JSON/YAML (filepath extension)'''
        markup_writer(data=self.get_sanitized_data(), filepath=filepath)

    def str_sanitized_markup(self, as_yaml: bool = False) -> str:
        '''Returns str sanitized YAML or JSON str of self.data'''
        return markup_dumper(self.get_sanitized_data(), as_yaml=as_yaml)


    def print_sanitized_markup(self, as_yaml: bool = False) -> None:
        '''Prints sanitized JSON str of self.data to STDOUT'''
        print(self.str_sanitized_markup(as_yaml=as_yaml))
