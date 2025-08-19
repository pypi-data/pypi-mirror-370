#!/usr/bin/python3

# SPDX-License-Identifier: MPL-2.0

import time
import signal
import re
import os
import sys
import getopt
import getpass
import shutil
import shlex
import traceback
import subprocess
import socket

# requres PySerial package:
import serial # maybe at some point, pull this in, as PySerial is pure python.
import serial.tools.list_ports

from opencos import util
from opencos import names as opencos_names
from opencos.hw import pcie


util.progname_in_message = False # too noise for this use case

# **************************************************************
# **** Readline related

try:
    import readline
    got_readline = 1
except:
    got_readline = 0
    pass

if got_readline:
    histfile = os.path.join(os.path.expanduser("~"), ".oc_cli_history")
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

# **************************************************************
# **** Global vars

global_vars = {}

def apply_global_vars(text):
    global global_vars
    for key in global_vars.keys():
        text = text.replace("$%s" % key, global_vars[key])
    return text

def eval_true(text):
    tt = apply_global_vars(text).lower()
    if tt=="t" or tt=="true" or tt=="1" or tt=="yes" or tt=="on": return True
    if tt=="f" or tt=="false" or tt=="0" or tt=="no" or tt=="off": return False
    util.warning(f"Expected a boolean, got '{text}', assuming that means 'False'")
    return False

def eval_number(text, ishex=False, check_uint_bits=False, check_int_min=False, check_int_max=False):
    # if we've been given an int already, set the value to that
    if isinstance(text, int):
        value = text
    else:
        mult = 1
        # do variable substitution
        text = apply_global_vars(text)
        # look for a prefix for human friendly number, note these suffixes work on hex numbers too
        m = re.match(r'^(.*)[Kk]$', text)
        if m:
            mult = 1024
            text = m.group(1)
        m = re.match(r'^(.*)[Mm]$', text)
        if m:
            mult = 1024*1024
            text = m.group(1)
        m = re.match(r'^(.*)[Gg]$', text)
        if m:
            mult = 1024*1024*1024
            text = m.group(1)
        # substition is done, multiplier is extracted, time to look for a number
        value = False
        if not ishex: # if we've been told it's hex, we don't do this match, because hex can look decimal
            m = re.match(r'^(\d+)$', text)
            if m: value = int(m.group(1)) * mult
        if (type(value) != int):
            m = re.match(r'^0x([\da-fA-F]+)$', text) # if it's starts with 0x, then it's hex
            if m: value = int(m.group(1), 16) * mult
        if (type(value) != int):
            m = re.match(r'^([\da-fA-F]+)$', text) # if it has a-f, then it's hex
            if m: value = int(m.group(1), 16) * mult
        # if we don't have value as an int by here, we are out of ideas
        if (type(value) != int):
            util.error(f"Expected a number, got '{text}'", do_exit=False)
            raise HandledError
    # if we're given a number of uint bits to check, convert to int min/max
    if (type(check_uint_bits) == int):
        check_int_min = 0
        check_int_max = (1 << check_uint_bits)-1
    # check value is within int min/max
    if (type(check_int_min) == int):
        if (value < check_int_min):
            util.error(f"Expected a number >= {check_int_min}, got {value}", do_exit=False)
            raise HandledError
    if (type(check_int_max) == int):
        if (value > check_int_max):
            util.error(f"Expected a number <= {check_int_max}, got {value}", do_exit=False)
            raise HandledError
    return value

def eval_regex(regex, text):
    global m
    text = apply_global_vars(text)
    m = re.match(regex, text)
    return m

# **************************************************************
# **** Serial-Over-TCP

class FakeSerial:
    def __init__(self, port, timeout) -> None:
        try:
            tcpTuple = port.split(":", 1)[1].split(",")
            self.ip = tcpTuple[0]
            self.baseport = int(tcpTuple[1])
            self.devno = int(tcpTuple[2])
            self.inBuf = bytearray()
            self.timeout = timeout
        except:
            raise AttributeError("Fake serial port must be specified as: tcp:IPAddress,UARTBasePort,UARTDeviceNumber")
        self.sck = socket.create_connection(("127.0.0.1", self.baseport+self.devno))
        self.sck.settimeout(0)
    def read(self, nBytes):

        starttime = time.monotonic()

        while (len(self.inBuf) < nBytes) and ((time.monotonic() - starttime) < self.timeout):
            try:
                data = self.sck.recv(4096)
            except BlockingIOError:
                data = b''
            self.inBuf.extend(data)

        requested = self.inBuf[:nBytes]
        nextdata = self.inBuf[nBytes:]
        self.inBuf = nextdata
        return bytes(requested)
    def write(self, data):
        ret = self.sck.send(data)
        return ret
    def close(self):
        self.sck.close()
    @property
    def in_waiting(self):
        return len(self.inBuf)
    @property
    def out_waiting(self):
        return 0

# **************************************************************
# **** XXTEA for Protection

# ported from https://en.wikipedia.org/wiki/XXTEA

def btea (vin, n, key):
    v = vin
    DELTA = 0x9e3779b9
    if (n > 1): # Encoding part
        rounds = int(6 + 52/n)
        s = 0
        z = v[n-1]
        while rounds:
            s = (s + DELTA) & 0xffffffff
            e = (s >> 2) & 3;
            for p in range(n-1):
                y = v[p+1]
                v[p] = (v[p] + (((z>>5^y<<2) + (y>>3^z<<4)) ^ ((s^y) + (key[(p&3)^e] ^ z)))) & 0xffffffff
                z = v[p]
            p = n-1
            y = v[0]
            v[n-1] = (v[n-1] + (((z>>5^y<<2) + (y>>3^z<<4)) ^ ((s^y) + (key[(p&3)^e] ^ z)))) & 0xffffffff
            z = v[n-1]
            rounds -= 1
    elif (n < -1): # Decoding part
        n = -n
        rounds = int(6 + 52/n)
        s = (rounds * DELTA) & 0xffffffff
        y = v[0]
        while rounds:
            e = (s >> 2) & 3
            for p in range(n-1, 0, -1):
                z = v[p-1]
                v[p] = (v[p] - (((z>>5^y<<2) + (y>>3^z<<4)) ^ ((s^y) + (key[(p&3)^e] ^ z)))) & 0xffffffff
                y = v[p]
            p = 0
            z = v[n-1]
            v[0] = (v[0] - (((z>>5^y<<2) + (y>>3^z<<4)) ^ ((s^y) + (key[(p&3)^e] ^ z)))) & 0xffffffff
            y = v[0]
            s = (s - DELTA) & 0xffffffff
            rounds -= 1
    return v

# **************************************************************
# **** Blocks
block_table = {}

class Block():
    def __init__(self, channel, blockid, name="Unknown"):
        self.channel = channel
        self.blockid = blockid
        self.name = name

    def __str__(self):
        return f"Block {self.name} [{self.blockid}]"

    def info    (self, text): util.info    (f"{self.name}[{self.blockid}]: {text}")
    def debug   (self, text): util.debug   (f"{self.name}[{self.blockid}]: {text}")
    def warning (self, text): util.warning (f"{self.name}[{self.blockid}]: {text}")
    def error   (self, text): util.error   (f"{self.name}[{self.blockid}]: {text}")

    def connect(self):
        util.debug(f"Connecting {self.name}@{self.blockid}")

    def disconnect(self):
        util.debug(f"Disconnecting {self.name}@{self.blockid}")

    def csr_read32(self, space, address, msgid=0, verbose=False):
        util.debug(f"{self}: csr_read32(space={space},address={address:08x})")
        return self.channel.csr_read32(self.blockid, space, address, msgid, verbose)

    def csr_write32(self, space, address, data, msgid=0, verbose=False):
        util.debug(f"{self}: csr_write32(space={space},address={address:08x}, data={data:08x})")
        return self.channel.csr_write32(self.blockid, space, address, data, msgid, verbose)

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        self.warning(f"Command 'show' was called on a block type for which there is no handler")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.warning(f"Command 'dump' was called on a block type for which there is no handler")

    def command_help(self, parts=[], help_line=False):
        if help_line: return "This help";
        util.info(f"Help for {self}")
        for func in sorted([a for a in dir(self) if callable(getattr(self, a))]):
            m = re.match(r'command_(\w+)', func)
            if m:
                cmd = m.group(1)
                util.info(f"{cmd:20} : {getattr(self,func)(help_line=True)}")

    def dump_reg (self, space, address, name, fields=[], end='\n'):
        data = self.csr_read32(space, address)
        util.info("REG [%02x][%01x][%08x] (%-28s) = %08x" % (self.blockid, space, address, name, data), end=end)
        for field in fields:
            msb = field[0]
            lsb = field[1]
            fieldname = field[2]
            width = (msb-lsb+1)
            mask = (1<<width)-1
            if msb == lsb:
                util.info("                 [%2d] %-28s   = %8x" % (lsb, fieldname, ((data >> lsb) & 1)))
            else:
                digits = int((width+3)/4)
                fmt = "              [%%2d:%%2d] %%-28s   = %s%%0%dx" % (' '*(8-digits), digits)
                util.info(fmt % (msb, lsb, fieldname, ((data >> lsb) & mask)), end=end)
        return data

    def process_tokens(self, parts):
        command = parts.pop(0)
        if (f"command_{command}" in dir(self)) and callable(getattr(self,f"command_{command}")):
            util.debug(f"About to launch into method command_{command}")
            getattr(self,f"command_{command}")(parts)
        else:
            util.warning(f"Didn't understand command: '{command}'")

