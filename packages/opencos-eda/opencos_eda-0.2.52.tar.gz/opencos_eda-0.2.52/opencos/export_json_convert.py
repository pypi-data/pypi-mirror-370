'''Converts eda style export.json or export.jsonl to an alternate schema.'''

import argparse
import json
import os
import sys
import uuid

import yaml

def read_input_json_fname(input_json_fname: str) -> list:
    '''Returns list (or tests) from input JSON or JSONL, helper function used by convert(...)'''
    data = None
    assert os.path.exists(input_json_fname), f'{input_json_fname=} does not exist'
    with open(input_json_fname, encoding='utf-8') as f:

        if input_json_fname.lower().endswith('.jsonl'):
            data = []
            for line in f.readlines():
                if line.rstrip():
                    data.append(json.loads(line.rstrip()))
        else:
            data = json.load(f)

    if isinstance(data, dict) and 'eda' in data:
        # 1 test, make it a list:
        data = [data]
    elif isinstance(data, dict) and 'tests' in data and isinstance(data['tests'], list):
        data = data['tests']

    assert data is not None and isinstance(data, list), f'unknown schmea for {input_json_fname=}'
    return data


def convert( # pylint: disable=dangerous-default-value, too-many-locals
        input_json_fname: str,
        output_json_fname: str,
        correlation_ids: list = [],
        correlation_id_key: str = 'correlation_id',
        output_top_is_eda_target_name:bool = False
) -> None:
    '''Returns None, takes an input json filename, writes to output_json_fname'''

    data = read_input_json_fname(input_json_fname)
    new_tests_list = []

    for index,test in enumerate(data):

        if correlation_ids and index < len(correlation_ids):
            correlation_id = correlation_ids[index]
        else:
            correlation_id = str(uuid.uuid4()) # somewhat uuid per entry.

        new_test_item = {
            'top': '',
            'files_list': [],
            correlation_id_key: correlation_id,
        }

        assert 'files' in test
        for entry in test['files']:
            new_test_item['files_list'].append({
                'filename': entry['name'],
                'content': entry['content'],
            })

            # load the DEPS.yml (from str) to find the value for 'top', because reasons.
            if entry['name'] == 'DEPS.yml':
                yaml_str = entry['content']
                deps_data = yaml.safe_load(yaml_str)
                assert len(deps_data.keys()) == 1
                #print(f'{deps_data=}')
                first_target_name = list(deps_data.keys())[0]
                target_entry = deps_data[first_target_name]
                #print(f'{target_entry=}')
                # TODO(drew): output_top_is_eda_target_name -- probably want to change this to be
                # Table key "targets" with list of string values.
                if output_top_is_eda_target_name:
                    top = first_target_name
                else:
                    top = target_entry.get('top', '')
                    if not top:
                        # then pick the last file?
                        top = target_entry.get('deps', [''])[-1]
                #print(f'{top=}')
                assert top
                new_test_item['top'] = top


        new_tests_list.append(new_test_item)

    new_data = {
        'tests': new_tests_list
    }

    with open(output_json_fname, 'w', encoding='utf-8') as f:
        json.dump(new_data, f)

    print(f'Wrote: {output_json_fname=}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='export_json_convert', add_help=True, allow_abbrev=False)

    parser.add_argument('--input-json', '-i', type=str)
    parser.add_argument('--output-json', '-o', type=str)
    parser.add_argument('--output-top-is-eda-target-name', default=False, action="store_true")

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    parsed, unparsed = parser.parse_known_args(sys.argv[1:])

    if not parsed.input_json or not parsed.output_json:
        parser.print_help()
        sys.exit(1)

    convert(
        input_json_fname=parsed.input_json,
        output_json_fname=parsed.output_json,
        output_top_is_eda_target_name=parsed.output_top_is_eda_target_name
    )
