'''test_deps_schema - pytest to check schema of all DEPS.[markup] files in the repo'''

import os

from opencos.deps_schema import check_files

def test_all_deps():
    '''Find all DEPS files and confirm the schema is error-free

    uses opencos.deps_schema.check_files (aka package script eda_deps_schema) which
    is using pypackage 'schema'.
    '''

    # get all the files
    all_deps_files = []
    for root, _, files in os.walk(os.getcwd()):
        for fname in files:
            if fname.startswith('DEPS') and \
               any(fname.endswith(x) for x in [
                   '.yml', '.yaml', '.json', '.toml', 'DEPS'
               ]):

                all_deps_files.append(os.path.join(root, fname))

    # run all the files, but one at a time:
    for fname in all_deps_files:
        passes = check_files(all_deps_files)
        assert passes, f'{fname=} did not pass schema checks'

    assert len(all_deps_files) > 0