class BlockPll(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "PLL")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.pll_type = ((data >> 8) & 0xff)
        self.pll_name = lookup_table_string('PLL_TYPES',self.pll_type)
        self.out_clock_count = ((data >> 4) & 0xf)
        self.auto_throttle = ((data >> 2) & 0x1)
        self.throttle_map = ((data >> 1) & 0x1)
        self.measure_enable = ((data >> 0) & 0x1)
        util.debug(f"Connect: {self} CsrId={self.csrid} PllType={self.pll_name} "+
                   f"AutoThrottle={self.auto_throttle},ThrottleMap={self.throttle_map},MeasureEnable={self.measure_enable}")

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        util.info(f"Showing {self}: Features: AutoThrottle={self.auto_throttle},ThrottleMap={self.throttle_map},MeasureEnable={self.measure_enable}")
        util.info(f"CsrId={self.csrid} PllType={self.pll_name} ")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        cfg = self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [15,8,"TYPE"], [7,4,"OUT_CLOCK_COUNT"],
                                                 [2,2,"AUTO_THROTTLE"], [1,1,"THROTTLE_MAP"], [0,0,"MEASURE_ENABLE"] ])
        clocks = ((cfg>>4) & 0xf)
        self.dump_reg(0, 0x0004, "OcPll0", [ [31,31,"PLL_LOCKED"], [21,21,"THERMAL_ERROR"], [20,20,"THERMAL_WARNING"],
                                             [17,17,"CLK_FB_STOPPED"], [16,16,"CLK_IN_STOPPED"],
                                             [5,5,"CDDC_DONE"], [4,4,"CDDC_REQ"],
                                             [1,1,"POWER_DOWN"], [0,0,"RESET"] ])
        for i in range(clocks):
            self.dump_reg(0, 0x0008+(4*i), "OcPllClk%d"%i, [ [31,16,"MEASURE_COUNT"], [15,8,"THROTTLE_MAP"],
                                                             [1,1,"ENABLE_AUTO_THROTTLE"], [0,0,"FORCE_AUTO_THROTTLE"] ])
        self.dump_reg(1, 0x004f, "FiltReg2", [ [15,8,"RESISTOR"], [7,4,"CAPACITOR"] ])
        self.dump_reg(1, 0x004e, "FiltReg1", [ [15,8,"CHARGE PUMP"] ])
        self.dump_reg(1, 0x0027, "PowerReg", [ [15,0,"INTERPOLATOR"] ])
        self.dump_reg(1, 0x001a, "LockReg3", [ [14, 10, "REF DELAY"], [9, 0, "SAT_HIGH"] ])
        self.dump_reg(1, 0x0019, "LockReg2", [ [14, 10, "FB DELAY"], [9, 0, "UNLOCK_CNT"] ])
        self.dump_reg(1, 0x0018, "LockReg1", [ [9, 0, "LOCK_CNT"] ])
        self.dump_reg(1, 0x0016, "DivReg", [ [13, 13, "EDGE"], [11, 6, "HIGH TIME"], [5, 0, "LOW_TIME"] ])
        self.dump_reg(1, 0x0015, "CLKFBOUT", [ [14,12,"FRAC_PHASE"], [11,11,"FRAC_EN"], [10,10,"FRAC_WF_R"],
                                               [7,7,"EDGE"], [6,6,"NO_COUNT"], [5,0,"FRAC"] ])
        self.dump_reg(1, 0x0014, "CLKFBOUT", [ [15,13,"PHASE_SELECT_RISE"], [12,12,"COUNTER_EN"],
                                               [11,6,"HIGH_TIME"], [5,0,"LOW_TIME"] ])
        self.dump_reg(1, 0x0013, "CLKFBOUT/CLKOUT[6]", [ [15,13,"PHASE_SELECT_FALL"], [12,12,"FRAC_WF_R"],
                                                         [10,10,"CLKOUT6_CDDC_EN"], [7,7,"CLKOUT6_EDGE"],
                                                         [6,6,"CLKOUT6_NO_COUNT"], [5,0,"CLKOUT6_DELAY"] ])
        self.dump_reg(1, 0x0012, "CLKOUT[6]", [ [15,13,"PHASE_SELECT"], [12,12,"COUNTER_EN"],
                                                [11,6,"HIGH_TIME"], [5,0,"LOW_TIME"] ])
        for clkout in [4, 3, 2, 1]:
            self.dump_reg(1, 0x0011-((4-clkout)*2), "CLKOUT[%d]"%clkout, [ [10,10,"CDDC_EN"], [7,7,"EDGE"],
                                                                           [6,6,"NO_COUNT"], [5,0,"DELAY"] ])
        self.dump_reg(1, 0x0010-((4-clkout)*2), "CLKOUT[%d]"%clkout, [ [15,13,"PHASE_SELECT"], [12,12,"COUNTER_EN"],
                                                                       [11,6,"HIGH_TIME"], [5,0,"LOW_TIME"] ])
        self.dump_reg(1, 0x0009, "CLKOUT[0]", [ [ 15, 15, "CDDC_EN" ], [ 14, 12, "FRAC_PHASE" ], [ 11, 11, "FRAC_EN" ],
                                                [ 10, 10, "FRAC_WF_R" ], [  9,  8, "MX" ], [  7,  7, "EDGE" ],
                                                [  6,  6, "NO_COUNT" ], [  5,  0, "DELAY" ] ])
        self.dump_reg(1, 0x0008, "CLKOUT[0]", [ [ 15, 13, "PHASE_SELECT_RISE" ], [ 12, 12, "COUNTER_EN" ],
                                                [ 11,  6, "HIGH_TIME" ], [  5,  0, "LOW_TIME" ] ])
        self.dump_reg(1, 0x0007, "CLKOUT[0]/CLKOUT[5]", [ [ 15, 13, "PHASE_SELECT_FALL" ], [ 12, 12, "FRAC_WF_F" ],
                                                          [ 10, 10, "CLKOUT5_CDDC_EN" ], [  7,  7, "CLKOUT5_EDGE" ],
                                                          [  6,  6, "CLKOUT5_NO_COUNT" ], [  5,  0, "CLKOUT6_DELAY" ] ])
        self.dump_reg(1, 0x0006, "CLKOUT[5]", [ [ 15, 13, "PHASE_SELECT" ], [ 12, 12, "COUNTER_EN" ],
                                                [ 11,  6, "HIGH_TIME" ], [  5,  0, "LOW_TIME" ] ])
        for clock in range(1):
            util.info(f"{self}: Measuring clock {clock}...")
            self.command_measure(["1", f"{clock}"])

    def command_throttle(self, parts=[], help_line=False):
        if help_line: return "Enables clock skipping, 0-8 for the number of cycles to skip in each 8-clock window"
        if len(parts)<1:
            util.error(f"Need argument for 'throttle', 0-8, the number of cycles to skip in each 8 cycle window", do_exit=False)
            raise HandledError

        throttle_count = eval_number(parts.pop(0), ishex=True, check_int_min=0, check_int_max=255)
        self.csr_write32(0, 0x0008, ((1 << throttle_count)-1) << 8)
        util.info(f"{self}: throttled clock[0] to the following pattern: {((1 << throttle_count)-1):08b}")

    def command_reset(self, parts=[], help_line=False):
        if help_line: return "Reset the PLL, 'assert' or 'deassert' to do one (default is both) and add 'ramp' to throttle down and up";
        assert_reset = True
        deassert_reset = True
        ramp_throttle = False
        for p in parts:
            if p == 'assert': deassert_reset = False
            elif p == 'deassert': assert_reset = False
            elif p == 'ramp' : ramp_throttle = True
            else :
                util.error(f"'reset' doesn't understand argument '{p}'", do_exit=False)
                raise HandledError
        if ramp_throttle:
            # we have been told to ramp throttle, i.e. to be careful about how fast we change current load
            # we start by sampling the current throttle map and we start ramping down from there, and after
            # reset we will ramp back up to the same setting
            data = ((self.csr_read32(0, 0x0008) >> 8) & 0xff)
            starting_throttle = 0
            for i in range(8): starting_throttle += (1 if (data & (1<<i)) else 0)
            if starting_throttle != 0:
                util.info(f"{self}: Ramping enabled, and starting throttle count was {starting_throttle}")
                util.info(f"{self}: Will ramp down from there, and back up to there")
        if assert_reset:
            if ramp_throttle:
                for throttle_count in range(starting_throttle, 9, 1):
                    self.csr_write32(0, 0x0008, ((1 << throttle_count)-1) << 8)
            self.csr_write32(0, 0x0004, 0x00000001) # assert reset
            util.info(f"{self}: reset asserted")
        if deassert_reset:
            self.csr_write32(0, 0x0004, 0x00000000) # deassert reset
            # after releasing reset, ramp up the throttle
            if ramp_throttle:
                for throttle_count in range(8, (starting_throttle-1), -1):
                    self.csr_write32(0, 0x0008, ((1 << throttle_count)-1) << 8)
            util.info(f"{self}: reset deasserted")

    def command_measure(self, parts=[], help_line=False):
        if help_line: return "Measure a PLL output clock.  First arg is measurement seconds (default=1), next is output (default=0)"
        if not self.measure_enable:
            util.info(f"{self}: Skipping measure since PLL doesn't have support")
            return
        measure_seconds = 1
        measure_clock = 0
        if len(parts)>0: measure_seconds = eval_number(parts.pop(0), check_int_min=0, check_int_max=30)
        if len(parts)>0: measure_clock = eval_number(parts.pop(0), check_int_min=0, check_int_max=(self.out_clock_count-1))
        if len(parts):
            util.error(f"measure didn't understand arg(s): {parts}", do_exit=False)
            raise HandledError
        start = self.csr_read32(0, 0x0008 + (measure_clock*4)) >> 16
        start_time = time.time()
        time.sleep(measure_seconds)
        stop = self.csr_read32(0, 0x0008 + (measure_clock*4)) >> 16
        stop_time = time.time()
        if (stop < start): stop += 0x10000
        mhz = (65536.0 * (stop-start)) / ((stop_time-start_time) * 1000000.0)
        util.info(f"{self}: clock[{measure_clock}] is {mhz:.3f} MHz")

    def command_clk0_up(self, parts=[], help_line=False):
        if help_line: return "Reduces fractional phase, DRP REG 0x09 [14:12], speeding up clock 0 on this PLL"
        orig = self.csr_read32(1, 0x0009)
        keep = orig & 0x00008fff
        newval = ((orig >> 12) & 7)-1
        if newval == -1:
            util.info("Cannot go further")
            return
        self.command_reset(['assert', 'ramp'])
        self.csr_write32(1, 0x0009, keep | (newval<<12))
        self.command_reset(['deassert', 'ramp'])
        self.command_measure()

    def command_clk0_down(self, parts=[], help_line=False):
        if help_line: return "Increases fractional phase, DRP REG 0x09 [14:12], slowing down clock 0 on this PLL"
        orig = self.csr_read32(1, 0x0009)
        keep = orig & 0x00008fff
        newval = ((orig >> 12) & 7)+1
        if newval == 8:
            util.info("Cannot go further")
            return
        self.command_reset(['assert', 'ramp'])
        self.csr_write32(1, 0x0009, keep | (newval<<12))
        self.command_reset(['deassert', 'ramp'])
        self.command_measure()

    def command_all_up(self, parts=[], help_line=False):
        if help_line: return "Increases one of the feedback dividers, DRP REG 0x14 [11:0], speeding up all clocks on this PLL"
        orig = self.csr_read32(1, 0x0014)
        keep = orig & 0xf000
        low = (orig >> 0) & 31 # clock low time
        high = (orig >> 6) & 31 # clock high time
        # we need to increment, and will increment whichever is lower
        if (high == 31) and (low == 31):
            util.info("Cannot go further")
            return
        if (low <= high): low += 1
        else: high += 1
        self.command_reset(['assert', 'ramp'])
        self.csr_write32(1, 0x0014, keep | (low<<0) | (high<<6))
        self.command_reset(['deassert', 'ramp'])
        self.command_measure()

    def command_all_down(self, parts=[], help_line=False):
        if help_line: return "Decreases one of the feedback dividers, DRP REG 0x14 [11:0], slowing down all clocks on this PLL"
        orig = self.csr_read32(1, 0x0014)
        keep = orig & 0xf000
        low = (orig >> 0) & 31 # clock low time
        high = (orig >> 6) & 31 # clock high time
        # we need to increment, and will increment whichever is lower
        if (high == 0) and (low == 0):
            util.info("Cannot go further")
            return
        if (low >= high): low -= 1
        else: high -= 1
        self.command_reset(['assert', 'ramp'])
        self.csr_write32(1, 0x0014, keep | (low<<0) | (high<<6))
        self.command_reset(['deassert', 'ramp'])
        self.command_measure()

    def command_scan(self, parts=[], help_line=False):
        if help_line: return "Scans the CLK0 frac_phase, measuring PLL freqs at each step"
        orig = self.csr_read32(1, 0x0009)
        keep = orig & 0x00008fff
        for i in range(0, 8, 1):
            util.info(f"{self}: writing CLK0 frac_phase to {i}")
            self.command_reset(['assert', 'ramp'])
            self.csr_write32(1, 0x0009, keep | (i<<12))
            self.command_reset(['deassert', 'ramp'])
            self.command_measure()
        self.command_reset(['assert', 'ramp'])
        self.csr_write32(1, 0x0009, orig)
        self.command_reset(['deassert', 'ramp'])

class BlockChipMon(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "ChipMon")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.chipmon_type = ((data >> 8) & 0xff)
        self.chipmon_name = lookup_table_string('CHIPMON_TYPES',self.chipmon_type)
        self.internal_reference = ((data >> 0) & 0x1)
        util.debug(f"Connect: {self} CsrId={self.csrid} ChipMonType={self.chipmon_name} "+
                   f"InternalReference={self.internal_reference}")

    def chipmon_code_to_temp(self, code):
        return (((code * 507.5921310)/65536)-279.42657680)

    def chipmon_code_to_volt(self, code, voltagerange="normal"):
        if voltagerange=="normal": return 3.0*(code/65536)
        else: return 6.0*(code/65536)

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        util.info(f"Showing {self}: ({self.chipmon_name})")
        util.info(f"CsrId={self.csrid} InternalReference={self.internal_reference}")
        t = self.chipmon_code_to_temp(self.csr_read32(1, 0x0))
        t_min = self.chipmon_code_to_temp(self.csr_read32(1, 0x24))
        t_max = self.chipmon_code_to_temp(self.csr_read32(1, 0x20))
        vint = self.chipmon_code_to_volt(self.csr_read32(1, 0x1))
        vint_min = self.chipmon_code_to_volt(self.csr_read32(1, 0x25))
        vint_max = self.chipmon_code_to_volt(self.csr_read32(1, 0x21))
        vaux = self.chipmon_code_to_volt(self.csr_read32(1, 0x2))
        vaux_min = self.chipmon_code_to_volt(self.csr_read32(1, 0x26))
        vaux_max = self.chipmon_code_to_volt(self.csr_read32(1, 0x22))
        vbram = self.chipmon_code_to_volt(self.csr_read32(1, 0x6))
        vbram_min = self.chipmon_code_to_volt(self.csr_read32(1, 0x27))
        vbram_max = self.chipmon_code_to_volt(self.csr_read32(1, 0x23))
        util.info(f"Temperature : {t:5.1f}C (seen {t_min:5.1f}C - {t_max:5.1f}C)")
        util.info(f"VCCint      : {vint:5.3f}V (seen {vint_min:5.3f}V - {vint_max:5.3f}V)")
        util.info(f"VCCaux      : {vaux:5.3f}V (seen {vaux_min:5.3f}V - {vaux_max:5.3f}V)")
        util.info(f"VCCbram     : {vbram:5.3f}V (seen {vbram_min:5.3f}V - {vbram_max:5.3f}V)")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"],
                                           [15,8,"CHIPMON_TYPE"], [0,0,"INTERNAL_REF"] ])
        self.dump_reg(0, 0x0001, "OcChipMon0", [ [29,29,"JTAG_BUSY"], [29,29,"JTAG_MODIFIED"],
                                                 [28,28,"JTAG_LOCKED"], [0,0,"RESET"] ])
        self.dump_reg(0, 0x0002, "OcChipMon1", [ [31,16,"ALARM"], [0,0,"OVER_TEMP"] ])
        self.dump_reg(1, 0x003e, "Flags1", [ [3,0,"ALARM[11:8]"] ])
        self.dump_reg(1, 0x003f, "Flags2", [ [11,11,"JTAG_DISABLE"], [10,10,"JTAG_RESTRICTED"],
                                             [9,9,"INTERNAL_REFERENCE"],
                                             [7,4,"ALARM[6:3]"], [3,3,"OVER_TEMP"], [2,0,"ALARM[2:0]"]])
        self.dump_reg(1, 0x0040, "ConfigReg0", [ [15,15,"DISABLE_CAL"], [13,12,"SAMPLE_AVERAGING"],
                                                 [11,11,"EXT_MUX_MODE"], [10,10,"BIPOLAR_INPUTS"],
                                                 [9,9,"EVENT_DRIVEN"], [8,8,"10_CYCLE_SLOW_ACQ"],
                                                 [5,0,"CHANNEL"] ])
        self.dump_reg(1, 0x0041, "ConfigReg1", [ [15,12,"SEQUENCER_MODE"], [11,8,"ALARM_DISABLE[6:3]"],
                                                 [7,4,"CAL[3:2:-:0]"], [3,1,"ALARM_DISABLE[2:0]"],
                                                 [0,0,"OVER_TEMP_DISABLE"]])
        self.dump_reg(1, 0x0042, "ConfigReg2", [ [15,8,"ADCCLK_DIV"] ])
        self.dump_reg(1, 0x0043, "ConfigReg3", [ [14,8,"I2C_ADDR"], [7,7,"I2C_ENABLE"],
                                                 [3,0,"ALARM_DISABLE[11:8]"]])
        self.dump_reg(1, 0x0044, "ConfigReg4", [ [11,10,"SLOW_EOS"], [9,8,"SLOW_SEQ"], [3,0,"PMBUS_HRIO"]])
        self.dump_reg(1, 0x0046, "SequenceReg0", [ [3,3,"CHSEL_USER3"], [2,2,"CHSEL_USER2"],
                                                   [1,1,"CHSEL_USER1"], [0,0,"CHSEL_USER0"] ])
        self.dump_reg(1, 0x0048, "SequenceReg1", [ [14,14,"CHSEL_BRAM_AVG"], [13,13,"CHSEL_VREFN"],
                                                   [12,12,"CHSEL_VREFP"], [11,11,"CHSEL_VPVN"],
                                                   [10,10,"CHSEL_AUX_AVG"], [9,9,"CHSEL_INT_AVG"],
                                                   [8,8,"CHSEL_TEMP"], [7,7,"CHSEL_VCC_PSAUX"],
                                                   [6,6,"CHSEL_VCC_PSINTFP"], [5,5,"CHSEL_VCC_PSINTLP"],
                                                   [0,0,"CHSEL_SYSMON_CAL"] ])
        self.dump_reg(1, 0x0049, "SequenceReg2", [ [15,0,"CHSEL_AUX[15:0]"]])
        self.dump_reg(1, 0x007a, "SlowChSel0", [ [14,14,"SLOW_BRAM"], [13,13,"SLOW_VREFN"], [12,12,"SLOW_VREFP"],
                                                 [11,11,"SLOW_VPVN"], [10,10,"SLOW_AUX_AVG"], [9,9,"SLOW_INT_AVG"],
                                                 [8,8,"SLOW_TEMP"], [7,7,"SLOW_VCC_PSAUX"], [6,6,"SLOW_VCC_PSINTFP"],
                                                 [5,5,"SLOW_VCC_PSINTLP"], [0,0,"SLOW_SYSMON"]])
        self.dump_reg(1, 0x007b, "SlowChSel1", [ [15,0,"SLOW_AUX[15:0]"]])
        self.dump_reg(1, 0x007c, "SlowChSel2", [ [3,0,"SLOW_USER[3:0]"]])
        self.dump_reg(1, 0x0047, "AvgChSel0", [ [3,0,"AVG_USER[3:0]"]])
        self.dump_reg(1, 0x004a, "AvgChSel1", [ [15,0,"AVG_AUX[15:0]"]])
        self.dump_reg(1, 0x004b, "AvgChSel2", [ [14,14,"AVG_BRAM"],
                                                [11,11,"AVG_VPVN"], [10,10,"AVG_AUX_AVG"], [9,9,"AVG_INT_AVG"],
                                                [8,8,"AVG_TEMP"], [7,7,"AVG_VCC_PSAUX"], [6,6,"AVG_VCC_PSINTFP"],
                                                [5,5,"AVG_VCC_PSINTLP"]])
        self.dump_reg(1, 0x004c, "SeqInMode0", [ [11,11,"INSEL_VPVN"]])
        self.dump_reg(1, 0x004d, "SeqInMode1", [ [15,0,"INSEL_AUX[15:0]"]])
        self.dump_reg(1, 0x004e, "SeqAcq0", [ [11,11,"ACQ_VPVN"]])
        self.dump_reg(1, 0x004f, "SeqAcq1", [ [15,0,"ACQ_AUX[15:0]"]])

        data = self.dump_reg(1, 0x0050, "Temperature Upper", [], end="")
        print(" (%.1fC)" % (self.chipmon_code_to_temp(data)))
        data = self.dump_reg(1, 0x0051, "VCCint Upper", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0052, "VCCaux Upper", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0053, "Over Temp Upper", [], end='')
        print(" (%.1fC)" % (self.chipmon_code_to_temp(data)))
        data = self.dump_reg(1, 0x0054, "Temperature Lower", [], end='')
        print(" (%.1fC)" % (self.chipmon_code_to_temp(data)))
        data = self.dump_reg(1, 0x0055, "VCCint Lower", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0056, "VCCaux Lower", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0057, "Over Temp Lower", [], end='')
        print(" (%.1fC)" % (self.chipmon_code_to_temp(data)))
        data = self.dump_reg(1, 0x0058, "VCCbram Upper", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x005c, "VCCbram Lower", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0000, "Temperature", [], end='')
        print(" (%.1fC)" % (self.chipmon_code_to_temp(data)))
        data = self.dump_reg(1, 0x0001, "VCCint", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0002, "VCCaux", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0006, "VCCbram", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0020, "Max Temperature", [], end='')
        print(" (%.1fC)" % (self.chipmon_code_to_temp(data)))
        data = self.dump_reg(1, 0x0021, "Max VCCint", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0022, "Max VCCaux", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0023, "Max VCCbram", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0024, "Min Temperature", [], end='')
        print(" (%.1fC)" % (self.chipmon_code_to_temp(data)))
        data = self.dump_reg(1, 0x0025, "Min VCCint", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0026, "Min VCCaux", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))
        data = self.dump_reg(1, 0x0027, "Min VCCbram", [], end='')
        print(" (%.3fV)" % (self.chipmon_code_to_volt(data)))

