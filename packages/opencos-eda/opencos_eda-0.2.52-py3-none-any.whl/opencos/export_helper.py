''' opencos.export_helper: package used by command sim and synth,

to handle common tasks with "exporting" a DEPS target. An exported target copies all
source files (deps, reqs) and attempts to resolve included files so they are all relative
to +incdir+.
'''

import os
import shutil
import json

from opencos import util
from opencos.util import debug, info, warning, error
from opencos.utils.markup_helpers import yaml_safe_writer

# pylint: disable=dangerous-default-value


SV_INCLUDE_ITERATION_MAX_DEPTH = 128 # Depth to look for nested included files.
REMOVE_DEPS_YML_DEFINES = [
    'OC_SEED',
    'OC_ROOT',
]


def json_paths_to_jsonl(
        json_file_paths:list, output_json_path:str, assert_json_types=[dict]
) -> None:
    '''Given a list of .json filepath strs, save a single .jsonl (newline separated json(s)).

    errors if one of json_file_paths content's type is not in assert_json_types
    (assert_json_types can be empty list to avoid check).
    '''

    if not json_file_paths:
        error(f'{json_file_paths=} cannot be empty list')


    output_json_dir = os.path.split(output_json_path)[0]
    util.safe_mkdir(output_json_dir)

    with open(output_json_path, 'w', encoding='utf-8') as outf:

        # jsonl is every line of the file is a json.
        for json_file_path in json_file_paths:
            with open(json_file_path, encoding='utf-8') as f:
                data = json.load(f)
                if len(assert_json_types) > 0 and type(data) not in assert_json_types:
                    error(f'{json_file_path=} JSON data is not a Table (py dict) {type(data)=}')
                json.dump(data, outf)
                outf.write('\n')
        info(f'Wrote {len(json_file_paths)} tests to {output_json_path=}')


def json_paths_to_single_json(
        json_file_paths:list, output_json_path:str, assert_json_types=[dict]
) -> None:
    '''Given a list of .json filepath strs, save a single .json with key 'tests' and a list.

    errors if one of json_file_paths content's type is not in assert_json_types
    (assert_json_types can be empty list to avoid check).
    '''

    if len(json_file_paths) == 0:
        error(f'{json_file_paths=} cannot be empty list')


    output_json_dir = os.path.split(output_json_path)[0]
    util.safe_mkdir(output_json_dir)

    with open(output_json_path, 'w', encoding='utf-8') as outf:

        out_json_data = {
            'tests': [],
        }
        for json_file_path in json_file_paths:
            with open(json_file_path, encoding='utf-8') as f:
                data = json.load(f)
                if len(assert_json_types) > 0 and type(data) not in assert_json_types:
                    error(f'{json_file_path=} JSON data is not a Table (py dict) {type(data)=}')
                out_json_data['tests'].append(data)
        json.dump(out_json_data, outf)
        outf.write('\n')
        info(f'Wrote {len(json_file_paths)} tests {output_json_path=}')


