''' names.py

This is a human-maintained but ideally machine parsable mapping of names

Where convenient, this file should be parsed versus embedding names in code,
which is what oc_cli.py does.

Once assigned, names are not changed, so it's OK to use: `define OC_VENDOR 1
to indicate Xilinx in some RTL code.  There doesn't yet seem to be cause to
bring in automation to create SystemVerilog defines and such, as each board
just needs to set a couple of these statically.

all values in this file are in hex.
'''

table = {

    'OC_VENDOR': {
        0: "None",
        1: "Xilinx",
    },

    'OC_BOARD': {
        0: "None",
        1: "JC35",
        2: "U200",
        3: "U50",
        4: "U55N",
        5: "U50C",
        6: "PYNQ-Z2",
    },

    'OC_LIBRARY': {
        0: "None",
        1: "Ultrascale+",
    },

    'PLL_TYPES': {
        0: "None",
        1: "MMCME4_ADV",
    },

    'CHIPMON_TYPES': {
        0: "None",
        1: "SYSMONE4",
    },

    'IIC_OFFLOAD_TYPES': {
        0: "None",
        1: "Xilinx AXI-IIC",
    },

    'PCIE_TYPES': {
        0: "None",
        1: "Xilinx PCIE40E4--based XDMA",
    },

}