class BlockLED(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "LED")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.numled = ((data) & 0xff)
        util.debug(f"Connect: {self} CsrId={self.csrid} NumLed={self.numled}")

    def led_status(self, led):
        data = self.csr_read32(0, 8 + (led*4))
        blinks = ((data>>16) & 0x07)
        bright_pct = (100 * ((data >> 8) & 0x3f) / 63)
        if ((data & 0x3) == 1):   return (f"on ({bright_pct}% bright)")
        elif ((data & 0x3) == 2): return (f"blink ({blinks} times, {bright_pct}% bright)")
        elif ((data & 0x3) == 3): return (f"heartbeat ({bright_pct}% bright)")
        return "off"

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        for i in range(self.numled):
            util.info(f"LED {i:3}: {self.led_status(i):20}")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        data = self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [7,0,"LED_COUNT"] ])
        count = data & 0xff
        self.dump_reg(0, 0x0004, "Prescale", [ [9,0,"CYCLES"] ])
        for i in range(count):
            self.dump_reg(0, 0x0008+(i*4), "LedControl%d" % i, [ [18,16,"BLINKS"], [13,8,"BRIGHT"], [1,0,"MODE"] ])

    def command_set(self, parts=[], help_line=False):
        if help_line: return "Set the state of the led: [on|off|blink|heartbeat] [brightness=0-63]";
        led = -1
        bright = 0x3f
        blinks = 1
        command = -1 # report status
        prescale = -1
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^(\d+)$', cmd)):
                led = eval_number(m.group(1))
            elif (eval_regex(r'^status$', cmd)):
                command = -1
            elif (eval_regex(r'^off$', cmd)):
                command = 0
            elif (eval_regex(r'^on$', cmd)):
                command = 1
            elif (eval_regex(r'^blink$', cmd)):
                command = 2
            elif (eval_regex(r'^(?:heart)?beat$', cmd)):
                command = 3
            elif (eval_regex(r'^prescale=(.+)', cmd)):
                prescale = eval_number(m.group(1), check_uint_bits=10, check_int_min=5)
            elif (eval_regex(r'^bright(?:ness)?=(.+)', cmd)):
                bright = eval_number(m.group(1), check_uint_bits=6)
            elif (eval_regex(r'^blink(?:s)?=(.+)', cmd)):
                blinks = eval_number(m.group(1), check_uint_bits=3)
            else:
                util.error(f"LED didn't understand arg(s): {parts}", do_exit=False)
                raise HandledError
        if prescale != -1:
            self.csr_write32(0, 4, prescale)
        if command == -1: # we reporting status
            if led == -1: # on all LEDs
                for i in range(self.numled): print("LED %3d : %s" % (  i, self.led_status(  i)))
            else:                            print("LED %3d : %s" % (led, self.led_status(led)))
        else:
            if led == -1: # on all LEDs
                for i in range(self.numled): self.csr_write32(0, 8 + (  i*4), ((blinks<<16) | (bright<<8) | command) )
            else:                            self.csr_write32(0, 8 + (led*4), ((blinks<<16) | (bright<<8) | command) )

class BlockRGB(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "RGB")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.numrgb = ((data) & 0xff)
        util.debug(f"Connect: {self} CsrId={self.csrid} NumRgb={self.numrgb}")

    def rgb_status(self, rgb):
        data = self.csr_read32(0, 8 + (rgb*4))
        red = ((data >> 24) & 0x3f)
        green = ((data >>16) & 0x3f)
        blue = ((data >> 8) & 0x3f)
        if (data & 0x1) == 1: return (f"on ({red:3d} {green:3d} {blue:3d})")
        elif (data & 0x2) == 2: return (f"blink ({red:3d} {green:3d} {blue:3d})")
        elif (data & 0x3) == 3: return (f"heartbeat ({red:3d} {green:3d} {blue:3d})")
        return "off"

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        for i in range(self.numrgb):
            util.info(f"RGB {i:3}: {self.rgb_status(i):20}")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        data = self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [7,0,"RGB_COUNT"] ])
        count = data & 0xff
        self.dump_reg(0, 0x0004, "Prescale", [ [9,0,"CYCLES"] ])
        for i in range(count):
            self.dump_reg(0, 0x0008+(i*4), "RgbControl%d" % i, [ [24,24,"RED"], [16,16,"GREEN"], [8,8,"BLUE"], [0,0,"MODE"] ])

    def command_set(self, parts=[], help_line=False):
        if help_line: return "Set the state of the rgb: [on|off|blink|heartbeat] [red=0-63] [green=0-63] [blue=0-63]";
        rgb = -1
        red = 0x3f
        green = 0x3f
        blue = 0x3f
        command = -1 # report status
        prescale = -1
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^(\d+)$', cmd)):
                rgb = eval_number(m.group(1))
            elif (eval_regex(r'^status$', cmd)):
                command = -1
            elif (eval_regex(r'^off$', cmd)):
                command = 0
            elif (eval_regex(r'^on$', cmd)):
                command = 1
            elif (eval_regex(r'^blink$', cmd)):
                command = 2
            elif (eval_regex(r'^(?:heart)?beat$', cmd)):
                command = 3
            elif (eval_regex(r'^prescale=(.+)', cmd)):
                prescale = eval_number(m.group(1), check_uint_bits=10, check_int_min=5)
            elif (eval_regex(r'^red=(.+)', cmd)):
                red = eval_number(m.group(1), check_uint_bits=6)
            elif (eval_regex(r'^green=(.+)', cmd)):
                green = eval_number(m.group(1), check_uint_bits=6)
            elif (eval_regex(r'^blue=(.+)', cmd)):
                blue = eval_number(m.group(1), check_uint_bits=6)
            else:
                util.error(f"RGB didn't understand arg(s): {parts}", do_exit=False)
                raise HandledError
        if prescale != -1:
            self.csr_write32(0, 4, prescale)
        if command == -1: # we reporting status
            if rgb == -1: # on all RGBs
                for i in range(self.numrgb): print("RGB %3d : %s" % (  i, self.rgb_status(  i)))
            else:                            print("RGB %3d : %s" % (rgb, self.rgb_status(rgb)))
        else:
            if rgb == -1: # on all RGBs
                for i in range(self.numrgb): self.csr_write32(0, 8 + (  i*4), ((blue<<24) | (green<<16) | (red<<8) | command) )
            else:                            self.csr_write32(0, 8 + (rgb*4), ((blue<<24) | (green<<16) | (red<<8) | command) )

class BlockToggle(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "Toggle")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.numtoggle = ((data) & 0xff)
        util.debug(f"Connect: {self} CsrId={self.csrid} NumToggle={self.numtoggle}")

    def toggle_status(self, toggle):
        data = self.csr_read32(0, 4 + (toggle*4))
        if (data & 0x80000000): return "on"
        return "off"

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        for i in range(self.numtoggle):
            util.info(f"Toggle {i:3}: {self.toggle_status(i):20}")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        data = self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [7,0,"TOGGLE_COUNT"] ])
        count = data & 0xff
        for i in range(count):
            self.dump_reg(0, 0x0004+(i*4), "ToggleStatus%d" % i, [ [31,31,"STATE"], [30,30,"EVENT"], [15,0,"COUNT"] ])

class BlockButton(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "Button")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.numbutton = ((data) & 0xff)
        util.debug(f"Connect: {self} CsrId={self.csrid} NumButton={self.numbutton}")

    def button_status(self, button):
        data = self.csr_read32(0, 4 + (button*4))
        if (data & 0x80000000): return "on"
        return "off"

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        for i in range(self.numbutton):
            util.info(f"Button {i:3}: {self.button_status(i):20}")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        data = self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [7,0,"BUTTON_COUNT"] ])
        count = data & 0xff
        for i in range(count):
            self.dump_reg(0, 0x0004+(i*4), "ButtonStatus%d" % i, [ [31,31,"STATE"], [30,30,"EVENT"], [15,0,"COUNT"] ])

