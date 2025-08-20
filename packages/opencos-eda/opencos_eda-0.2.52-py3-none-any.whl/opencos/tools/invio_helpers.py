''' opencos.tools.invio_helpers - general helper functions for running Invio.'''

# TODO(drew): clean these up, method write_py_file is too long, etc:
# pylint: disable=dangerous-default-value # default list arg = []
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=unused-argument


import os
from typing import TypedDict
from opencos.util import ShellCommandList

# Given what we'll assume is a CommandDesign (CommandSim?) object, we'll try to
# perform some invio related commands on it.

class InvioCommandInfo(TypedDict):
    '''Return dict schema from get_invio_command_dict(..)'''
    work_dir: str
    py_filename: str
    v_filename: str
    full_v_filename: str
    full_py_filename: str
    top: str
    blackbox_module_list: list
    blackbox_files_list: list
    log_fname: str
    command_lists: list # list of util.ShellCommandList


def write_py_file(
        command_design_obj: object,
        py_filename: str = 'run_invio.py',
        v_filename: str = '',
        blackbox_list: list = [],
        sim_elab: bool = False,
        **kwargs
) -> dict:
    '''Given an eda.CommandDesign object, creates a .py file that can be run

    from invio-py or standalone. Returns a dict with a few details about the generated .py'''


    # Sanity check that command_design_obj has some expected details.
    assert isinstance(getattr(command_design_obj, 'incdirs', None), list)
    assert isinstance(getattr(command_design_obj, 'files_v', None), list)
    assert isinstance(getattr(command_design_obj, 'files_sv', None), list)
    assert isinstance(getattr(command_design_obj, 'files_vhd', None), list)

    args = getattr(command_design_obj, 'args', {})
    work_dir = args.get('work-dir', '')

    assert work_dir

    work_dir = os.path.abspath(work_dir)

    lines = [

        'from invio import init, define_macro, add_include_directory, \\',
        '    add_verilog_file, add_sv_file, elaborate, elaborate_pct, analyze, \\',
        '    print_instance_hierarchy, write_design, report_analyzed_files',
        'import os, shutil',
        '',
        'for p in ["invio"]:',
        f'    fullp = os.path.join("{work_dir}", p)',
        '    if not os.path.exists(fullp):',
        '        os.mkdir(fullp)',
        '',
    ]

    for name,value in command_design_obj.defines.items():
        if name in ['SIMULATION']:
            continue

        if value is None:
            lines.append(f'define_macro("{name}")')
        else:
            value = str(value)
            value = value.replace("'", "\\" + "'")
            value = value.replace('"', "\\" + '"')
            lines.append(f'define_macro("{name}", value="{value}")')

    # We must define SYNTHESIS for oclib_defines.vh to work correctly.
    lines.append('define_macro("SYNTHESIS")')

    for path in command_design_obj.incdirs:
        lines.append(f'add_include_directory("{path}")')

    for path in command_design_obj.files_v:
        lines.append(f'add_verilog_file("{path}")')

    for path in command_design_obj.files_sv:
        lines.append(f'add_sv_file("{path}")')

    for path in command_design_obj.files_vhd:
        lines.append(f'add_vhdl_file("{path}")')

    # Note - big assumption here that "module myname" is contained in myname.[v|sv]:
    blackbox_files_list = []
    for path in command_design_obj.files_v + command_design_obj.files_sv:
        _, leaf_filename = os.path.split(path)
        module_name = ''.join(leaf_filename.split('.')[:-1])
        if module_name in blackbox_list:
            blackbox_files_list.append(path)


    top = args.get('top', None)
    if top is None:
        # Infer the 'top' module as last verilog, SV, or vhdl file.
        tmp_list = command_design_obj.files_v + command_design_obj.files_sv \
            + command_design_obj.files_vhd
        _, top_fileonly = os.path.split(tmp_list[-1])
        top = ''.join(top_fileonly.split('.')[:-1])


    assert top

    if not v_filename:
        v_filename = f'{top}.v'


    full_v_filename = os.path.join(work_dir, 'invio', v_filename)
    full_py_filename = os.path.join(work_dir, py_filename)

    ret = InvioCommandInfo({
        'work_dir': work_dir,
        'py_filename': py_filename,
        'v_filename': v_filename,
        'full_v_filename': full_v_filename,
        'full_py_filename': full_py_filename,
        'top': top,
        'blackbox_module_list': blackbox_list,
        'blackbox_files_list': blackbox_files_list,
        'log_fname': 'invio.log',
        'command_lists': [ ShellCommandList(['python3', full_py_filename],
                                            tee_fpath = 'invio.log')]
    })

    if sim_elab:
        # elab (non-synthesis), runs the following (from eda.CommandElabInvio)
        lines += [
            'assert analyze()',
            f"assert elaborate('{top}', pct_elaboration=True, forceBlackbox={blackbox_list})",
            'assert elaborate_pct()',
            '',
            'report_analyzed_files()',
            'print_instance_hierarchy()',
        ]
    else:
        # synthesis-style elab (from eda.CommandElabInvioYosys)
        lines += [
            'assert analyze()',
            f"assert elaborate('{top}', rtl_elaboration=True, forceBlackbox={blackbox_list})",
            '',
            'report_analyzed_files()',
            'print_instance_hierarchy()',
            '',
            f"assert write_design('{full_v_filename}')",
            '',
        ]

        # It seems that Invio's write_design(..) will leave a few VERIFIC_MUX and other modules
        # commented out in the .v file. This doesn't work downstream for yosys, so uncomment these
        # with some brute force.

        tmp_v_filename = os.path.join(work_dir, '_tmp.v')

        lines += [
            '',
            '# We also get the joy of uncommenting any VERIFIC_* modules in the generated .v',
            f'with open("{full_v_filename}") as old, open("{tmp_v_filename}", "w") as new:',
            '    in_verific_commented_module = False',
            '    for line in old.readlines():',
            '        # Handle old, modify line:',
            '        if "// module VERIFIC_" in line:',
            '            in_verific_commented_module = True',
            '        if in_verific_commented_module:',
            '            line = line.replace("// ", "")',
            '        if line.startswith("endmodule"):',
            '            in_verific_commented_module = False',
            '        # Write out line to new:',
            '        new.write(line)',
            f'shutil.move("{tmp_v_filename}", ',
            f'            "{full_v_filename}")',
            '',
        ]


        for k,v in ret.items():
            if isinstance(v, str):
                lines.append(f'## {k} = "{v}"')

        # done with (not sim_elab).


    # write 'run_invo.py':
    if py_filename:
        outfile = os.path.join(work_dir, py_filename)
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


    return ret




def get_invio_command_dict(command_design_obj:object, v_filename='', py_filename='run_invio.py',
                           blackbox_list=[], sim_elab:bool=False, **kwargs) -> dict:
    '''Creates a .py file from an eda.CommandDesign. Returns a dict with

    information about what to run.'''

    invio_dict = write_py_file( command_design_obj, v_filename=v_filename,
                                py_filename=py_filename, blackbox_list=blackbox_list,
                                sim_elab=sim_elab, **kwargs )

    return invio_dict
