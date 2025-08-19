''' opencos.utils.markup_helpers - function helpers for YAML, TOML reading and writing'''

import json
import os
import re
import shutil
import subprocess

import yaml

from opencos.util import debug, error, info, warning


def yaml_load_only_root_line_numbers(filepath: str) -> dict:
    '''Returns a dict of {key: int line number}, very crude'''
    # Other solutions aren't as attractive, require a lot of mappers to get
    # line numbers on returned values that aren't dict
    data = None
    with open(filepath, encoding='utf-8') as f:
        try:
            # Try to do a very lazy parse of root level keys only, returns dict{key:lineno}
            data = {}
            for lineno,line in enumerate(f.readlines()):
                m = re.match(r'^(\w+):', line)
                if m:
                    key = m.group(1)
                    data[key] = lineno + 1
        except Exception as e:
            error(f"Error loading YAML {filepath=}:", e)
    return data


def toml_load_only_root_line_numbers(filepath: str) -> dict:
    '''Returns a dict of {key: int line number}, very crude'''
    data = None
    with open(filepath, encoding='utf-8') as f:
        try:
            data = {}
            for lineno, line in enumerate(f.readlines()):
                m = re.match(r'^\[(\w+)\]', line)
                if m:
                    key = m.group(1)
                    data[key] = lineno + 1
        except Exception as e:
            error(f'Error loading TOML {filepath=}', e)
    return data


def yaml_safe_load(filepath: str, only_root_line_numbers:bool = False) -> dict:
    '''Returns dict or None from filepath (str), errors if return type not in assert_return_types.

    only_root_line_numbers -- if True, will return a dict of {key: line number (int)} for
                              all the root level keys. Used for debugging DEPS.yml in
                              eda.CommandDesign.resolve_target_core
    '''

    data = None

    if only_root_line_numbers:
        return yaml_load_only_root_line_numbers(filepath)

    with open(filepath, encoding='utf-8') as f:
        debug(f'Opening {filepath=}')
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:

            # if yamllint is installed, then use it to get all errors in the .yml|.yaml
            # file, instead of the single exception.
            if shutil.which('yamllint'):
                try:
                    sp_out = subprocess.run(
                        f'yamllint -d relaxed --no-warnings {filepath}'.split(),
                        capture_output=True, text=True, check=False )
                    for x in sp_out.stdout.split('\n'):
                        if x:
                            info('yamllint: ' + x)
                except Exception as e2:
                    debug(f'yamllimt exception: {e2}')

            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                error(f"Error parsing {filepath=}: line {mark.line + 1},",
                      f"column {mark.column +1}: {e.problem}")
            else:
                error(f"Error loading YAML {filepath=}:", e)
        except Exception as e:
            error(f"Error loading YAML {filepath=}:", e)

    return data


def yaml_safe_writer(data: dict, filepath: str) -> None:
    '''Wrapper for yaml.dump, enforces file extension otherwise warning'''
    _, ext = os.path.splitext(filepath)
    if ext.lower() in ('.yml', '.yaml'):
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True,
                      default_flow_style=False, sort_keys=False, encoding='utf-8')
    else:
        warning(f'{filepath=} to be written for this extension not implemented.')

def json_writer(data: dict, filepath: str) -> None:
    '''Wrapper for json.dump'''
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def markup_writer(data: dict, filepath: str) -> None:
    '''Wrapper for yaml_safe_writer or json_writer'''
    _, ext = os.path.splitext(filepath)
    if ext.lower in ('.yml', '.yaml'):
        yaml_safe_writer(data, filepath)
    else:
        json_writer(data, filepath)


def markup_dumper(data: dict, as_yaml: bool = False) -> str:
    '''Returns JSON str; if as_yaml=True returns YAML str, from data'''
    if as_yaml:
        return yaml.dump(
            data=data, allow_unicode=True,
            default_flow_style=False, sort_keys=False
        )

    # else return JSON:
    return str(json.dumps(data, indent=4))