class BlockIIC(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "IIC")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.offload_type = ((data >> 8) & 0xff)
        self.offload_enable = ((data) & 0x1)
        self.accelerator_disable = ((data) & 0x2)
        names = { 0 : 'None', 1: 'Xilinx', }
        offload = names[self.offload_type] if self.offload_type in names else 'Unknown'
        util.debug(f"Connect: {self} CsrId={self.csrid} AcceleratorDisable={self.accelerator_disable} "+
                   f"OffloadEnable={self.offload_enable} OffloadType={self.offload_type} ({offload})")
        self.pinreg = self.csr_read32(0, 4)
        self.manual_mode = True if ((self.pinreg & 0x1) or (self.pinreg & 0x10)) else False
        self.accelerator_mode = self.manual_mode and not self.accelerator_disable
        self.accelerator_type = None
        self.operation_byte_out = 0x0
        self.operation_byte_in = 0x1
        self.operation_byte_store = 0x2
        self.operation_byte_load = 0x3
        self.operation_setup = 0xf
        self.debug = False

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        util.info(f"Showing {self}: AcceleratorDisable={self.accelerator_disable} OffloadEnable={self.offload_enable} OffloadType={self.offload_type}")
        data = self.csr_read32(0, 4)
        scl_in = "HIGH (IDLE)" if data&0x08 else "LOW (ACTIVE)"
        sda_in = "HIGH (IDLE)" if data&0x80 else "LOW (ACTIVE)"
        if data&0x01:  scl_in += " (MANUAL MODE)"
        if data&0x10:  sda_in += " (MANUAL MODE)"
        util.info(f"{self}: SCL: {scl_in} SDA: {sda_in}")
        if ((data&0x01) != ((data&0x10)>>4)):
            util.warning(f"Inconsistent setting of MANUAL MODE on the pins")
        self.pinreg = data
        if self.offload_enable and self.offload_type == 0x1:
            data = self.csr_read32(1, 0x100) # control
            string = "Control:"
            if data&0x01: string += " ENABLE"
            if data&0x02: string += " TXFIFO_RESET"
            if data&0x04: string += " MSMS"
            if data&0x08: string += " TX"
            if data&0x10: string += " TXACK"
            if data&0x20: string += " RST"
            if data&0x40: string += " GCE"
            util.info(string)
            data = self.csr_read32(1, 0x104) # status
            string = "Status:"
            if data&0x01: string += " ABGC"
            if data&0x02: string += " AAS"
            if data&0x04: string += " BUS_BUSY"
            if data&0x08: string += " SLV_RW"
            if data&0x10: string += " TXFIFO_FULL"
            if data&0x20: string += " RXFIFO_FULL"
            if data&0x40: string += " RXFIFO_EMPTY"
            if data&0x80: string += " TXFIFO_EMPTY"
            util.info(string)

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [15, 8,"OFFLOAD_TYPE"],
                                           [ 1, 1,"ACCELERATOR_DISABLE"], [ 0, 0,"OFFLOAD_ENABLE"] ])
        self.dump_reg(0, 0x0004, "Control", [ [31,31,"OFFLOAD_INTERRUPT"], [30,30,"OFFLOAD_DEBUG"],
                                              [7,7,"SDA_IN"], [5,5,"SDA_TRISTATE"], [4,4,"SDA_MANUAL"],
                                              [3,3,"SCL_IN"], [1,1,"SCL_TRISTATE"], [0,0,"SCL_MANUAL"] ])
        if not self.accelerator_disable:
            self.dump_reg(0, 0x0008, "AcceleratorControl", [ [31,16,"ADDRESS"], [15,12,"OPERATION"],
                                                             [10,10,"ACK"], [9,9,"STOP"], [8,8,"START"],
                                                             [7,0,"DATA"]])
            self.dump_reg(0, 0x000c, "AcceleratorStatus", [ [31,31,"ERROR"], [28,28,"DONE"],
                                                            [16,16,"ACK"], [7,0,"DATA"]])
        if self.offload_enable and self.offload_type == 0x1:
            self.dump_reg(1, 0x001c, "GlobalInterruptEnable", [ [31,31,"ENABLE"] ])
            self.dump_reg(1, 0x0020, "InterruptStatus", [ [7,7,"TX_HALF_EMPTY"], [6,6,"NOT_ADDR_SLAVE"], [5,5,"ADDR_SLAVE"],
                                                             [4,4,"IIC_NOT_BUSY"], [3,3,"RX_FULL"], [2,2,"TX_EMPTY"],
                                                             [1,1,"TX_ERROR/SLAVE_COMPLETE"], [0,0,"ARB_LOST"] ])
            self.dump_reg(1, 0x0028, "InterruptEnable", [ [7,7,"TX_HALF_EMPTY"], [6,6,"NOT_ADDR_SLAVE"], [5,5,"ADDR_SLAVE"],
                                                             [4,4,"IIC_NOT_BUSY"], [3,3,"RX_FULL"], [2,2,"TX_EMPTY"],
                                                             [1,1,"TX_ERROR/SLAVE_COMPLETE"], [0,0,"ARB_LOST"] ])
            self.dump_reg(1, 0x0040, "SoftReset", [ [3,0,"KEY (0xA)"] ])
            self.dump_reg(1, 0x0100, "Control", [ [6,6,"GN_EN (GeneralCallEnable)"], [5,5,"RSTA (RepeatedStart)"],
                                                  [4,4,"TXAK (TransmitAckEnable)"], [3,3,"TX (TransmitMode)"],
                                                  [2,2,"MSMS (MasterSlaveModeSelect)"], [1,1,"TX_FIFO_RESET"], [0,0,"ENABLE"] ])
            self.dump_reg(1, 0x0104, "Status", [ [7,7,"TX_FIFO_EMPTY"], [6,6,"RX_FIFO_EMPTY"], [5,5,"RX_FIFO_FULL"],
                                                    [4,4,"TX_FIFO_FULL"], [3,3,"SRW (SlaveReadWrite)"], [2,2,"BB (BusBusy)"],
                                                    [1,1,"AAS (AddrAsSlave)"], [0,0,"ABGC (AddrAsGeneralCall)"] ])
            self.dump_reg(1, 0x0110, "SlaveAddress", [ [7,1,"ADDRESS"], [0,0,"RESERVED"] ])
            self.dump_reg(1, 0x0114, "TxOccupancy")
            self.dump_reg(1, 0x0118, "RxOccupancy")
            self.dump_reg(1, 0x011c, "TenBitAddress", [ [2,0,"ADDRESS_MSBS"] ])
            self.dump_reg(1, 0x0120, "RxIntrThreshold")
            self.dump_reg(1, 0x0124, "GPOutput", [ [0,0,"DEBUG_TO_CSR"] ])
            self.dump_reg(1, 0x0128, "TSUSTA (SetupRepeatedStart)")
            self.dump_reg(1, 0x012C, "TSUSTO (SetupRepeatedStop)")
            self.dump_reg(1, 0x0130, "THDSTA (HoldRepeatedStart)")
            self.dump_reg(1, 0x0134, "TSUDAT (SetupData)")
            self.dump_reg(1, 0x0138, "TBUF (BusFree)")
            self.dump_reg(1, 0x013C, "THIGH (ClockHigh)")
            self.dump_reg(1, 0x0140, "TLOW (ClockLow)")
            self.dump_reg(1, 0x0144, "THDDAT (HoldData)")

    def command_manual(self, parts=[], help_line=False):
        if help_line: return "Enables manual mode: enable, disable";
        command = -1 # report status
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^enable$', cmd)):
                command = True
            elif (eval_regex(r'^disable$', cmd)):
                command = False
            else:
                util.error(f"IIC didn't understand arg(s): {parts}", do_exit=False)
                raise HandledError
        if command != -1:
            self.iic_manual(command)
        util.info(f"{self}: Manual mode: {self.manual_mode}")

    def command_accelerator(self, parts=[], help_line=False):
        if help_line: return "Enables accelerator mode: enable, disable";
        command = -1 # report status
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^enable$', cmd)):
                command = True
            elif (eval_regex(r'^disable$', cmd)):
                command = False
            else:
                util.error(f"IIC didn't understand arg(s): {parts}", do_exit=False)
                raise HandledError
        if command != -1:
            self.accelerator_mode = command
            self.accelerator_type = None
            if command and not self.manual_mode:
                self.iic_manual(True)
        util.info(f"{self}: Accelerator mode: {self.accelerator_mode}")

    def command_debug(self, parts=[], help_line=False):
        if help_line: return "Enables debug mode: enable, disable";
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^enable$', cmd)):
                self.debug = True
            elif (eval_regex(r'^disable$', cmd)):
                self.debug = False
            elif (eval_regex(r'^show$', cmd)):
                self.iic_debug_show()
        util.info(f"{self}: Debug mode: {self.debug}")

    # the following are "low level" commands that are used in manual mode to manipulate the IIC pins

    def command_scl(self, parts=[], help_line=False):
        if help_line: return "Controls SCL pin: status, high, low";
        self.shared_scl_sda(parts, sda=False)

    def command_sda(self, parts=[], help_line=False):
        if help_line: return "Controls SDA pin: status, high, low";
        self.shared_scl_sda(parts, sda=True)

    def command_start(self, parts=[], help_line=False):
        if help_line: return "Sends IIC Start";
        if not self.manual_mode: self.warning(f"Use 'manual enable' to enter manual mode before manipulating pins")
        else:                    self.iic_start()

    def command_stop(self, parts=[], help_line=False):
        if help_line: return "Sends IIC Stop";
        if not self.manual_mode: self.warning(f"Use 'manual enable' to enter manual mode before manipulating pins")
        else:                    self.iic_stop()

    def command_byte_out(self, parts=[], help_line=False):
        if help_line: return "Sends IIC Byte";
        value = None
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^([\dxa-fA-F]+)$', cmd)):
                value = eval_number(m.group(1))
            else:
                util.error(f"IIC didn't understand arg(s): {parts}", do_exit=False)
                raise HandledError
        if value == None:
            util.warning("Need a value to send")
        elif not self.manual_mode:
            self.warning(f"Use 'manual enable' to enter manual mode before manipulating pins")
        else:
            ack = self.iic_byte_out(value)
            util.info(f"Received Ack: {ack}")

    def command_byte_in(self, parts=[], help_line=False):
        if help_line: return "Receives IIC Byte";
        send_ack = True
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^ack$', cmd)):
                send_ack = True
            elif (eval_regex(r'^n[o_]*ack$', cmd)):
                send_ack = False
            else:
                util.error(f"IIC didn't understand arg(s): {parts}", do_exit=False)
                raise HandledError
        if not self.manual_mode:
            self.warning(f"Use 'manual enable' to enter manual mode before manipulating pins")
        else:
            value = self.iic_byte_in(send_ack=send_ack)

    # Unfortunately, command_scan also only works in manual mode, until it learns to use iic_read

    def command_scan(self, parts=[], help_line=False):
        if help_line: return "Scans the IIC bus";
        util.info(f"{self}: Scanning IIC bus")
        util.info(f"     -0  -1  -2  -3  -4  -5  -6  -7  -8  -9  -A  -B  -C  -D  -E  -F")
        for addr in range(0x00, 128):
            if ((addr % 16) == 0): util.info(f"{addr:02x}  ", end='')
            self.iic_start()
            ack = self.iic_byte_out((addr*2)+1)
            if ack:
                status = " ** "
                self.iic_byte_in(send_ack=False)
            else:
                status = " -- "
            util.info(status, start='', end='')
            self.iic_stop()
            if ((addr % 16) == 15): util.info('', start='')

    def command_read7b(self, parts=[], help_line=False):
        if help_line: return "Reads a byte from a 7-bit address device: dev_addr, reg_addr";
        if len(parts)<2:
            util.error(f"Need two arguments: dev_addr, reg_addr", do_exit=False)
            raise HandledError
        if len(parts)>0: dev_addr = eval_number(parts.pop(0), check_int_min=0, check_int_max=0x7f)
        if len(parts)>0: reg_addr = eval_number(parts.pop(0), check_int_min=0, check_int_max=0xff)
        if len(parts)>0:
            util.error(f"IIC didn't understand arg(s): {parts}", do_exit=False)
            raise HandledError
        util.info(f"IIC reading from device {dev_addr:02x}, register {reg_addr:02x}")
        data = self.iic_read(dev_addr, reg_addr)
        util.info(f"IIC read: {data:02x} <- {dev_addr:02x}:{reg_addr:02x}")

    def command_write7b(self, parts=[], help_line=False):
        if help_line: return "Reads a byte from a 7-bit address device: dev_addr, reg_addr, data";
        if len(parts)<3:
            util.error(f"Need three arguments: dev_addr, reg_addr, data", do_exit=False)
            raise HandledError
        if len(parts)>0: dev_addr = eval_number(parts.pop(0), check_int_min=0, check_int_max=0x7f)
        if len(parts)>0: reg_addr = eval_number(parts.pop(0), check_int_min=0, check_int_max=0xff)
        if len(parts)>0: data = eval_number(parts.pop(0), check_int_min=0, check_int_max=0xff)
        if len(parts)>0:
            util.error(f"IIC didn't understand arg(s): {parts}", do_exit=False)
            raise HandledError
        util.info(f"IIC writing to device {dev_addr:02x}, register {reg_addr:02x}, data {data:02x}")
        self.iic_write(dev_addr, reg_addr, data)
        util.info(f"IIC read: {data:02x} -> {dev_addr:02x}:{reg_addr:02x}")

    def command_read7b_page(self, parts=[], help_line=False):
        if help_line: return "Reads 256-bytes from a 7-bit address device: dev_addr";
        if len(parts)<1:
            util.error(f"Need one argument: dev_addr", do_exit=False)
            raise HandledError
        if len(parts)>0: dev_addr = eval_number(parts.pop(0), check_int_min=0, check_int_max=0x7f)
        util.info(f"{self}: Scanning IIC device: {dev_addr}")
        util.info(f"      -0  -1  -2  -3  -4  -5  -6  -7  -8  -9  -A  -B  -C  -D  -E  -F")
        for reg_addr in range(0x00, 256):
            if ((reg_addr % 16) == 0): util.info(f"{reg_addr:02x}  ", end='')
            data = self.iic_read(dev_addr, reg_addr)
            util.info(f"  {data:02x}", start='', end='')
            if ((reg_addr % 16) == 15): util.info('', start='')

    def command_program_clock_chip(self, parts=[], help_line=False):
        if help_line: return "Programs the SI5394 Clock Generator from a regmap.txt file (the only arg)";
        if len(parts)<1:
            util.error(f"Need one argument: <file> (a regmap from the ClockBuilder Pro software)", do_exit=False)
            raise HandledError
        filename = parts.pop(0)
        if not os.path.exists(filename):
            util.error(f"Couldn't open file: {filename}", do_exit=False)
            raise HandledError
        # start on page 0
        current_page = 0
        self.iic_write(0x68, 0x1, current_page)
        with open(filename, 'r') as f:
            for line in f:
                m = re.match(r'\# Delay (\d+) msec', line)
                if m:
                    util.info(f"{self} Sleeping {m.group(1)} msec")
                    time.sleep(float(m.group(1))/1000.0)
                    continue
                m = re.match(r'\#', line)
                if m: continue
                m = re.match(r'Address,Data', line)
                if m: continue
                m = re.match(r'0x(\w\w)(\w\w)\,0x(\w\w)', line)
                if m:
                    page = int(m.group(1), 16)
                    addr = int(m.group(2), 16)
                    data = int(m.group(3), 16)
                    if page != current_page:
                        util.info(f"{self} Switching to page {page:02x}")
                        current_page = page
                        self.iic_write(0x68, 0x1, current_page)
                    util.info(f"{self} Writing 0x{page:02x}{addr:02x},0x{data:02x}")
                    self.iic_write(0x68, addr, data)
                time.sleep(0.002)

    def shared_scl_sda(self, parts=[], sda=False):
        level = None # report status
        check = False
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^(\d+)$', cmd)):
                number = eval_number(m.group(1))
                if number==0: level=False
                elif number==1: level=True
                else: self.warning(f"Cannot set pin to {number:x}")
            elif (eval_regex(r'^status$', cmd)):
                level = None
            elif (eval_regex(r'^high$', cmd)):
                level = True
            elif (eval_regex(r'^low$', cmd)):
                level = False
            elif (eval_regex(r'^check$', cmd)):
                check = True
            else:
                util.error(f"IIC didn't understand arg(s): {parts}", do_exit=False)
                raise HandledError
        if level == None:
            self.pinreg = self.csr_read32(0, 4)
            scl_in = "HIGH (IDLE)" if self.pinreg&0x08 else "LOW (ACTIVE)"
            sda_in = "HIGH (IDLE)" if self.pinreg&0x80 else "LOW (ACTIVE)"
            if self.pinreg&0x01:  scl_in += " (MANUAL MODE)"
            if self.pinreg&0x10:  sda_in += " (MANUAL MODE)"
            util.info(f"{self}: SCL: {scl_in} SDA: {sda_in}")
            return
        elif not self.manual_mode:
            self.warning(f"Use 'manual enable' to enter manual mode before manipulating pins")
        elif check:
            if sda: val = self.iic_sda_get()
            else:   val = self.iic_scl_get()
            if val == level:
                self.info(f"{'SDA' if sda else 'SCL'} was {val} as expected")
            else:
                self.warning(f"{'SDA' if sda else 'SCL'} was {val}, while {level} was expected")
        else:
            if sda: self.iic_sda_set(level)
            else:   self.iic_scl_set(level)
            self.shared_scl_sda() # just show status

    # iic_* layer is the "low level" API that the above commands call either atomically or in sequence

    def iic_manual(self, enabled=True):
        if (enabled != self.manual_mode):
            self.pinreg = self.csr_read32(0, 4)
            if enabled: self.pinreg = self.pinreg | 0x00000033 # start tristated
            else:       self.pinreg = self.pinreg & 0xffffffee | 0x00000022
            self.csr_write32(0,4,self.pinreg)
            self.manual_mode = enabled
            if not enabled:
                self.accelerator_mode = False # can't be in accelerator mode if not in manual mode
        else:
            # just confirm the settings
            want = 0x00000033 if self.manual_mode else 0x00000022
            self.pinreg = self.csr_read32(0, 4)
            if ((self.pinreg & 0x00000033) != want):
                util.warning(f"Saw pin control bits as {self.pinreg & 0x33:08x}, rewriting")
                self.csr_write32(0,4,self.pinreg & 0xffffffcc | want)
                self.pinreg = self.csr_read32(0, 4)
                if ((self.pinreg & 0x00000033) != want):
                    util.error(f"Still seeing {self.pinreg & 0x33:08x}, giving up")
        return self.manual_mode

    def iic_delay(self, us=10):
        #time.usleep(us)
        pass

    def iic_debug_show(self):
        pinreg = self.csr_read32(0, 4)
        if pinreg&0x08:  scl_in  = "HIGH"
        else:            scl_in  = "LOW "
        if pinreg&0x01:  scl_in += " (MANUAL)"
        else:            scl_in += "         "
        if pinreg&0x02:  scl_in += " (TRI)"
        else:            scl_in += "      "
        if pinreg&0x80:  sda_in  = "HIGH"
        else:            sda_in  = "LOW "
        if pinreg&0x10:  sda_in += " (MANUAL)"
        else:            sda_in += "         "
        if pinreg&0x20:  sda_in += " (TRI)"
        else:            sda_in += "      "
        print(f"DEBUG: {self}: SCL: {scl_in} SDA: {sda_in} RAW: {pinreg:08x} (scl:{(pinreg>>0)&0xf:04b},sda:{(pinreg>>4)&0xf:04b})")

    # low level pin handling (manual mode)

    def iic_scl_set(self, value=1, us_delay=0, optimize=False):
        if self.debug: print(f"          DEBUG IIC  iic_scl_set value={value} optimize={optimize}")
        if not optimize or (value != self.iic_scl_get(from_cache=True)):
            if value: self.pinreg = self.pinreg | 0x00000002 # set bit 1, tristate SCL
            else:     self.pinreg = self.pinreg & 0xfffffffd # clear bit 1, !tristate SCL
            self.csr_write32(0, 4, self.pinreg)
            if self.debug: print(f"          DEBUG IIC  iic_scl_set value={value} (csr written)")
        if us_delay: self.iic_delay(us_delay)
        if self.debug: self.iic_debug_show()

    def iic_sda_set(self, value=1, us_delay=0, optimize=False):
        if self.debug: print(f"          DEBUG IIC  iic_sda_set value={value} optimize={optimize}")
        if not optimize or (value != self.iic_sda_get(from_cache=True)):
            if value: self.pinreg = self.pinreg | 0x00000020 # set bit 1, tristate SDA
            else:     self.pinreg = self.pinreg & 0xffffffdf # clear bit 1, !tristate SDA
            self.csr_write32(0, 4, self.pinreg)
            if self.debug: print(f"          DEBUG IIC  iic_sda_set value={value} (csr written)")
        if us_delay: self.iic_delay(us_delay)
        if self.debug: self.iic_debug_show()

    def iic_scl_get(self, from_cache=False):
        if self.debug: print(f"          DEBUG IIC  iic_scl_get(from_cache={from_cache})")
        if self.debug: self.iic_debug_show()
        if not from_cache:
            self.pinreg = self.csr_read32(0, 4)
            if self.debug: print(f"          DEBUG IIC  iic_scl_get value={True if (self.pinreg & 0x8) else False} (csr read)")
        return True if (self.pinreg & 0x8) else False

    def iic_sda_get(self, from_cache=False):
        if self.debug: print(f"          DEBUG IIC  iic_sda_get(from_cache={from_cache})")
        if self.debug: self.iic_debug_show()
        if not from_cache:
            self.pinreg = self.csr_read32(0, 4)
            if self.debug: print(f"          DEBUG IIC  iic_sda_get value={True if (self.pinreg & 0x80) else False} (csr read)")
        return True if (self.pinreg & 0x80) else False

    def iic_start(self):
        if self.debug: print(f"          DEBUG IIC  iic_start()")
        if self.debug: self.iic_debug_show()
        # assume SCL=1 SDA=1
        self.iic_sda_set(0)
        self.iic_scl_set(0)
        # leave  SCL=0 SDA=0

    def iic_stop(self):
        if self.debug: print(f"          DEBUG IIC  iic_stop()")
        if self.debug: self.iic_debug_show()
        # assume SCL=0 SDA=x
        self.iic_sda_set(0)
        self.iic_scl_set(1)
        self.iic_sda_set(1)
        # leave  SCL=1 SDA=1

    def iic_byte_out(self, value):
        if self.debug: print(f"          DEBUG IIC  iic_byte_out(value={value})")
        # assume SCL=0 SDA=x
        for bit in range(8):
            if self.debug: print(f"          DEBUG IIC  iic_byte_out: sending bit {7-bit}: {1 if ((value << bit) & 0x80) else 0}")
            self.iic_sda_set(1 if ((value << bit) & 0x80) else 0)
            #self.iic_sda_set(1 if ((value << bit) & 0x80) else 0, optimize=True)
            self.iic_scl_set(1)
            self.iic_scl_set(0)
        if self.debug: print(f"          DEBUG IIC  iic_byte_out: releasing SDA to collect ACK")
        self.iic_sda_set(1)
        self.iic_scl_set(1)
        if self.debug: print(f"          DEBUG IIC  iic_byte_out: sampling ACK")
        got_ack = False if self.iic_sda_get() else True
        self.iic_scl_set(0)
        # leave  SCL=0 SDA=1
        return got_ack

    def iic_byte_in(self, send_ack=True):
        if self.debug: print(f"          DEBUG IIC  iic_byte_in(send_ack={send_ack})")
        # assume SCL=0 SDA=x
        self.iic_sda_set(1)
        value = 0
        for bit in range(8):
            value = value << 1
            self.iic_scl_set(1)
            while (not self.iic_scl_get()): self.iic_delay()
            value |= self.iic_sda_get()
            self.iic_scl_set(0)
        self.iic_sda_set(0 if send_ack else 1)
        self.iic_scl_set(1)
        self.iic_scl_set(0)
        self.iic_sda_set(1)
        # leave  SCL=0 SDA=1
        return value

    # high level reg read/write (offload or accelerator mode, still needs to code to call the above in manual mode which aint hard)

    def iic_accelerator_operation(self, dev_addr, reg_addr, operation, data=0, dev_type=0, repeat_start=1, start=0, stop=0, ack=0):
        accelerator_type = (dev_addr  + # device address, bits 6:0
                            (dev_type <<  8) + # device type, bits 9:8
                            (repeat_start << 12))  # repeat start, bit  12
        if accelerator_type != self.accelerator_type:
            accelerator_control = ((self.operation_setup << 12) +
                                   (accelerator_type << 16) )
            self.csr_write32(0, 0x0008, accelerator_control) # set accelerator type
            self.accelerator_type = accelerator_type
        accelerator_control = ((data << 0) + # data, bits 7:0
                                (start <<  8) + # start, bit 8
                                (stop <<  9) + # stop, bit 9
                                (ack << 10) + # ack, bit 10
                                (operation << 12) + # operation, bit 15:12
                                (reg_addr << 16)) # address, bits 31:16
        self.csr_write32(0, 0x0008, accelerator_control)
        status = 0
        iters = 0
        while (iters<1000) and (status & 0x10000000) == 0:
            status = self.csr_read32(0, 0x000c)
            iters += 1
        if iters >= 1000:
            util.error(f"{self} Polled 1000 times, never saw accelerator done")
            raise HandledError
        if status & 0x80000000:
            util.error(f"{self} Accelerator error: {status:08x}")
            raise HandledError
        return status

    def iic_read(self, dev_addr, reg_addr, tenBitMode=False):
        util.debug(f"IIC reading from device {dev_addr:02x}, register {reg_addr:02x}")
        if self.manual_mode and self.accelerator_mode:
            status = self.iic_accelerator_operation(dev_addr, reg_addr, self.operation_byte_load)
            val = status & 0xff
            util.debug(f"IIC read via accelerator: {val:02x} <- {dev_addr:02x}:{reg_addr:02x}")
        elif self.manual_mode:
            util.error(f"IIC don't know how to write in unaccelerated manual mode yet", do_exit=False)
            raise HandledError
        elif self.accelerator_mode:
            util.error(f"IIC is somehow in accelerator_mode without manual_mode???", do_exit=False)
            raise HandledError
        elif not self.offload_enable:
            util.error(f"IIC is somehow in accelerator_mode without manual_mode???", do_exit=False)
            raise HandledError
        elif self.offload_type == 0x1:
            self.csr_write32(1, 0x0100, 0x0001) # CONFIG: CR=1
            self.csr_write32(1, 0x0108, 0x0100 + (dev_addr<<1) + 0) # TXFIFO: START + DEVADDR + WRITING
            self.csr_write32(1, 0x0108, 0x0000 + reg_addr) # TXFIFO: REGADDR
            self.csr_write32(1, 0x0108, 0x0100 + (dev_addr<<1) + 1) # TXFIFO: REPEATED_START + DEVADDR + READING
            self.csr_write32(1, 0x0108, 0x0201) # TXFIFO: STOP + reading 1 byte
            iters = 0
            val = 0x40
            while (iters < 1000) and (val&0x40): # we wait for rx FIFO not empty
                val = self.csr_read32(1, 0x104) # read status register
                iters += 1
            if iters >= 1000:
                util.error(f"{self} polled 1000 times, never saw RX FIFO not empty")
                raise HandledError
            val = self.csr_read32(1, 0x10c)
            util.debug(f"IIC read via offload: {val:02x} <- {dev_addr:02x}:{reg_addr:02x}")
        else:
            util.error(f"IIC don't know how to read with a type {self.offload_type} offload", do_exit=False)
        return val

    def iic_write(self, dev_addr, reg_addr, data, tenBitMode=False):
        util.debug(f"IIC writing to device {dev_addr:02x}, register {reg_addr:02x}, data {data:02x}")
        if self.manual_mode and self.accelerator_mode:
            status = self.iic_accelerator_operation(dev_addr, reg_addr, self.operation_byte_store, data=data)
            util.debug(f"IIC write via accelerator: {data:02x} -> {dev_addr:02x}:{reg_addr:02x}")
        elif self.manual_mode:
            util.error(f"IIC don't know how to write in unaccelerated manual mode yet", do_exit=False)
            raise HandledError
        elif self.accelerator_mode:
            util.error(f"IIC is somehow in accelerator_mode without manual_mode???", do_exit=False)
            raise HandledError
        elif not self.offload_enable:
            util.error(f"IIC is somehow in accelerator_mode without manual_mode???", do_exit=False)
            raise HandledError
        elif self.offload_type == 0x1:
            self.csr_write32(1, 0x0100, 0x0001) # CONFIG: CR=1
            self.csr_write32(1, 0x0108, 0x0100 + (dev_addr<<1) + 0) # TXFIFO: START + DEVADDR + WRITING
            self.csr_write32(1, 0x0108, 0x0000 + reg_addr) # TXFIFO: REGADDR
            self.csr_write32(1, 0x0108, 0x0200 + data) # TXFIFO: STOP + DATA
            iters = 0
            val = 0
            while (iters < 1000) and not (val&0x80): # we wait for tx FIFO empty
                val = self.csr_read32(1, 0x104) # read status register
                iters += 1
                if iters >= 1000:
                    util.error(f"{self} polled 1000 times, never saw TX FIFO empty")
                    raise HandledError
            val = self.csr_read32(1, 0x10c)
            util.debug(f"IIC write via offload: {data:02x} -> {dev_addr:02x}:{reg_addr:02x}")
        else:
            util.error(f"IIC don't know how to write with a type {self.offload_type} offload", do_exit=False)
            raise HandledError