def traverse_sv_file_for_includes(filename: str) -> (dict, set):
    '''Lazily parses a SV <filename> looking for `includes

    Returns tuple:
       - dict of modified_lines: {linenum (int): line (str, modified line value), ...}
       - set of found included files
    '''

    assert any(filename.endswith(x) for x in ['.v', '.sv', '.vh', '.svh']), \
        f'{filename=} does not have a supported extension, refusing to parse it'
    assert os.path.exists(filename), f'{filename=} does not exist'

    found_included_files = set()
    modified_lines = {}

    with open(filename, encoding='utf-8') as f:

        for linenum, line in enumerate(f.readlines()):
            line_modified = False

            if '`include' in line:
                # strip comments on line, in case someone has: // `include "lib/foo.svh"
                # we can't handle /* comments */ on a line like this.
                assert '/*' not in line
                parts = line.split("//")
                words = parts[0].split() # only use what's on the left of the comments
                prev_word_is_tick_include = False
                for i,word in enumerate(words):
                    word = word.rstrip('\n')
                    if word == '`include':
                        # don't print this word, wait until next word
                        prev_word_is_tick_include = True
                    elif prev_word_is_tick_include:
                        assert word.startswith('"')
                        assert word.endswith('"')
                        prev_word_is_tick_include = False
                        include_fname = word[1:-1] # trim " at start and end

                        # strip the path information and keep track that
                        # we would like to modify this line of filename
                        _, include_fname_no_path = os.path.split(include_fname)
                        if include_fname != include_fname_no_path:
                            words[i] = '"' + include_fname_no_path + '"'
                            line_modified = True

                        if include_fname not in found_included_files:
                            # this has path information, perhaps relative, perhaps absolute, or
                            # perhaps relative to any of the +incdir+ paths. Figure that out later.
                            found_included_files.add(include_fname)

                if line_modified:
                    modified_lines[linenum] = ' '.join(words)

    return modified_lines, found_included_files


def write_modified_lines(
        src_filename: str,
        modified_lines: dict,
        modify_files_and_save_to_path: str = '',
        unmodified_files_copy_to_path: str = ''
) -> None:
    '''Given a dict of modified lines, walk the src_filename contents and write modifications

    to the dst_filename. The modified_lines dict is:
       {linenum (int): line (str, modified line value), ...}
    '''

    debug(f'export_helper: {src_filename=} {modified_lines=}')

    _, src_filename_no_path = os.path.split(src_filename)

    # Optionally write out modified files (flatten the path information
    # on `include "../bar.svh" )
    if modified_lines and modify_files_and_save_to_path:
        dst = os.path.join(modify_files_and_save_to_path, src_filename_no_path)
        if not os.path.exists(dst):
            with open(src_filename, encoding='utf-8') as f, \
                 open(dst, 'w', encoding='utf-8') as outf:
                for linenum, line in enumerate(f.readlines()):
                    if linenum in modified_lines:
                        new_line = modified_lines[linenum]
                        outf.write(new_line + '\n')
                        debug(f'export_helper: Modified {src_filename=} as {dst=}:',
                              f'{linenum=} {new_line=}')
                    else:
                        outf.write(line)

    # Copy unmodified files to some path.
    if not modified_lines and unmodified_files_copy_to_path:
        if os.path.isdir(unmodified_files_copy_to_path):
            dst = os.path.join(unmodified_files_copy_to_path, src_filename_no_path)
            if not os.path.exists(dst):
                debug(f'export_helper: Copied unmodified {src_filename=} to {dst=}')
                shutil.copy(src=src_filename, dst=dst)


def find_sv_included_files_within_file(
        filename: str,
        known_incdir_paths: list,
        warnings: bool = True,
        modify_files_and_save_to_path: str = '',
        unmodified_files_copy_to_path: str = ''
) -> list:
    '''Given a filename (full path) and a list of known incdir paths, returns
    a list of included files (full path).

    (Optional) modify_files_and_save_to_path (str: directory/path) if you wish
    to strip all path information on the `include "(path)" for example:
      `include "foo.svh" -- no modifications
      `include "../bar.svh" -- is modified to become `include "bar.svh"
    (Optional) unmodified_files_copy_to_path (str: directory/path) if you wish
    to copy unmodified files to this path.
    '''

    modified_lines, found_included_files = traverse_sv_file_for_includes(filename)

    debug(f'export_helper: {filename=} {modify_files_and_save_to_path=}',
          f'{unmodified_files_copy_to_path=}')

    if modify_files_and_save_to_path or unmodified_files_copy_to_path:
        # Save outputs to these paths:
        write_modified_lines(
            src_filename=filename,
            modified_lines=modified_lines,
            modify_files_and_save_to_path=modify_files_and_save_to_path,
            unmodified_files_copy_to_path=unmodified_files_copy_to_path
        )

    # Back to the list found_included_files that we observed within our filename, we
    # still need to return all the included files.
    ret = []
    for fname in found_included_files:
        # Does this file exist, using our known_incdir_paths?
        found = False
        for some_dir in known_incdir_paths:
            try_file_path = os.path.abspath(os.path.join(some_dir, fname))
            if os.path.exists(try_file_path):
                if try_file_path not in ret:
                    ret.append(try_file_path)
                    found = True
                    debug(f'export_helper: Include observed in {filename=} will use',
                          f'{try_file_path=} for export')
                    break # we can only match one possible file out of N possible incdir paths.


        if not found and warnings:
            # file doesn't exist in any included directory, we only warn here b/c
            # it will eventually fail compile.
            include_fname = fname
            warning(f'export_helper: {include_fname=} does not exist in any of'
                    f'{known_incdir_paths=}, was included within source files: {filename=}')

    return ret


