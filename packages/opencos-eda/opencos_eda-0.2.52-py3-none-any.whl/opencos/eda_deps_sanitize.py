#!/usr/bin/env python3

'''opencos.eda_deps_sanitize is an executable script

Usage:
    eda_deps_sanitize --dir=<path>

Will print santized JSON data for the DEPS file found in --dir=<path>
'''

import argparse
import os
import sys

from pathlib import Path

from opencos import util
from opencos.deps import deps_file
from opencos.utils import status_constants


def run(*args) -> (int, str):
    '''Runs the DEPS sanitizer, prints results to stdout'''


    bool_kwargs = util.get_argparse_bool_action_kwargs()

    parser = argparse.ArgumentParser(
        prog='opencos eda_deps_sanitize', add_help=True, allow_abbrev=False
    )

    parser.add_argument('--yaml', **bool_kwargs,
                        help='Print output as YAML text, otherwise default is JSON text')
    parser.add_argument('dir', type=str, default=str(Path('.')),
                        help='Directory to look for DEPS.[markup] file')

    try:
        parsed, unparsed = parser.parse_known_args(list(args) + [''])
        unparsed = list(filter(None, unparsed))
    except argparse.ArgumentError:
        return 1, f'problem attempting to parse_known_args for {args=}'

    deps_path = parsed.dir
    if os.path.isfile(deps_path):
        deps_path, _ = os.path.split(deps_path)

    try:
        my_depsfile_obj = deps_file.DepsFile(None, deps_path, {})
        if not my_depsfile_obj.deps_file:
            return status_constants.EDA_DEPS_FILE_NOT_FOUND, f'No DEPS markup file at {parsed.dir}'

        ret_str = my_depsfile_obj.str_sanitized_markup(as_yaml=parsed.yaml)
        rc = util.get_return_code()
        return rc, ret_str
    except Exception as e:
        rc = 1, str(e)

    return 0, ''


def main() -> None:
    '''calls sys.exit(), main entrypoint'''
    args = []
    if len(sys.argv) > 1 and not args:
        args = sys.argv[1:]

    rc, deps_str = run(*args)
    print(deps_str)
    sys.exit(rc)


if __name__ == '__main__':
    main()