class BlockGPIO(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "GPIO")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.numgpio = ((data) & 0xff)
        util.debug(f"Connect: {self} CsrId={self.csrid} NumGpio={self.numgpio}")

    def gpio_status(self, gpio):
        data = self.csr_read32(0, 4 + (gpio*4))
        if (data & 0x10): s = "driving " + "HIGH" if (data & 0x01) else "LOW"
        else:             s = "not driving (tristate)"
        s += (", receiving " + ("HIGH" if (data & 0x100) else "LOW"))
        return s

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        for i in range(self.numgpio):
            util.info(f"GPIO {i:3}: {self.gpio_status(i):20}")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        data = self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [7,0,"GPIO_COUNT"] ])
        for i in range(self.numgpio):
            data = self.dump_reg(0, 0x0000, "Gpio%d" % i, [ [8,8,"IN"], [4,4,"ENABLE"], [0,0,"OUT"] ])

    def command_set(self, parts=[], help_line=False):
        if help_line: return "Set the state of the GPIO: [<gpio>] [high|low|tristate]";
        gpio = -1
        command = None # report status
        while (len(parts)):
            cmd = parts.pop(0)
            if (eval_regex(r'^(\d+)$', cmd)):
                led = eval_number(m.group(1))
            elif (eval_regex(r'^high$', cmd)):
                command = 1
            elif (eval_regex(r'^low$', cmd)):
                command = 0
            elif (eval_regex(r'^tri(?:state)$', cmd)):
                command = 2
            else:
                util.error(f"LED didn't understand arg(s): {parts}", do_exit=False)
                raise HandledError
        if command == None: # we reporting status
            util.warning(f"Need a command")
            return
        if gpio == -1: # on all GPIO
            if   command == 0: csrval = 0x10
            elif command == 1: csrval = 0x11
            else             : csrval = 0x00
            for i in range(self.numgpio): self.csr_write32(0, 4 + (   i*4), csrval)
        else:                             self.csr_write32(0, 4 + (gpio*4), csrval)

class BlockProtect(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "Protect")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.skeleton_key = ((data>>0) & 0x1)
        self.timed_license = ((data>>1) & 0x1)
        self.paranoia = ((data>>2) & 0x1)
        util.debug(f"Connect: {self} CsrId={self.csrid} SkeletonKey={self.skeleton_key},TimedLicense={self.timed_license},Paranoia={self.paranoia}")

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        util.info(f"Showing {self}: Features: SkeletonKey={self.skeleton_key},TimedLicense={self.timed_license},Paranoia={self.paranoia}")
        data = self.csr_read32(0, 4)
        util.info(f"State: "+
                  ("Locked " if (((data>>30)&3)==0) else "") +
                  ("Unlocked " if ((data>>31)&1) else "") +
                  ("Timed Unlock " if ((data>>30)&1) else "") +
                  ("Decryption Done " if ((data>>29)&1) else "") +
                  ("Decryption Go " if ((data>>0)&1) else "") +
                  ("Decryption Idle " if not ((data>>0)&1) else ""))
        fpga_serial = self.csr_read32(0, 0x10)
        bitstream_id= self.csr_read32(0, 0x14)
        util.info(f"FPGA Serial #: {fpga_serial:08x}, Bitstream ID: {bitstream_id:08x}")
        util.info(f"Encrypted License: {self.csr_read32(0, 0x08):08x} {self.csr_read32(0, 0x0c):08x}")
        util.info(f"Decrypted License: {self.csr_read32(0, 0x18):08x} {self.csr_read32(0, 0x1c):08x}")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        data = self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [2,2,"ENABLE_PARANOIA"], [1,1,"ENABLE_TIMED_LICENSE"], [0,0,"ENABLE_SKELETON_KEY"] ])
        self.dump_reg(0, 0x0004, "Control", [ [31,31,"UNLOCKED"], [30,30,"TIMED_UNLOCK"], [29,29,"DECRYPT_DONE"], [0,0,"DECRYPT_GO"] ])
        self.dump_reg(0, 0x0008, "License0")
        self.dump_reg(0, 0x000c, "License1")
        self.dump_reg(0, 0x0010, "FpgaSerial")
        self.dump_reg(0, 0x0014, "BitstreamID")
        self.dump_reg(0, 0x0018, "Plaintext0")
        self.dump_reg(0, 0x001c, "Plaintext1")

    def command_unlock(self, parts=[], help_line=False):
        if help_line: return "Unlocks the protected device, requires a license, given as two arguments (8-digit hex each)";
        if len(parts) != 2:
            util.error(f"Need two arguments for 'unlock'", do_exit=False)
            raise HandledError
        lic = [ eval_number(parts.pop(0), ishex=True),
                eval_number(parts.pop(0), ishex=True) ]
        self.csr_write32(0, 0x08, lic[0])
        self.csr_write32(0, 0x0c, lic[1])
        self.csr_write32(0, 0x04, 0x00000001)
        data = self.csr_read32(0, 0x04)
        if ((data>>31)&1):   util.info("License valid, FPGA unlocked")
        elif ((data>>30)&1): util.info("Demo license valid, FPGA enabled for licensed period")
        elif ((data>>29)&1): util.warning("FAIL -- key was loaded but not accepted")
        elif ((data>>0)&1):  util.warning("FAIL -- set the 'go' bit but decryption never finished?")
        else:                util.warning("FAIL -- unable to set the 'go' bit?")

class BlockDummy(Block):
    def __init__(self, channel, blockid):
        Block.__init__(self, channel, blockid, "Dummy")

    def connect(self):
        Block.connect(self)
        data = self.csr_read32(0, 0)
        self.csrid = ((data >> 16) & 0xffff)
        self.datapath_count = ((data>>0) & 0xff)
        util.debug(f"Connect: {self} CsrId={self.csrid} DatapathCount={self.datapath_count}")

    def command_show(self, parts=[], help_line=False):
        if help_line: return "Shows high level status of the block in human readable form";
        util.info(f"Showing {self}: Features: DatapathCount={self.datapath_count}")
        data = self.csr_read32(0, 0x04)
        util.info(f"State: "+
                  ("Done " if ((data>>31)&1) else "") +
                  ("Go " if ((data>>0)&1) else ""))
        data = self.csr_read32(0, 0x08)
        datapath_width = ((data >> 16) & 0xffff)
        datapath_pipe_stages = ((data >> 0) & 0xffff)
        data = self.csr_read32(0, 0x0c)
        datapath_logic_levels = ((data >> 24) & 0xff)
        datapath_lut_inputs = ((data >> 20) & 0xf)
        util.info(f"Logic Datapath Width: {datapath_width}-bit, {datapath_pipe_stages} pipe stages, each "+
                  f"stage is {datapath_logic_levels} logic levels of {datapath_lut_inputs}-input LUTS")

    def command_dump(self, parts=[], help_line=False):
        if help_line: return "Dumps detailed config/status info of the block in human readable form";
        self.info(f"Dumping {self}:")
        data = self.dump_reg(0, 0x0000, "OcID", [ [31,16,"ID"], [7,0,"DATAPATH_COUNT"] ])
        self.dump_reg(0, 0x0004, "Control", [ [31,31,"DONE"], [0,0,"GO"] ])
        self.dump_reg(0, 0x0008, "Param0", [ [31,16,"DATAPATH_WIDTH"], [15,0,"DATAPATH_PIPE_STAGES"] ])
        self.dump_reg(0, 0x000c, "Param1", [ [31,24,"DATAPATH_LOGIC_LEVELS"], [23,20,"DATAPATH_LUT_INPUTS"] ])
        self.dump_reg(0, 0x0010, "CurrentChunk")
        self.dump_reg(0, 0x0014, "LastChunk")
        for i in range(self.datapath_count):
            self.dump_reg(0, 0x0018+(i*4), "Result{i}")

    def command_run(self, parts=[], help_line=False):
        if help_line: return "Runs and returns signatures.  Takes one argument, the last chunk (i.e.0 means run one chunk)";
        if len(parts) != 1:
            util.error(f"Need one argument for 'run'", do_exit=False)
            raise HandledError
        num_chunks_m1 = eval_number(parts.pop(0))
        self.csr_write32(0, 0x14, num_chunks_m1)
        self.csr_write32(0, 0x04, 0)
        self.csr_write32(0, 0x04, 1)
        start_time = time.time()
        data = 0
        while not (data & 0x80000000):
            data = self.csr_read32(0, 0x04)
        stop_time = time.time()
        for i in range(self.datapath_count):
            data = self.csr_read32(0, 0x0018+(i*4))
            util.info(f"Result from DP[{i}]: {data:08x}")
        self.csr_write32(0, 0x04, 0)
        elapsed_time = (stop_time - start_time)
        mhz = ((num_chunks_m1) * 65536.0) / (elapsed_time * 1000000.0)
        util.info(f"Ran {num_chunks_m1+1} chunks in {elapsed_time:.3f} seconds, estimate clock to be {mhz:.3f} Mhz")

    def command_check(self, parts=[], help_line=False):
        if help_line: return "Runs and checks signatures.  Requires the length and the expected result"
        if len(parts) != (1+self.datapath_count):
            util.error(f"Need {1+self.datapath_count} arguments for 'check': <length-1> and <result> (x DatapathCount) ", do_exit=False)
            raise HandledError
        num_chunks_m1 = eval_number(parts.pop(0))
        expect = []
        for i in range(self.datapath_count):
            expect.append(eval_number(parts.pop(0)))
        self.csr_write32(0, 0x14, num_chunks_m1)
        self.csr_write32(0, 0x04, 0)
        self.csr_write32(0, 0x04, 1)
        start_time = time.time()
        data = 0
        while not (data & 0x80000000):
            data = self.csr_read32(0, 0x04)
        stop_time = time.time()
        for i in range(self.datapath_count):
            data = self.csr_read32(0, 0x0018+(i*4))
            if data == expect[i]: util.info(f"Result from DP[{i}]: {data:08x} (OK)")
            else : util.warning(f"Result from DP[{i}]: {data:08x} (MISMATCH, expected {expect[i]:08x})")
        self.csr_write32(0, 0x04, 0)
        elapsed_time = (stop_time - start_time)
        mhz = ((num_chunks_m1) * 65536.0) / (elapsed_time * 1000000.0)
        util.info(f"Ran {num_chunks_m1+1} chunks in {elapsed_time:.3f} seconds, estimate clock to be {mhz:.3f} Mhz")