def get_list_sv_included_files(
        all_src_files: list,
        known_incdir_paths: list,
        target: str = '',
        warnings: bool = True,
        modify_files_and_save_to_path: str = '',
        unmodified_files_copy_to_path: str = ''
) -> list:
    ''' Given a list of all_src_files, and list of known_incdir_paths, returns a list
    of all included files (fullpath). This is recurisve if an included file includes another file.

    Optional args -
    target -- (str) for debug purposes, the original DEPS target
    warnings -- (bool) False to disable warnings
    modify_files_and_save_to_path -- (str: directory/path) if you wish to strip all path information
      on the `include "(path)" for example:
        `include "foo.svh" -- no modifications
        `include "../bar.svh" -- is modified to become `include "bar.svh"
      Set to None (default) to disable.
    unmodified_files_copy_to_path -- (str: directory/path) if you wish to copy unmodified
      files to this path. Set to None (default) to disable.
    '''

    # order shouldn't matter, these will get added to the testrunner's filelist and
    # be included with +incdir+.

    sv_included_files_dict = {} # key, value is if we've traversed it (bool)

    for fname in all_src_files:
        included_files_list = find_sv_included_files_within_file(
            filename=fname,
            known_incdir_paths=known_incdir_paths,
            warnings=warnings,
            modify_files_and_save_to_path=modify_files_and_save_to_path,
            unmodified_files_copy_to_path=unmodified_files_copy_to_path
        )

        for f in included_files_list:
            if f not in sv_included_files_dict:
                sv_included_files_dict[f] = False # add entry, mark it not traversed.

    for _ in range(SV_INCLUDE_ITERATION_MAX_DEPTH):
        # do these for a a depth of recurisve levels, in case `include'd file includes another file.
        # If we have more than N levels of `include hunting, then rethink this.
        # For example, some codebases would do their file dependencies as `include
        # as part of their header guards, which could be ~100 levels of nesting.
        for fname,traversed in sv_included_files_dict.items():
            if not traversed:
                included_files_list = find_sv_included_files_within_file(
                    filename=fname,
                    known_incdir_paths=known_incdir_paths,
                    warnings=warnings,
                    modify_files_and_save_to_path=modify_files_and_save_to_path,
                    unmodified_files_copy_to_path=unmodified_files_copy_to_path
                )
                sv_included_files_dict[fname] = True # mark as traversed.

                for f in included_files_list:
                    if f not in sv_included_files_dict:
                        sv_included_files_dict[f] = False # add entry, mark it not traversed.

    if not all(sv_included_files_dict.values()):
        # we had some that we're traversed.
        not_traversed = [k for k,v in sv_included_files_dict.items() if not v]
        error(f'Depth {SV_INCLUDE_ITERATION_MAX_DEPTH=} exceeded in looking for `includes,' \
              + f' {target=} {not_traversed=}')


    ret = []
    for fname,traversed in sv_included_files_dict.items():
        if traversed:
            # add all the included files (should be traversed!) to our return list
            ret.append(fname)

    return ret


