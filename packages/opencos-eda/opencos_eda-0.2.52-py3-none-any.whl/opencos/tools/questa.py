''' opencos.tools.questa - Used by opencos.eda commands with --tool=questa

Also a base class for tools.modelsim_ase.
'''

# pylint: disable=R0801 # (setting similar, but not identical, self.defines key/value pairs)

# TODO(drew): fix these pylint eventually:
# pylint: disable=too-many-branches

import os
import re
import shutil

from opencos import util
from opencos.eda_base import Tool
from opencos.commands import CommandSim

class ToolQuesta(Tool):
    '''Base class for CommandSimQuesta, collects version information about qrun'''

    _TOOL = 'questa'
    _EXE = 'qrun'

    starter_edition = False # Aka, modelsim_ase
    sim_exe = '' # vsim or qrun
    sim_exe_base_path = ''
    questa_major = None
    questa_minor = None

    def __init__(self, config: dict):
        super().__init__(config=config)
        self.args['part'] = 'xcu200-fsgd2104-2-e'

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION
        path = shutil.which(self._EXE)
        if not path:
            self.error(f"{self._EXE} not in path, need to setup",
                       "(i.e. source /opt/intelFPGA_pro/23.4/settings64.sh")
            util.debug(f"{path=}")
            if self._EXE.endswith('qrun') and \
               any(x in path for x in ('modelsim_ase', 'questa_fse')):
                util.warning(f"{self._EXE=} Questa path is for starter edition",
                             "(modelsim_ase, questa_fse), consider using --tool=modelsim_ase",
                             "or --tool=questa_fse")
        else:
            self.sim_exe = path
            self.sim_exe_base_path, _ = os.path.split(path)

        if self._EXE.endswith('vsim'):
            self.starter_edition = True

        m = re.search(r'(\d+)\.(\d+)', path)
        if m:
            self.questa_major = int(m.group(1))
            self.questa_minor = int(m.group(2))
            self._VERSION = str(self.questa_major) + '.' + str(self.questa_minor)
        else:
            self.error("Questa path doesn't specificy version, expecting (d+.d+)")
        return self._VERSION

    def set_tool_defines(self):
        # Will only be called from an object which also inherits from CommandDesign,
        # i.e. has self.defines
        self.defines['OC_TOOL_QUESTA'] = None
        self.defines[f'OC_TOOL_QUESTA_{self.questa_major:d}_{self.questa_minor:d}'] = None

class CommandSimQuesta(CommandSim, ToolQuesta):
    '''Command handler for: eda sim --tool=questa.'''

    def __init__(self, config:dict):
        CommandSim.__init__(self, config)
        ToolQuesta.__init__(self, config=self.config)
        # add args specific to this simulator
        self.args['gui'] = False
        self.args['tcl-file'] = "sim.tcl"
        self.shell_command = self.sim_exe # set by ToolQuesta.get_versions(self)

    def set_tool_defines(self):
        ToolQuesta.set_tool_defines(self)

    def do_it(self):
        # add defines for this job
        self.set_tool_defines()
        self.write_eda_config_and_args()

        # it all gets done with one command
        command_list = [ self.shell_command, "-64", "-sv" ]

        # incdirs
        for value in self.incdirs:
            command_list += [ f"+incdir+{value}" ]

        # defines
        for key, value in self.defines.items():
            if value is None:
                command_list += [ f"+define+{key}" ]
            elif isinstance(value, str) and "\'" in value:
                command_list += [ f"\"+define+{key}={value}\"" ]
            else:
                command_list += [ f"\'+define+{key}={value}\'" ]

        # compile verilog
        for f in self.files_v:
            command_list += [ f ]

        # compile systemverilog
        for f in self.files_sv:
            command_list += [ f ]

        # TODO(drew): We don't natively support Xilinx Ultrascale+ glbl.v in questa yet.
        # To do so, would need to do something along the lines of:
        # if using_queta_and_xilinx_libs:
        #     vivado_base_path = getattr(self, 'vivado_base_path', '')
        #     glbl_v = vivado_base_path.replace('bin', 'data/verilog/src/glbl.v')
        #     if not os.path.exists(glbl_v):
        #         self.error(f"Vivado is not setup, could not find file {glbl_v=}")
        #     command_list.append(glbl_v)

        # misc options
        command_list += [ '-top', self.args['top'], '-timescale', '1ns/1ps', '-work', 'work.lib']
        # TODO(drew): most of these should move to eda_config_defaults.yml
        command_list += [
            # avoid warnings about defaulting to "var" which isn't LRM behavior
            '-svinputport=net',
            #  Existing package 'xxxx_pkg' at line 9 will be overwritten.
            '-suppress', 'vlog-2275',
            #  Extra checking for conflict in always_comb and always_latch variables at vopt time
            '-suppress', 'vlog-2583',
            #  Missing connection for port 'xxxx' (The default port value will be used)
            '-suppress', 'vopt-13159',
            #  Too few port connections for 'uAW_FIFO'.  Expected 10, found 8
            '-suppress', 'vopt-2685',
            #  Missing connection for port 'almostEmpty' ... same message for inputs and outputs.
            '-note', 'vopt-2718',
        ]
        if self.args['gui']:
            command_list += ['-gui=interactive', '+acc', '-i']
        elif self.args['waves']:
            command_list += ['+acc', '-c']
        else:
            command_list += ['-c']

        if util.args['verbose']:
            command_list += ['-verbose']

        # TODO(drew): We don't natively support Xilinx Ultrascale+ libraries in --tool=questa
        # with an easy hook (like --xilinx) but we could?
        # To get this to work, need to add this, among other items:
        # --> command_list += '''-L xil_defaultlib -L unisims_ver -L unimacro_ver
        #                        -L xpm -L secureip -L xilinx_vip'''.split(" ")

        # check if we're bailing out early
        if self.args['stop-after-elaborate']:
            command_list += ['-elab', 'elab.output', '-do', '"quit"' ]

        # create TCL
        tcl_name = os.path.abspath(os.path.join(self.args['work-dir'], self.args['tcl-file']))
        with open( tcl_name, 'w', encoding='utf-8' ) as fo:
            if self.args['waves']:
                if self.args['waves-start']:
                    print(f"run {self.args['waves-start']} ns", file=fo)
                print("add wave -r /*", file=fo)
            print("run -all", file=fo)
            if not self.args['gui']:
                print("quit", file=fo)
        command_list += ['-do', tcl_name ]

        # execute snapshot
        self.exec(self.args['work-dir'], command_list)

    # Note that CommandSimQuesta doesn't yet follow the framework from CommandSim.do_it()
    # so we have to define all helper methods for pylint:

    def compile(self) -> None:
        pass

    def elaborate(self) -> None:
        pass

    def simulate(self) -> None:
        pass

    def get_compile_command_lists(self, **kwargs) -> list:
        return []

    def get_elaborate_command_lists(self, **kwargs) -> list:
        return []

    def get_simulate_command_lists(self, **kwargs) -> list:
        return []

    def get_post_simulate_command_lists(self, **kwargs) -> list:
        return []


class CommandElabQuesta(CommandSimQuesta):
    '''Command handler for: eda elab --tool=questa'''

    def __init__(self, config:dict):
        CommandSimQuesta.__init__(self, config)
        # add args specific to this simulator
        self.args['stop-after-elaborate'] = True