# **** Register all the block classes into a table that can be queried by GUI

block_table[ 0] = { 'name' : 'Unknown'    , 'csrid' :  0, 'handler' : Block           }
block_table[ 1] = { 'name' : 'Pll'        , 'csrid' :  1, 'handler' : BlockPll        }
block_table[ 2] = { 'name' : 'ChipMon'    , 'csrid' :  2, 'handler' : BlockChipMon    }
block_table[ 3] = { 'name' : 'Protect'    , 'csrid' :  3, 'handler' : BlockProtect    }
block_table[ 4] = { 'name' : 'Dummy'      , 'csrid' :  4, 'handler' : BlockDummy      }
block_table[ 5] = { 'name' : 'IIC'        , 'csrid' :  5, 'handler' : BlockIIC        }
block_table[ 6] = { 'name' : 'LED'        , 'csrid' :  6, 'handler' : BlockLED        }
block_table[ 7] = { 'name' : 'GPIO'       , 'csrid' :  7, 'handler' : BlockGPIO       }
block_table[ 8] = { 'name' : 'Fan'        , 'csrid' :  8, 'handler' : Block           }
block_table[ 9] = { 'name' : 'HBM'        , 'csrid' :  9, 'handler' : Block           }
block_table[10] = { 'name' : 'CMAC'       , 'csrid' : 10, 'handler' : Block           }
block_table[11] = { 'name' : 'PCIe'       , 'csrid' : 11, 'handler' : Block           }
block_table[12] = { 'name' : 'Eth1G'      , 'csrid' : 12, 'handler' : Block           }
block_table[13] = { 'name' : 'Eth10G'     , 'csrid' : 13, 'handler' : Block           }
block_table[14] = { 'name' : 'RGB'        , 'csrid' : 14, 'handler' : BlockRGB        }
block_table[15] = { 'name' : 'Toggle'     , 'csrid' : 15, 'handler' : BlockToggle     }
block_table[16] = { 'name' : 'Button'     , 'csrid' : 16, 'handler' : BlockButton     }

# **************************************************************
# *** Channels
# Connect to a particular chip.  They contain standard methods
# (csr_read, info, timers, scan, etc).

class Channel:
    global block_table
    def __init__(self, name):
        self.name = name
        self.chip_info_bytes = []
        self.chip_info_strings = None
        self.chip_timers = None
        self.scanned = False
        # need to read this from the RTL file
        self.block_handler = {} # <block> : <Block class>, so we can have stateful objects managing each block
        self.csrid_table = {} # <csrid> : block name as a pretty string, so we can print "Block[0] is an LED"
        self.block_dict = {} # lowercase name : block table entry, for when user types "led dump"
        for i,b in block_table.items():
            self.csrid_table[i] = b['name'] # create a table for convenient printing of name
            self.block_dict[b['name'].lower()] = b # and a dict to lookup block info by lowercase (CLI) name

    def close(self):
        util.debug(f"Closed {self.name}")
        self.name = self.name + " (closed)"
        self.chip_info_bytes = []
        self.chip_info_strings = None
        self.chip_timers = None

    def show_chip_info(self):
        self.chip_info_load()
        util.info(f"Version             : {self.chip_info_strings['version']:8}")
        util.info(f"Builder ID          : {self.chip_info_strings['builder_id']:8}")
        util.info(f"Bitstream ID        : {self.chip_info_strings['bitstream_id']:8}")
        util.info(f"Build Date          : {self.chip_info_strings['build_date']:8}")
        util.info(f"Build Time          : {self.chip_info_strings['build_time']:8}")
        util.info(f"Vendor Name         : {self.chip_info_strings['vendor_name']:8}")
        util.info(f"Library Name        : {self.chip_info_strings['library_name']:8}")
        util.info(f"Board Name          : {self.chip_info_strings['board_name']:8}")
        util.info(f"Block Top Count     : {self.chip_info_strings['block_top_count']:8}")
        util.info(f"Block User Count    : {self.chip_info_strings['block_user_count']:8}")
        util.info(f"Block Protocol      : {self.chip_info_strings['block_protocol']:8}")
        util.info(f"User CSR Interfaces : {self.chip_info_strings['user_csr_interfaces']:8}")
        util.info(f"User Memory Sources : {self.chip_info_strings['user_memory_sources']:8}")
        util.info(f"User Memory Sinks   : {self.chip_info_strings['user_memory_sinks']:8}")
        util.info(f"User Stream Sources : {self.chip_info_strings['user_stream_sources']:8}")
        util.info(f"User Stream Sinks   : {self.chip_info_strings['user_stream_sinks']:8}")
        util.info(f"User App Name       : {self.chip_info_strings['userspace']}")
        util.info(f"UUID                : {self.chip_info_strings['uuid']}")

    def show_chip_timers(self):
        util.info(f"Taking 2 seconds to measure clockTop")
        self.chip_timer_load()
        start_seconds = time.time()
        start_cycles = self.chip_timers['cycles_since_reset']
        time.sleep(2)
        self.chip_timer_load()
        stop_seconds = time.time()
        stop_cycles = self.chip_timers['cycles_since_reset']
        util.info(f"Time since reload/power : {self.chip_timers['seconds_since_reload']:10} seconds")
        util.info(f"Time since reset        : {self.chip_timers['seconds_since_reset']:10} seconds")
        util.info(f"Cycles since reset      : {self.chip_timers['cycles_since_reset']:10} cycles")
        util.info(f"Cycles under reset      : {self.chip_timers['cycles_under_reset']:10} cycles")
        cycles = (stop_cycles - start_cycles)
        if cycles<0: cycles += (1 << 32)
        seconds = (stop_seconds - start_seconds)
        mhz = (cycles / (seconds * 1000000.0))
        util.info(f"clockTop frequency      : {cycles:10} cycles in {seconds:.2f}s ({mhz:6.2f} MHz)")

    def create_block_handler(self, block, handler):
        if block in self.block_handler:
            util.warning(f"Creating a block handler for block {block} but one exists, removing it")
            self.block_handler[block].disconnect()
        self.block_handler[block] = handler(self, block)
        self.block_handler[block].connect()

    def scan_chip(self, create_handlers=True, force_new_handlers=False):
        self.chip_info_load()
        for b in range(0, int(self.chip_info_strings['block_top_count'],0)):
            temp32 = self.csr_read32(b, 0, 0)
            csrid = ((temp32 >> 16) & 0xffff)
            params = (temp32 & 0xffff)
            name = lookup_table_string(self.csrid_table, csrid)
            util.info(f"Block {name:12} [{b:04x}] CsrId={csrid:04x} Params={params:04x}")
            if create_handlers and (force_new_handlers or not b in self.block_handler):
                if name.lower() in self.block_dict: handler = self.block_dict[name.lower()]['handler']
                else: handler = self.block_dict['unknown']['handler']
                self.create_block_handler(b, handler)
        self.scanned = True

    def performance_check(self, actions_per_iter=100):
        if not self.scanned:
            util.error(f"Please scan chip before trying to do performance check", do_exit=False)
            return
        util.info(f"Checking 32-bit CSR write performance")
        start_time = time.time()
        now_time = start_time
        temp32 = 0
        actions = 0
        while (now_time < (start_time + 2)):
            for _ in range(actions_per_iter):
                temp32 = self.csr_write32(0, 0, 0, 0)
            actions += actions_per_iter
            now_time = time.time()
        elapsed = now_time-start_time
        util.info(f"- {actions} in {elapsed:8.3f}s ({actions/elapsed:8.1f} op/s, {(actions*4)/(elapsed*1000000):8.1f} MB/s")
        util.info(f"Checking 32-bit CSR read performance")
        start_time = time.time()
        now_time = start_time
        temp32 = 0
        actions = 0
        while (now_time < (start_time + 2)):
            for _ in range(actions_per_iter):
                temp32 = self.csr_read32(0, 0, 0)
            actions += actions_per_iter
            now_time = time.time()
        elapsed = now_time-start_time
        util.info(f"- {actions} in {elapsed:8.3f}s ({actions/elapsed:8.1f} op/s, {(actions*4)/(elapsed*1000000):8.1f} MB/s")

# PciChannel is a subclass of channel that knows how to talk to the chip over PCIe
class PCIeChannel(Channel):
    def __init__(self, slot):
        Channel.__init__(self, f"PCIe:{slot}")
        self.slot = slot
        self.bar = 0
        self.pcie = pcie.PCIe(slot=self.slot, bar=self.bar)
        self.pcie.mmap()
        self.data_port = self.pcie.size - 256 # ffff00, blocking on data transfer
        self.debug_port = self.pcie.size - 128 # ffff80, non-blocking, reads all internal state with no side effects
        self.access_port = self.pcie.size - 64 # ffffc0, non-blocking, as above but will pop the read data from FIFO if present
        self.max_polls = 0
        self.bytes_rx = 0
        self.bytes_tx = 0
        self.csr_reads = 0
        self.csr_writes = 0
        util.info(f"Opened PCIe slot {self.slot} BAR{self.bar}, data/debug/access_ports at {self.data_port:04x}/"+
                  f"{self.debug_port:04x}/{self.access_port:04x}")

    def close(self):
        self.pcie.close()
        Channel.close()

    def flush(self):
        util.debug(f"Channel: Flushing PCIe...", level=1)
        s = "."
        flushed = 0
        # TODO: I'm not loving how ineffient it is.  Ideally we could read non-blocking, and if we read something,
        # know the state of whether there's something ELSE in there too.
        c = self.pcie.read32(self.debug_port)
        util.debug(f"PCIe debug  port read returned: {c:08x}", level=1)
        while (c & 0x100):
            c = self.pcie.read32(self.access_port)
            util.debug(f"PCIe access port read returned: {c:08x}", level=1)
            flushed += 1
            if flushed > 200:
                util.error(f"Got >200 bytes while trying to flush PCIe channel, this isn't an OC device")
            c = self.pcie.read32(self.debug_port)
            util.debug(f"PCIe debug  port read returned: {c:08x}", level=1)
        util.debug(f"Channel: Flush done ({flushed} bytes)", level=2)

    def reset(self):
        util.debug(f"Channel: Reset, sending 64 '~' chars", level=1)
        for i in range(64):
            self.pcie.write32(self.data_port, 0x7e)
        time.sleep(0.01)
        self.flush() # read anything else that comes in after reset, like prompt, syntax error because partial byte
        util.info(f"Channel: Reset complete")

    def serial_write(self, tx_bytes, expect_prompt=False):
        p = " (prompt)" if expect_prompt else ""
        util.debug(f"Channel: writing {tx_bytes} ({len(tx_bytes)} bytes){p}", level=5)
        for b in tx_bytes:
            self.pcie.write32(self.data_port, b)
        if expect_prompt:
            self.serial_read_prompt()
        self.bytes_tx += len(tx_bytes)

    def serial_read(self, length=1, poll_interval = 0.01, max_wait = 0.1):
        util.debug(f"Channel: Reading {length} bytes...", level=5)
        rx_bytes = bytes()
        for i in range(length):
            waited = 0
            polls = 0
            while True:
                polls += 1
                c = self.pcie.read32(self.data_port)
                util.debug(f"Read returned {c:08x}")
                if (c & 0x100):
                    d = bytes([c & 0xff])
                    util.debug(f"appending {d}")
                    rx_bytes += d
                    break
                elif (c & 0x8000):
                    util.error(f"Received timeout from AXIL-BC bridge, no BC RX data in FIFO")
                    i = length
                    break
                else:
                    time.sleep(poll_interval)
                    waited += poll_interval
                    if waited >= max_wait:
                        util.error(f"PCIe polled {polls} times, and took longer than {max_wait}s timeout")
                        util.info(f"PCIe stats since init:")
                        util.info(f"  BYTES_RX:  {self.bytes_rx:10} BYTES_TX:   {self.bytes_tx:10}")
                        util.info(f"  CSR_READS: {self.csr_reads:10} CSR_WRITES: {self.csr_writes:10}")
                        i = length
                        break
            polls += 1
        util.debug(f"Channel: Read {rx_bytes} ({len(rx_bytes)} bytes, {polls} polls)", level=5)
        if polls > self.max_polls: self.max_polls = polls
        self.bytes_rx += len(rx_bytes)
        return rx_bytes

    def serial_read_prompt(self):
        util.debug(f"Channel: Expecting prompt...", level=4)
        s = self.serial_read(5)
        if s != b'\r\nOC>':
            util.error(f"Channel: Ping didn't receive expected prompt, got: {s} ({len(s)} bytes)", do_exit=False)
            raise HandledError

    def serial_read_error(self):
        util.debug(f"Channel: Expecting error...", level=4)
        s = self.serial_read(12)
        if s != b'\r\nERROR\r\nOC>':
            util.error(f"Channel: Ping didn't receive expected error, got: {s} ({len(s)} bytes)", do_exit=False)
            raise HandledError

    def ping(self):
        util.debug(f"Channel: Ping, first flushing anything in channel", level=2)
        self.flush()
        util.debug(f"Channel: Pinging serial, sending \\n for prompt", level=2)
        self.serial_write(b'\n')
        self.serial_read_prompt()
        util.debug(f"Channel: Pinging serial, sending ^ for error", level=2)
        self.serial_write(b'^\n')
        self.serial_read_error()
        util.info(f"Channel: Ping OK")

    def serial_read_int32(self):
        util.debug(f"Channel: Readinf int32...", level=2)
        b = self.serial_read(4)
        i32 = ((b[0] << 24) | (b[1] << 16) | (b[2] << 8) | (b[3]))
        util.debug(f"Channel: Read int32: {i32}")
        return i32

    def chip_info_load(self):
        if self.chip_info_strings: return
        util.info(f"Loading chip info")
        self.serial_write(b'I\n')
        b = self.serial_read(64)
        if len(b) != 64:
            util.error(f"ChipInfoLoad: only got {len(b)} bytes back from I command, wanted 64", do_exit=False)
            raise HandledError
        self.chip_info_bytes = b
        self.chip_info_strings = {
            'version'             : ("0x%02x" % (b[0])),
            'builder_id'          : ("0x%06x" % ((b[1] << 16) | (b[2] << 8) | (b[3]))),
            'bitstream_id'        : ("0x%08x" % ((b[4] << 24) | (b[5] << 16) | (b[6] << 8) | (b[7]))),
            'build_date'          : ("%04x/%02x/%02x" % ((b[8] << 8) | (b[9]), (b[10]), (b[11]) )),
            'build_time'          : ("%02x:%02x" % ((b[12]), (b[13]))),
            'vendor_name'         : lookup_table_string('OC_VENDOR', ((b[14] << 8) | (b[15]))),
            'library_name'        : lookup_table_string('OC_LIBRARY', ((b[16] << 8) | (b[17]))),
            'board_name'          : lookup_table_string('OC_BOARD', ((b[18] << 8) | (b[19]))),
            'block_top_count'     : ("0x%04x" % ((b[20] << 8) | (b[21]))),
            'block_user_count'    : ("0x%04x" % ((b[22] << 8) | (b[23]))),
            'block_protocol'      : ("0x%02x" % (b[24])),
            'user_csr_interfaces' : ("0x%02x" % (b[25])),
            'user_memory_sources' : ("0x%02x" % (b[26])),
            'user_memory_sinks'   : ("0x%02x" % (b[27])),
            'user_stream_sources' : ("0x%02x" % (b[28])),
            'user_stream_sinks'   : ("0x%02x" % (b[29])),
            'userspace'           : "",
            'uuid'                : "",
        }
        for i in range (0, 16): self.chip_info_strings['userspace'] += chr(b[32+i])
        for i in range (0, 16): self.chip_info_strings['uuid']      += ("%02x" % (b[48+i]))
        self.serial_write(b'', expect_prompt=True)

    def chip_timer_load(self):
        util.info(f"Loading chip timers")
        self.serial_write(b'T\n')
        self.chip_timers = {
            'seconds_since_reload' : self.serial_read_int32(),
            'seconds_since_reset'  : self.serial_read_int32(),
            'cycles_since_reset'   : self.serial_read_int32(),
            'cycles_under_reset'   : self.serial_read_int32(),
        }
        self.serial_write(b'', expect_prompt=True)
        util.info(f"Maximum polls done when reading byte from byte channel keyhole: {self.max_polls}")

    def bc_send(self, message, end=b'\n'):
        if len(message)<2 or len(message)>100:
            util.error(f"Cannot send BC messages >100B in length, this was: {message} ({len(message)} bytes)", do_exit=False)
            raise HandledError
        self.serial_write(b'B'+ (len(message)+1).to_bytes(1, 'big') + message + end)

    def bc_receive(self):
        b = self.serial_read(1)
        if len(b) == 0:
            util.error("Timeout waiting for response, you probably need to 'reset'", do_exit=False)
            raise HandledError
        length = int(b[0])
        message = self.serial_read(length-1)
        return message

    def bc_send_receive(self, message, end=b'\n'):
        self.bc_send(message,end=b'') # send message, no \n to leave response channel open
        response = self.bc_receive()  # collect message response, channel will have some timeout
        self.serial_write(end)        # close the BC channel
        return response

    def csr_read32(self, block, space, address, msgid=0, verbose=False):
        util.debug(f"Channel: csr_read32(block={block},space={space},address={address:08x})")
        request = (block.to_bytes(2, 'big') +
                   b'\x01' + # read command
                   ((space<<4)+msgid).to_bytes(1, 'big') +
                   address.to_bytes(4, 'big') +
                   int(0).to_bytes(4, 'big'))
        response = self.bc_send_receive(request)
        self.serial_read_prompt()
        if len(response) != 5:
            util.error(f"Expected 5-byte response to CSR BC message, got {response} ({len(response)} bytes)", do_exit=False)
            raise HandledError
        if response[0] != 1:
            util.error(f"Expected ready=1 status byte (0x01), got {response[0]:02x})", do_exit=False)
            raise HandledError
        data = int.from_bytes(response[1:5], 'big')
        util.debug(f"  {data:08x} <- [{block:04x}][{space:01x}][{address:08x}]")
        self.csr_reads += 1
        return data

    def csr_write32(self, block, space, address, data, msgid=0, verbose=False):
        util.debug(f"Channel: csr_write32(block={block},space={space},address={address:08x}, data={data:08x})")
        request = (block.to_bytes(2, 'big') +
                   b'\x02' + # write command
                   ((space<<4)+msgid).to_bytes(1, 'big') +
                   address.to_bytes(4, 'big') +
                   data.to_bytes(4, 'big'))
        response = self.bc_send_receive(request)
        self.serial_read_prompt()
        if len(response) != 5:
            util.error(f"Expected 5-byte response to CSR BC message, got {response} ({len(response)} bytes)", do_exit=False)
            raise HandledError
        if response[0] != 1:
            util.error(f"Expected ready=1 status byte (0x01), got {response[0]:02x})", do_exit=False)
            raise HandledError
        util.debug(f"  {data:08x} -> [{block:04x}][{space:01x}][{address:08x}]")
        self.csr_writes += 1