class ExportHelper:
    '''ExportHelper is an object that command handlers can use to assist in creating

    a directory with all exported sources, args, incdirs, defines, and output of
    what was exported.
    '''

    def __init__(self, cmd_design_obj, eda_command='export', out_dir=None, target=''):
        self.cmd_design_obj = cmd_design_obj
        self.eda_command = eda_command
        self.out_dir = out_dir
        self.target = target

        self.args = self.cmd_design_obj.args # lazy alias.
        self.included_files = []
        self.out_deps_file = None


    def run(
            self, check_if_overwrite:bool=False,
            deps_file_args:list=[],
            export_json_eda_config:dict={}, **kwargs
    ) -> None:
        '''main entrypoint for ExportHelper object. Creates output directory, writes files

        to it, creates a DEPS.yml in output directory, and optional output JSON file
        '''

        self.create_out_dir(check_if_overwrite)
        self.write_files_to_out_dir()
        self.create_deps_yml_in_out_dir(deps_file_args=deps_file_args)

        if self.args.get('export-json', False):
            self.create_export_json_in_out_dir(eda_config=export_json_eda_config, **kwargs)

        info(f'export_helper: done - wrote to: {self.out_dir}')


    def create_out_dir(self, check_if_overwrite: bool= False) -> None:
        '''Creates output directory for exported files, requires a 'top' to be

        set by the original target, or inferred from target or files.
        '''

        if not self.args.get('top', ''):
            error('export_helper.py internal error, args[top] is not set, cannot create',
                  'output directory for export',
                  f'{self.args=} {self.target=} {self.eda_command=} {self.out_dir=}')

        if not self.out_dir:
            if self.args.get('output', '') == "":
                self.out_dir = os.path.join('.', 'eda.export', self.args['top'] + '.export')

        if check_if_overwrite and self.args.get('force', False):
            if os.path.exists(self.out_dir):
                error(f"export_helper: output directory {self.out_dir} exists, use --force",
                      "to overwrite")

        if not os.path.exists(self.out_dir):
            info(f"export_helper: Creating {self.out_dir} for exported file tree")
            util.safe_mkdir(self.out_dir)


    def write_files_to_out_dir(self):
        '''Called by self.run(), writes all files to output directory. Has to determine

        the includes files used by SV/Verilog to unravel nested or relative included
        paths.
        '''

        # Also sets our list of included files.
        self.included_files = get_list_sv_included_files(
            all_src_files=self.cmd_design_obj.files_sv + self.cmd_design_obj.files_v,
            known_incdir_paths=self.cmd_design_obj.incdirs,
            target=self.target,
            modify_files_and_save_to_path=self.out_dir,
            unmodified_files_copy_to_path=self.out_dir
        )

        info(f"export_helper: {self.target=} included files {self.included_files=}")

        for filename in self.cmd_design_obj.files_non_source:
            dst = os.path.join(self.out_dir, os.path.split(filename)[1])
            if not os.path.exists(dst):
                shutil.copy(src=filename, dst=dst)


    def create_deps_yml_in_out_dir(self, deps_file_args:list=[]):
        '''Creates ouput exported directory DEPS.yml file with the exported target'''
        if not self.target:
            self.target = 'test'
        else:
            # Need to stip path information from self.target, b/c it will
            # be a Table key:
            self.target = os.path.split(self.target)[1]

        info(f'export_helper: Creating DEPS.yml for {self.target=} in {self.out_dir=}')

        # Need to strip path information from our files_sv and files_v:
        deps_files = []
        for fullpath in self.cmd_design_obj.files_sv + self.cmd_design_obj.files_v:
            filename = os.path.split(fullpath)[1]
            deps_files.append(filename)


        data = {
            self.target: {
                'incdirs': ['.'],
                'deps': deps_files,
            }
        }


        if deps_file_args:
            data[self.target]['args'] = deps_file_args.copy()

        if self.args.get('top', None):
            data[self.target]['top'] = self.args['top']

        if self.cmd_design_obj.defines:
            data[self.target]['defines'] = self.cmd_design_obj.defines.copy()
            for define in REMOVE_DEPS_YML_DEFINES:
                # Remove defines keys for OC_ROOT and OC_SEED. Change OC_SEED to _ORIG_OC_SEED
                if define in data[self.target]['defines']:
                    data[self.target]['defines'].pop(define)

        reqs_fullpath_list = self.included_files + self.cmd_design_obj.files_non_source
        if reqs_fullpath_list:
            # Need to strip path information from non-source files:
            data[self.target]['reqs'] = []
            for fullpath in reqs_fullpath_list:
                filename = os.path.split(fullpath)[1]
                data[self.target]['reqs'].append(filename)


        dst = os.path.join(self.out_dir, 'DEPS.yml')
        self.out_deps_file = dst
        yaml_safe_writer(data=data, filepath=dst)


    def create_export_json_in_out_dir( # pylint: disable=unused-argument
            self, eda_config:dict={}, **kwargs
    ) -> None:
        '''Optionally creates an exported JSON file in the output directory'''

        if not self.eda_command:
            return

        # assumes we've run self.create_deps_yml_in_out_dir():
        assert self.target
        assert self.out_deps_file

        data = {
            'name': self.target,
            'eda': {
                'enable': True,
                'multi': False, # Not yet implemented.
                'command': self.eda_command,
                'targets': [self.target],
                'args': [],
                'waves': self.args.get('waves', False),
                # tool - eda.CommandSimVerilator has this set in self.args:
                'tool': self.args.get('tool', None),
            },
            'files': [],
        }

        # allow caller to override eda - tool, or eda - args, etc.
        for k,v in eda_config.items():
            if k in data['eda'] and v is not None:
                data['eda'][k] = v

        # Note that args may already be set via:
        #   create_deps_yml_in_out_dir(deps_file_args=some_list)
        # For example, eda.CommandSim.do_export() will set certain allow-listed
        # args if present with non-default values.


        all_files = [self.out_deps_file] + self.included_files \
            + self.cmd_design_obj.files_sv + self.cmd_design_obj.files_v \
            + self.cmd_design_obj.files_vhd + self.cmd_design_obj.files_cpp \

        for x in self.cmd_design_obj.files_non_source:
            if x not in all_files:
                all_files.append(x)

        for somefile in all_files:

            # because 'somefile' may still be pointing to the OG path in
            # self.cmd_design_obj.files_sv or .files_v, we really need to
            # instead use the files in self.out_dir (we already created them as
            # part of the export.
            filename = os.path.split(somefile)[-1]
            out_dir_filename = os.path.join(self.out_dir, filename)
            if os.path.exists(out_dir_filename):
                somefile = out_dir_filename
            else:
                error(f'export.json: {self.target=} Missing exported file, orig: {somefile=}')

            assert os.path.exists(somefile)
            with open(somefile, encoding='utf-8') as f:
                filestr = ''.join(f.readlines())
                data['files'].append({
                    'name': os.path.split(somefile)[1],
                    'content': filestr,
                })


        dst = os.path.join(self.out_dir, 'export.json')
        with open(dst, 'w', encoding='utf-8') as f:
            json.dump(data, f)
            f.write('\n')
        info(f'export_helper: Wrote {dst=}')

        # If this was from an `export` command, and the self.out_dir != self.args['work-dir'], then
        # copy the export.json to the work-dir:
        if self.out_dir != self.args['work-dir']:
            util.safe_mkdirs(base=self.args['work-dir'], new_dirs=['export'])
            src = os.path.abspath(os.path.join(self.out_dir, 'export.json'))
            dst = os.path.join(self.args['work-dir'], 'export', 'export.json')
            if not os.path.exists(dst):
                shutil.copy(src=filename, dst=dst)
            info(f'export_helper: Copied {src=} to {dst=}')
