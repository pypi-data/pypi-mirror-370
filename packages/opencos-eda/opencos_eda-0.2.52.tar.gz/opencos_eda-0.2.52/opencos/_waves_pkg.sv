package _waves_pkg;

`ifdef SIMULATION
`ifndef _WAVES_PKG_DISABLE_DUMPFILE // hook to disable this if user chooses
`ifdef VERILATOR

  //
  // Handle waves for +trace for Verilator, if there was no other $dumpfile in the
  // user source code, and the `eda` command had --waves present.
  //
  // Simulation runtime usage:
  // +trace=vcd    : Verilator/iverilog dump.vcd
  // all others    : Verilator dump.fst
  //
  bit        trace_en_init = 0;
  bit        trace_en      = init_trace();

  function automatic bit init_trace();

    if (trace_en_init) // only do this once.
      return trace_en;

    trace_en_init = 1;

    if ($test$plusargs("trace") != 0) begin
      automatic string trace_str_value = "";
      void'($value$plusargs("trace=%s", trace_str_value));
      if (trace_str_value.tolower() == "vcd") begin
        $display("%t %m: Starting tracing to ./dump.vcd, plusarg +trace=%s",
                 $realtime, trace_str_value);
        $dumpfile("dump.vcd");
        $dumpvars();
        return 1;
      end
    end

    $display("%t %m: Starting tracing to ./dump.fst", $realtime);
    $dumpfile("dump.fst");
    $dumpvars();
    return 1;

  endfunction : init_trace

`endif // #verilator
`endif
`endif

endpackage : _waves_pkg