# SerialChannel is a subclass of channel that knows how to talk to the chip over serial methods (TCP Socket, or PySerial)
class SerialChannel(Channel):
    def __init__(self, port, baud):
        Channel.__init__(self, f"Serial:{port}")
        # def serial_open(port, baud):
        self.port = port
        self.baud = baud
        if port.startswith("tcp:"):
            util.debug(f"Opening FakeSerial {port}...")
            self.ser = FakeSerial(port, timeout=0.5)
            util.info(f"Opened FakeSerial {port}")
        else:
            util.debug(f"Opening {port} @ {baud}bps...")
            self.ser = serial.Serial(port=port, baudrate=baud, timeout=0.5)
            util.info(f"Opened {port} @ {baud}bps")
            util.info(f"Dumping object: {self.ser}")

    def close(self):
        self.ser.close()
        Channel.close()

    def flush(self):
        util.debug(f"Channel: Flushing serial...", level=1)
        s = "."
        flushed = 0
        while len(s):
            s = self.ser.read(100)
            flushed += len(s)
            if flushed > 200:
                util.error(f"Got >200 bytes while trying to flush serial channel, this isn't an OC device")
        util.debug(f"Channel: Flush done ({flushed} bytes)", level=2)

    def reset(self):
        util.debug(f"Channel: Reset, sending 64 '~' chars", level=1)
        for i in range(64):
            self.serial_write(b'~')
        time.sleep(0.01)
        s = self.serial_read(32) # read anything else that comes in after reset, like prompt, syntax error because partial byte
        util.info(f"Channel: Reset complete")

    def serial_write(self, tx_bytes, expect_prompt=False):
        p = " (prompt)" if expect_prompt else ""
        util.debug(f"Channel: writing {tx_bytes} ({len(tx_bytes)} bytes){p}", level=5)
        self.ser.write(tx_bytes)
        if expect_prompt:
            self.serial_read_prompt()

    def serial_read(self, length=1):
        util.debug(f"Channel: Reading {length} bytes...", level=5)
        rx_bytes = self.ser.read(length)
        util.debug(f"Channel: Read {rx_bytes} ({len(rx_bytes)} bytes)", level=5)
        return rx_bytes

    def serial_read_prompt(self):
        util.debug(f"Channel: Expecting prompt...", level=4)
        s = self.serial_read(5)
        if s != b'\r\nOC>':
            util.error(f"Channel: Ping didn't receive expected prompt, got: {s} ({len(s)} bytes)", do_exit=False)
            raise HandledError

    def serial_read_error(self):
        util.debug(f"Channel: Expecting error...", level=4)
        s = self.serial_read(12)
        if s != b'\r\nERROR\r\nOC>':
            util.error(f"Channel: Ping didn't receive expected error, got: {s} ({len(s)} bytes)", do_exit=False)
            raise HandledError

    def ping(self):
        util.debug(f"Channel: Ping, first flushing anything in channel", level=2)
        self.flush()
        util.debug(f"Channel: Pinging serial, sending \\n for prompt", level=2)
        self.serial_write(b'\n')
        self.serial_read_prompt()
        util.debug(f"Channel: Pinging serial, sending ^ for error", level=2)
        self.serial_write(b'^\n')
        self.serial_read_error()
        util.info(f"Channel: Ping OK")

    def serial_read_int32(self):
        util.debug(f"Channel: Readinf int32...", level=2)
        b = self.serial_read(4)
        i32 = ((b[0] << 24) | (b[1] << 16) | (b[2] << 8) | (b[3]))
        util.debug(f"Channel: Read int32: {i32}")
        return i32

    def chip_info_load(self):
        if self.chip_info_strings: return
        util.info(f"Loading chip info")
        self.serial_write(b'I\n')
        b = self.serial_read(64)
        if len(b) != 64:
            util.error(f"ChipInfoLoad: only got {len(b)} bytes back from I command, wanted 64", do_exit=False)
            raise HandledError
        self.chip_info_bytes = b
        self.chip_info_strings = {
            'version'             : ("0x%02x" % (b[0])),
            'builder_id'          : ("0x%06x" % ((b[1] << 16) | (b[2] << 8) | (b[3]))),
            'bitstream_id'        : ("0x%08x" % ((b[4] << 24) | (b[5] << 16) | (b[6] << 8) | (b[7]))),
            'build_date'          : ("%04x/%02x/%02x" % ((b[8] << 8) | (b[9]), (b[10]), (b[11]) )),
            'build_time'          : ("%02x:%02x" % ((b[12]), (b[13]))),
            'vendor_name'         : lookup_table_string('OC_VENDOR', ((b[14] << 8) | (b[15]))),
            'library_name'        : lookup_table_string('OC_LIBRARY', ((b[16] << 8) | (b[17]))),
            'board_name'          : lookup_table_string('OC_BOARD', ((b[18] << 8) | (b[19]))),
            'block_top_count'     : ("0x%04x" % ((b[20] << 8) | (b[21]))),
            'block_user_count'    : ("0x%04x" % ((b[22] << 8) | (b[23]))),
            'block_protocol'      : ("0x%02x" % (b[24])),
            'user_csr_interfaces' : ("0x%02x" % (b[25])),
            'user_memory_sources' : ("0x%02x" % (b[26])),
            'user_memory_sinks'   : ("0x%02x" % (b[27])),
            'user_stream_sources' : ("0x%02x" % (b[28])),
            'user_stream_sinks'   : ("0x%02x" % (b[29])),
            'userspace'           : "",
            'uuid'                : "",
        }
        for i in range (0, 16): self.chip_info_strings['userspace'] += chr(b[32+i])
        for i in range (0, 16): self.chip_info_strings['uuid']      += ("%02x" % (b[48+i]))
        self.serial_write(b'', expect_prompt=True)

    def chip_timer_load(self):
        util.info(f"Loading chip timers")
        self.serial_write(b'T\n')
        self.chip_timers = {
            'seconds_since_reload' : self.serial_read_int32(),
            'seconds_since_reset'  : self.serial_read_int32(),
            'cycles_since_reset'   : self.serial_read_int32(),
            'cycles_under_reset'   : self.serial_read_int32(),
        }
        self.serial_write(b'', expect_prompt=True)

    def bc_send(self, message, end=b'\n'):
        if len(message)<2 or len(message)>100:
            util.error(f"Cannot send BC messages >100B in length, this was: {message} ({len(message)} bytes)", do_exit=False)
            raise HandledError
        self.serial_write(b'B'+ (len(message)+1).to_bytes(1, 'big') + message + end)

    def bc_receive(self):
        b = self.serial_read(1)
        if len(b) == 0:
            util.error("Timeout waiting for response, you probably need to 'reset'", do_exit=False)
            raise HandledError
        length = int(b[0])
        message = self.serial_read(length-1)
        return message

    def bc_send_receive(self, message, end=b'\n'):
        self.bc_send(message,end=b'') # send message, no \n to leave response channel open
        response = self.bc_receive()  # collect message response, channel will have some timeout
        self.serial_write(end)        # close the BC channel
        return response

    def csr_read32(self, block, space, address, msgid=0, verbose=False):
        util.debug(f"Channel: csr_read32(block={block},space={space},address={address:08x})")
        request = (block.to_bytes(2, 'big') +
                   b'\x01' + # read command
                   ((space<<4)+msgid).to_bytes(1, 'big') +
                   address.to_bytes(4, 'big') +
                   int(0).to_bytes(4, 'big'))
        response = self.bc_send_receive(request)
        self.serial_read_prompt()
        if len(response) != 5:
            util.error(f"Expected 5-byte response to CSR BC message, got {response} ({len(response)} bytes)", do_exit=False)
            raise HandledError
        if response[0] != 1:
            util.error(f"Expected ready=1 status byte (0x01), got {response[0]:02x})", do_exit=False)
            raise HandledError
        data = int.from_bytes(response[1:5], 'big')
        util.debug(f"  {data:08x} <- [{block:04x}][{space:01x}][{address:08x}]")
        return data

    def csr_write32(self, block, space, address, data, msgid=0, verbose=False):
        util.debug(f"Channel: csr_write32(block={block},space={space},address={address:08x}, data={data:08x})")
        request = (block.to_bytes(2, 'big') +
                   b'\x02' + # write command
                   ((space<<4)+msgid).to_bytes(1, 'big') +
                   address.to_bytes(4, 'big') +
                   data.to_bytes(4, 'big'))
        response = self.bc_send_receive(request)
        self.serial_read_prompt()
        if len(response) != 5:
            util.error(f"Expected 5-byte response to CSR BC message, got {response} ({len(response)} bytes)", do_exit=False)
            raise HandledError
        if response[0] != 1:
            util.error(f"Expected ready=1 status byte (0x01), got {response[0]:02x})", do_exit=False)
            raise HandledError
        util.debug(f"  {data:08x} -> [{block:04x}][{space:01x}][{address:08x}]")

# **************************************************************
# **** Top Level Commands

def command_set(ch, parts, help_line=False):
    global global_vars
    if help_line:
        util.info(f"Syntax: set [<var> [<value>]]")
        util.info(f"With no arguments, displays value of all variables")
        util.info(f"With one argument, displays value of one variable")
        util.info(f"With two arguments, sets value of one variable")
        util.info(f"Variables are used in various places in the OC_CLI UI, generally")
        util.info(f"using '$var' syntax in CLI inputs will use substitution if the")
        util.info(f"name matches")
        return
    if (len(parts) < 1):
        for key,value in sorted(global_vars.items()):
            util.info(f"{key}={value}")
        return
    key = parts.pop(0)
    if (len(parts)): # set
        global_vars[key] = parts.pop(0)
    else: # get
        if key in global_vars: util.info(f"SET: ${key} = {global_vars[key]}")
        else: util.warning(f"SET: var '${key}' does not exist")

def command_read (ch, parts, help_line=False):
    if help_line:
        util.info(f"Syntax: read|rd|r <address> [<block> <space> [<length> [<jump>]]]")
        return
    if (len(parts) < 1):
        util.info(f"Syntax: read|rd|r <address> [<block> <space> [<length> [<jump>]]]")
        util.error(f"Need at least an address to read", do_exit=False)
        raise HandledError
    address = eval_number(parts.pop(0), ishex=True)
    if parse_block_space(parts):
        if parse_block_space(parts) == 2:
            util.info(f"Syntax: read|rd|r <address> [<block> <space> [<length> [<jump>]]]")
            util.error(f"Need a block and space after address", do_exit=False)
            raise HandledError
    if ((address < 0) or (address > 0xffffffff)):
        util.error(f"Address {address:08x} is not a 32-bit value", do_exit=False)
        raise HandledError
    elif len(parts):
        length = eval_number(parts.pop(0), ishex=True)
        jump = 4
        if (len(parts)):
            jump = eval_number(parts.pop(0), ishex=True)
        on_this_line = 0
        for offset in range(0, length, jump):
            if (on_this_line == 0):
                print("%08x : " % (address+offset), end='')
            data = ch.csr_read32(current_block, current_space, address + offset)
            print("%08x " % data, end='')
            on_this_line += 1
            if on_this_line == 8:
                print("")
                on_this_line = 0
        if (on_this_line):
            print("")
    else:
        data = ch.csr_read32(current_block, current_space, address, verbose=True)
        print("%08x : %08x " % (address, data))

def command_write (ch, parts, help_line=False):
    if help_line:
        util.info(f"Syntax: write|wr|w <address> <data> [<block> <space> [<length> [<jump>]]]")
        return
    if (len(parts) < 2):
        util.info(f"Syntax: write|wr|w <address> <data> [<block> <space> [<length> [<jump>]]]")
        util.error(f"Need at least an address and data to write", do_exit=False)
        raise HandledError
    address = eval_number(parts.pop(0), ishex=True)
    data = eval_number(parts.pop(0), ishex=True)
    if parse_block_space(parts):
        if parse_block_space(parts) == 2:
            util.info(f"Syntax: write|wr|w <address> <data> [<block> <space> [<length> [<jump>]]]")
            util.error(f"Need a channel and space after address", do_exit=False)
            raise HandledError
    if ((address < 0) or (address > 0xffffffff)):
        util.error(f"Address {address:08x} is not a 32-bit value", do_exit=False)
        raise HandledError
    elif ((data < 0) or (data > 0xffffffff)):
        util.error(f"Data {data:08x} is not a 32-bit value", do_exit=False)
        raise HandledError
    else:
        ch.csr_write32(current_block, current_space, address, data, verbose=True)

def command_keygen(ch, parts, help_line=False):
    def usage(s="", quiet=False):
        util.info(f"Syntax: keygen create <fpga_serial:32> <bitstream_id:32> <key0:32> <key1:32> <key2:32> <key3:32> ")
        util.info(f"            ... returns <lic0:32>, <lic1:32>")
        util.info(f"        keygen check <fpga_serial:32> <bitstream_id:32> <key0:32> <key1:32> <key2:32> <key3:32> <lic0:32> <lic1:32>")
        util.info(f"            ... returns PASS/FAIL")
        util.info(f"Note: create a key for fpga_serial==0x12345678 to create a skeleton key (bitstream needs to support this)")
        util.info(f"Note: create a key for inverted bitstream_id to create a timed demo key (bitstream needs to support this)")
        if quiet: return
        util.error(s, do_exit=False)
        raise HandledError
    if len(parts) and parts[0]=='help':
        usage(quiet=True)
        return
    cmd = parts.pop(0)
    if ((cmd != 'create') and (cmd != 'check')):  usage(f"Command must be 'create' or 'check'")
    if ((cmd == 'create') and (len(parts) != 6)): usage(f"Need six arguments for 'create'")
    if ((cmd == 'check') and (len(parts) != 8)):  usage(f"Need eight arguments for 'check'")
    fpga_serial = eval_number(parts.pop(0), ishex=True)
    bitstream_id = eval_number(parts.pop(0), ishex=True)
    key = [ eval_number(parts.pop(0), ishex=True),
            eval_number(parts.pop(0), ishex=True),
            eval_number(parts.pop(0), ishex=True),
            eval_number(parts.pop(0), ishex=True) ]
    if cmd=='check':
      # we are going to decrypt the license (ciphertext) using secret bitstream key.  that should result in
      # plaintext that looks like {serial:32, bitstream:32}
      lic = [ eval_number(parts.pop(0), ishex=True), eval_number(parts.pop(0), ishex=True)]
      pt = btea(lic, -len(lic), key)
      if ((pt[0] == fpga_serial) and (pt[1] == bitstream_id)):
        util.info("PASS: License valid")
      elif ((pt[0] == 0x12345678) and (pt[1] == bitstream_id)):
        util.info("PASS: License is a valid skeleton key (if bitfile supports them)")
      elif ((pt[0] == fpga_serial) and (pt[1] == (bitstream_id^0xffffffff))):
        util.info("PASS: License is a valid timed eval key (if bitfile supports them)")
      else:
        util.warning(f"FAIL: License doesn't match")
        util.warning(f"Assuming good KEY, license is for FPGA_SERIAL={fpga_serial:08x}, BITSTREAM_ID={bitstream_id:08x}")
        util.warning(f"That bitstream ID can be checked against the secret bitstream KEY (if known) to confirm above")
    else: # create
      din = [ fpga_serial, bitstream_id ]
      lic = btea(din, len(din), key)
      util.info(f"LICENSE: {lic[0]:08x} {lic[1]:08x}")

def command_help(ch, parts):
    util.info(f"")
    util.info(f"OC_CLI HELP")
    util.info(f"")
    util.info(f"For any of these commands, get more info with '<cmd> help'...")
    util.info(f"")
    util.info(f"Terminal Basics:")
    util.info(f"  quit, debug, set, history     : as typical")
    util.info(f"")
    util.info(f"Low level channel control:")
    util.info(f"  reset, ping, info, scan       : generally start with reset, ping, info, scan")
    util.info(f"")
    util.info(f"Raw CSR access:")
    util.info(f"  read <address> [<block> [<space>]]          : aka r/rd, will cache block/space")
    util.info(f"  write <address> <data> [<block> [<space>]]  : aka w/wr, will cache block/space")
    util.info(f"")
    util.info(f"Helpful:")
    util.info(f"  timers                        : report chip uptime stats")
    util.info(f"  keygen                        : create/check PROTECT keys")

# **************************************************************
# **** Token processing

current_block = 0
current_space = 0

def parse_block_space(parts):
    global current_block
    global current_space
    if (len(parts)): # we have been given channel + space
        if (len(parts)<2):
            return 2 # return 2 when we can't proceeed, caller prints an appropriate error
        block = eval_number(parts.pop(0))
        space = eval_number(parts.pop(0))
        if ((block < 0) or (block > 0xfff0)):
            util.error(f"Block: {block:04x} is not a valid 16-bit block", do_exit=False)
            raise HandledError
        elif ((space < 0) or (space > 0xf)):
            util.error(f"Space: {space:01x} is not a valid 4-bit space", do_exit=False)
            raise HandledError
        else:
            current_block = block
            current_space = space
    return 0

def process_tokens(ch, parts):
    global interactive_channel
    global interactive_space
    global source_stack
    command = parts.pop(0)
    try:
        if command == 'quit' or command == 'q':
            readline.write_history_file(histfile)
            util.exit(0)
        elif command == 'history' or command == 'h' or command == 'hi' or command == 'hist':
            if (len(parts) < 1):  num_to_show = 10
            else:                 num_to_show = eval_number(parts.pop(0))
            total_items = readline.get_current_history_length()
            num_to_show = min(total_items, num_to_show)
            for i in range(num_to_show):
                print(f"{total_items-num_to_show+i+1:4} {readline.get_history_item(total_items-num_to_show+i+1)}")
        elif eval_regex(r'\!\s*(\d*)',command) :
            total_items = readline.get_current_history_length()
            if m.group(1):        num = int(m.group(1))
            elif len(parts) < 1:  num = (total_items-1)
            else:                 num = eval_number(parts.pop(0))
            print(f"debug here: {total_items} {num}")
            if num < 1:
                util.error(f"Cannot access history line <1", do_exit=False)
                raise HandledError
            if num > (total_items-1):
                util.error(f"Cannot access history line >{total_items}", do_exit=False)
                raise HandledError
            line = readline.get_history_item(num)
            print(f"OC_CLI->{line}")
            readline.replace_history_item(total_items-1, line)
            source_stack.append([line])
        elif command == 'debug':
            if (len(parts) < 1):
                util.info(f"Debug level is currently {util.debug_level}, change with 'debug <level>'")
                return
            util.set_debug_level( eval_number(parts.pop(0)) )
        elif command == 'sleep':
            if (len(parts) < 1):
                util.info(f"Need to provide a number of milliseconds to sleep")
                return
            time.sleep( float(eval_number(parts.pop(0))) / 1000.0 )
        elif command == 'ping' or command == 'p':
            ch.ping()
        elif command == 'performance' or command == 'perf':
            ch.performance_check()
        elif command == 'flush':
            ch.flush()
        elif command == 'reset':
            ch.reset()
        elif command == 'info':
            ch.show_chip_info()
        elif command == 'scan':
            ch.scan_chip()
        elif command == 'timers':
            ch.show_chip_timers()
        elif command == 'read' or command == 'rd' or command == 'r':
            command_read(ch, parts)
        elif command == 'write' or command == 'wr' or command == 'w':
            command_write(ch, parts)
        # for commands within block drivers
        elif (command in ch.block_dict):
            if len(parts) < 2:
                util.info(f"Syntax: {command} <block> <command:'dump','help'> [<command-specific args>]")
                util.error(f"Need at least a block ID and a command", do_exit=False)
                raise HandledError
            block = eval_number(parts.pop(0))
            if block not in ch.block_handler:
                util.info(f"Syntax: {command} <block> <command:'dump','help'> [<command-specific args>]")
                util.error(f"Please do 'scan' first before trying to use block handlers", do_exit=False)
                raise HandledError
            handler = ch.block_handler[block]
            handler.process_tokens(parts)
        # for top level commands pulled in via plugin
        elif ("command_%s" % command) in globals():
            globals()[f"command_{command}"](ch, parts)
        else:
            util.warning(f"Didn't understand command: '{command}'")
    except HandledError:
        return
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      print(traceback.format_exc())
      util.error(f"Unexpected exception ({exc_tb.tb_frame.f_code.co_filename}:{exc_tb.tb_lineno}): {str(e)}")
      return

# **************************************************************
# **** Interactive

source_stack = []

def interactive_get_line(ser):
    global source_stack
    if (len(source_stack) > 0):
        # we are sourcing commands from a file, if there's more than one we finish the latest (last) one
        source_lines = source_stack[len(source_stack)-1]
        line = source_lines.pop(0)
        full_line = ""
        m = re.match(r'^(.*)\\$', line)
        while (m):
            full_line += m.group(1)
            line = source_lines.pop(0)
            m = re.match(r'^(.*)\\$', line)
        full_line += line
        if (len(source_lines) == 0):
            source_stack.pop(-1) # we are done with all lines from the latest list, pop the list off the stack
        return full_line
    else:
        # we have no lines from source commands
        line = input('OC_CLI->')
        full_line = ""
        m = re.match(r'^(.*)\\$', line)
        while (m):
            full_line += m.group(1)
            line = input('        ')
            m = re.match(r'^(.*)\\$', line)
        full_line += line
        return full_line

def interactive(ch):
    global debug
    global m
    ch.flush()
    while 1:
        line = interactive_get_line(ch)
        m = re.match(r'^([^\#]*)\#.*$', line)
        if m: line = m.group(1)
        parts = shlex.split(line)
        if len(parts) == 0: continue
        process_tokens(ch, parts)

# **************************************************************
# **** Interrupt Handler

def signal_handler(sig, frame):
    util.fancy_stop()
    util.info('Received Ctrl+C...', start='\nINFO: [OC_CLI] ')
    util.exit(1)

class HandledError(Exception):
    pass

# **************************************************************
# **** Read name arrays from shared file

# NOTE(drew): use names.py (aka, from names import table)
# TODO(drew): support an argument to BYO table via .txt or .yml or something.
name_tables = { 'OC_VENDOR' : {},
                'OC_LIBRARY' : {},
                'OC_BOARD' : {},
                'PLL_TYPES' : {},
                'CHIPMON_TYPES' : {},
                'IIC_OFFLOAD_TYPES' : {},
                'PCIE_TYPES' : {},
               }

def parse_names():
    name_tables.update(opencos_names.table) #update our global name_table from names.py

def lookup_table_string(table, index):
    if isinstance(table, str) and table in name_tables:
        if index not in name_tables[table]: return "INVALID"
        return name_tables[table][index]
    if isinstance(table, list):
        if index >= len(table): return "INVALID"
        return table[index]
    if isinstance(table, dict):
        if index not in table: return "INVALID"
        return table[index]
    return "INVALID_TABLE"

# **************************************************************
# **** Startup Code

debug_respawn = False
util.progname = "OC_CLI"

def main(*args):
    util.info("*** OpenCOS CLI ***")
    args = list(args)
    if len(args) == 0:
        # If not one passed args, then use sys.argv:
        args = sys.argv[1:]

    try:
        opts,args = getopt.getopt(args, "hp:s:b:",
                                  ["help", "pcie=", "serial=", "baud=",
                                   "color", "no-color",
                                   "quiet", "no-quiet",
                                   "verbose", "no-verbose",
                                   "debug", "no-debug",
                                   "fancy", "no-fancy",
                                   "logfile=", "force-logfile=",
                                   ])
    except getopt.GetoptError as err:
        print(str(err))
        return usage(error_code=-2)

    baud = 460800
    #port = "COM1" if os.name == 'nt' else "/dev/ttyUSB2"
    port = None
    pcie = None
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            return usage(do_exit=False, error_code=0)
        if opt in ['-p', '--pcie']:
            pcie = arg
        if opt in ['-s', '--serial']:
            port = arg
        if opt in ['-b', '--baud']:
            baud = arg
        if opt:
            # attempt to process util args individually:
            if arg:
                util.process_token([opt, arg])
            else:
                util.process_token([opt])

    if port == None and pcie == None and getpass.getuser() == 'root':
        # we have not been given a connection method, infer the best one
        # first we look for valid PCIe devices
        util.info(f"Scanning PCIe for OC device...")
        sp = subprocess.run( 'lspci', stdout=subprocess.PIPE, shell=True, universal_newlines=True)
        for s in sp.stdout.splitlines():
            util.debug(f"Examining {s}")
            m = re.match(r'(\S+) [^\:]+\: Xilinx Corporation Device (\w\w\w\w).*', s)
            if m:
                if m.group(2) == '0c0c':
                    util.info(f"Found Xilinx OC board on PCIe slot {pcie}{' (SELECTED)' if pcie==None else ''}")
                    if pcie == None:
                        pcie = m.group(1)

    if port == None and pcie == None:
        # next we look for valid SERIAL devices
        if getpass.getuser() != 'root':
            util.info(f"Wasn't able to scan PCIe for OC devices; not running as root")
        util.info(f"Scanning Serial for OC device...")
        for p in serial.tools.list_ports.comports():
            util.info(f"DEBUG p={p}")
            if p.manufacturer == 'Xilinx' and p.location.endswith('1.2'):
                util.info(f"Found {p.manufacturer} {p.product} (SN {p.serial_number}) on {p.device}"+
                          f"{' (SELECTED)' if port==None else ''}")
                if port == None:
                    port = p.device

    ch = None
    if port != None:
        try:
            ch = SerialChannel(port, baud)
        except Exception as e:
            if util.args['debug']: print(traceback.format_exc())
            else: print(str(e))
            return usage(error_code=-3)
    elif pcie != None:
        try:
            ch = PCIeChannel(pcie)
        except Exception as e:
            if util.args['debug']: print(traceback.format_exc())
            else: print(str(e))
            return usage(error_code=-3)
    else:
        usage(do_exit=False, error_code=0)
        return util.error(f"Wasn't able to find OC device!")

    parse_names()
    if ch is not None:
        interactive(ch)
        ch.close()

    return 0

def usage(do_exit=True, error_code=0):
    print("")
    print("Usage: oc_cli [-h|--help] [-p|--pcie <slot>] [-s|--serial <port>] [-b|--baud <rate>]")
    print("--help                This screen")
    print("--pcie <slot>         Select PCIe slot. Defaults to and slot with OC device (type 0c0c)")
    print("--serial <port>       Select serial port. Defaults to COM1 on Windows, else /dev/ttyUSB2 (Xilinx default)")
    print("--baud                Select baud rate. Defaults to 460800")
    print("")
    if do_exit:
        return util.exit(error_code)
    else:
        return error_code


def main_cli(support_respawn=False):
    if support_respawn and '--no-respawn' not in sys.argv:
        # If someone called oc_cli directly (aka, __name__ == '__main__'),
        # then we still support a legacy mode of operation - where we check
        # for OC_ROOT (in env, or git repo) to make sure this is the right
        # location of oc_cli by calling main_cli(support_respawn=True).
        # Otherwise, we do not respawn $OC_ROOT/bin/oc_cli
        # Can also be avoided with --no-respawn.

        # Note - respawn will never work if calling as a package executable script,
        # which is why our package entrypoint will be main_cli() w/out support_respawn.
        main_maybe_respawn()

    signal.signal(signal.SIGINT, signal_handler)
    util.global_exit_allowed = True
    rc = main()
    util.exit(rc)


def main_maybe_respawn():

    # First we check if we are respawning
    this_path = os.path.realpath(__file__)
    if debug_respawn: util.info(f"RESPAWN: this_path : '{this_path}'")
    oc_root = util.get_oc_root()
    if debug_respawn: util.info(f"RESPAWN: oc_root   : '{oc_root}'")
    cwd = util.getcwd()
    if debug_respawn: util.info(f"RESPAWN: cwd       : '{cwd}'")
    if oc_root:
        new_paths = [
            os.path.join(oc_root, 'opencos', 'oc_cli.py'),
            os.path.join(oc_root, 'bin', 'oc_cli'),
        ]
        if debug_respawn: util.info(f"RESPAWN: {new_paths=} {this_path=}")
        if this_path not in new_paths and os.path.exists(new_paths[0]):
            # we are not the correct version of oc_cli for this Git repo, we should respawn
            util.info(f"{this_path} respawning {new_paths[0]} in {cwd} with --no-respawn")
            sys.argv[0] = new_paths[0]
            sys.argv.insert(1, '--no-respawn')
            proc = subprocess.Popen(sys.argv, shell=0, cwd=cwd, universal_newlines=True)
            while True:
                try:
                    proc.communicate()
                    break
                except KeyboardInterrupt:
                    continue
            # get exit status from proc and return it
            util.exit(proc.returncode, quiet=True)
        else:
            if debug_respawn: util.info(f"RESPAWN: {oc_root=} respawn not necessary")
    else:
        if debug_respawn: util.info("RESPAWN: respawn not necessary")


if __name__ == "__main__":
    main_cli(support_respawn=True)
