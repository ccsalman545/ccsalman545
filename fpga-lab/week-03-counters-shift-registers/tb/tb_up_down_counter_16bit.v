//=============================================================================
// File          : tb_up_down_counter_16bit.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Description   : Self-checking testbench for up_down_counter_16bit.
//
//                 Stimulus is applied on the NEGATIVE edge of the clock so the
//                 inputs are stable around the active (positive) edge, and the
//                 outputs are checked just after each positive edge (#1). Every
//                 check prints a PASS/FAIL line; a final summary is printed and
//                 the simulation terminates automatically with $finish.
//
//                 Tests covered:
//                   T01 synchronous reset
//                   T02 hold when en = 0
//                   T03 synchronous parallel load
//                   T04 load priority over enable
//                   T05 up-counting sequence
//                   T06 hold (data retention) while disabled
//                   T07 down-counting sequence
//                   T08 terminal count 0xFFFF and upward rollover (overflow)
//                   T09 terminal count 0x0000 and downward rollover (underflow)
//                   T10 reset priority over load
//                   T11 direction change mid-stream
//                   T12 full-range sweep 0 -> 65535 -> 0 (65536 counts)
//=============================================================================
`timescale 1ns / 1ps

module tb_up_down_counter_16bit;

    localparam WIDTH      = 16;
    localparam CLK_PERIOD = 10;                     // 10 ns -> 100 MHz

    //--------------------------------------------------------------------------
    // Stimulus (regs) and observed outputs (wires)
    //--------------------------------------------------------------------------
    reg                 clk;
    reg                 rst;
    reg                 en;
    reg                 up_n_down;
    reg                 load;
    reg  [WIDTH-1:0]    din;
    wire [WIDTH-1:0]    count;
    wire                max_tick;
    wire                min_tick;

    //--------------------------------------------------------------------------
    // Book-keeping
    //--------------------------------------------------------------------------
    integer errors;
    integer total;
    integer i;

    //--------------------------------------------------------------------------
    // Device under test
    //--------------------------------------------------------------------------
    up_down_counter_16bit #(
        .WIDTH (WIDTH)
    ) dut (
        .clk       (clk),
        .rst       (rst),
        .en        (en),
        .up_n_down (up_n_down),
        .load      (load),
        .din       (din),
        .count     (count),
        .max_tick  (max_tick),
        .min_tick  (min_tick)
    );

    //--------------------------------------------------------------------------
    // Clock generator: 100 MHz (T = 10 ns)
    //--------------------------------------------------------------------------
    initial clk = 1'b0;
    always #(CLK_PERIOD/2) clk = ~clk;

    //--------------------------------------------------------------------------
    // Check tasks: compare against expected value, print PASS/FAIL, keep score
    //--------------------------------------------------------------------------
    task check_count;
        input [WIDTH-1:0] exp;
        input [8*64-1:0]  name;                     // message string (vector)
        begin
            total = total + 1;
            if (count !== exp) begin
                errors = errors + 1;
                $display("[%0t] FAIL : %0s | count = 0x%04h (expected 0x%04h)",
                         $time, name, count, exp);
            end
            else begin
                $display("[%0t] PASS : %0s | count = 0x%04h",
                         $time, name, count);
            end
        end
    endtask

    task check_flag;
        input            got;
        input            exp;
        input [8*64-1:0] name;
        begin
            total = total + 1;
            if (got !== exp) begin
                errors = errors + 1;
                $display("[%0t] FAIL : %0s | flag = %b (expected %b)",
                         $time, name, got, exp);
            end
            else begin
                $display("[%0t] PASS : %0s | flag = %b", $time, name, got);
            end
        end
    endtask

    //--------------------------------------------------------------------------
    // Advance one clock edge and check the resulting count value
    //--------------------------------------------------------------------------
    task step_and_check;
        input [WIDTH-1:0] exp;
        input [8*64-1:0]  name;
        begin
            @(posedge clk); #1;
            check_count(exp, name);
        end
    endtask

    //--------------------------------------------------------------------------
    // Main stimulus
    //--------------------------------------------------------------------------
    initial begin
        // Waveform dump (for external viewers; ignored harmlessly by Vivado)
        $dumpfile("tb_up_down_counter_16bit.vcd");
        $dumpvars(0, tb_up_down_counter_16bit);

        errors = 0;
        total  = 0;

        // Initialise all inputs before the first clock edge
        rst       = 1'b1;
        en        = 1'b0;
        up_n_down = 1'b1;
        load      = 1'b0;
        din       = {WIDTH{1'b0}};

        $display("==============================================================");
        $display(" TESTBENCH : tb_up_down_counter_16bit  (100 MHz clock)");
        $display("==============================================================");

        //----------------------------------------------------------------------
        // T01 - Synchronous reset, held active for two clock edges
        //----------------------------------------------------------------------
        $display("--- T01: synchronous reset ---");
        step_and_check(16'h0000, "T01a: rst clears counter");
        step_and_check(16'h0000, "T01b: rst held, counter stays 0");

        //----------------------------------------------------------------------
        // T02 - Release reset; with en = 0 and load = 0 the value must hold
        //----------------------------------------------------------------------
        $display("--- T02: hold with en = 0 ---");
        @(negedge clk);
        rst = 1'b0;
        step_and_check(16'h0000, "T02: hold after reset release");

        //----------------------------------------------------------------------
        // T03 - Synchronous parallel load of 0x1234
        //----------------------------------------------------------------------
        $display("--- T03: synchronous load ---");
        @(negedge clk);
        load = 1'b1;
        din  = 16'h1234;
        step_and_check(16'h1234, "T03: load 0x1234");

        //----------------------------------------------------------------------
        // T04 - While load = 1 a new datum is captured every clock, even though
        //       en = 1 (demonstrates load priority over enable/count)
        //----------------------------------------------------------------------
        $display("--- T04: load priority over enable ---");
        @(negedge clk);
        en  = 1'b1;
        din = 16'hABCD;
        step_and_check(16'hABCD, "T04: load wins over count-up request");
        @(negedge clk);
        load = 1'b0;
        en   = 1'b0;

        //----------------------------------------------------------------------
        // T05 - Up counting: five enabled steps from 0xABCD
        //----------------------------------------------------------------------
        $display("--- T05: count up x5 ---");
        @(negedge clk);
        en        = 1'b1;
        up_n_down = 1'b1;
        step_and_check(16'hABCE, "T05a: up-count 1");
        step_and_check(16'hABCF, "T05b: up-count 2");
        step_and_check(16'hABD0, "T05c: up-count 3");
        step_and_check(16'hABD1, "T05d: up-count 4");
        step_and_check(16'hABD2, "T05e: up-count 5");

        //----------------------------------------------------------------------
        // T06 - Hold: disable counting for three clocks, value must not move
        //----------------------------------------------------------------------
        $display("--- T06: hold while en = 0 ---");
        @(negedge clk);
        en = 1'b0;
        step_and_check(16'hABD2, "T06a: hold 1");
        step_and_check(16'hABD2, "T06b: hold 2");
        step_and_check(16'hABD2, "T06c: hold 3");

        //----------------------------------------------------------------------
        // T07 - Down counting: three enabled steps from 0xABD2
        //----------------------------------------------------------------------
        $display("--- T07: count down x3 ---");
        @(negedge clk);
        en        = 1'b1;
        up_n_down = 1'b0;
        step_and_check(16'hABD1, "T07a: down-count 1");
        step_and_check(16'hABD0, "T07b: down-count 2");
        step_and_check(16'hABCF, "T07c: down-count 3");

        //----------------------------------------------------------------------
        // T08 - Maximum count and upward rollover (overflow at FFFF -> 0000)
        //----------------------------------------------------------------------
        $display("--- T08: overflow / rollover at 0xFFFF ---");
        @(negedge clk);
        load      = 1'b1;
        en        = 1'b0;
        up_n_down = 1'b1;
        din       = 16'hFFFE;
        step_and_check(16'hFFFE, "T08a: load 0xFFFE");
        @(negedge clk);
        load = 1'b0;
        en   = 1'b1;
        step_and_check(16'hFFFF, "T08b: count reaches terminal 0xFFFF");
        check_flag(max_tick, 1'b1, "T08c: max_tick asserted at 0xFFFF");
        check_flag(min_tick, 1'b0, "T08d: min_tick low at 0xFFFF");
        step_and_check(16'h0000, "T08e: rollover FFFF -> 0000");
        check_flag(max_tick, 1'b0, "T08f: max_tick deasserted after rollover");

        //----------------------------------------------------------------------
        // T09 - Minimum count and downward rollover (underflow at 0000 -> FFFF)
        //----------------------------------------------------------------------
        $display("--- T09: underflow / rollover at 0x0000 ---");
        @(negedge clk);
        load = 1'b1;
        en   = 1'b0;
        din  = 16'h0001;
        step_and_check(16'h0001, "T09a: load 0x0001");
        @(negedge clk);
        load      = 1'b0;
        en        = 1'b1;
        up_n_down = 1'b0;
        step_and_check(16'h0000, "T09b: count reaches terminal 0x0000");
        check_flag(min_tick, 1'b1, "T09c: min_tick asserted at 0x0000");
        check_flag(max_tick, 1'b0, "T09d: max_tick low at 0x0000");
        step_and_check(16'hFFFF, "T09e: rollover 0000 -> FFFF");
        check_flag(min_tick, 1'b0, "T09f: min_tick deasserted after rollover");

        //----------------------------------------------------------------------
        // T10 - Reset has the highest priority (reset while load also active)
        //----------------------------------------------------------------------
        $display("--- T10: reset priority over load ---");
        @(negedge clk);
        rst  = 1'b1;
        load = 1'b1;
        din  = 16'h5555;
        step_and_check(16'h0000, "T10: reset dominates simultaneous load");
        @(negedge clk);
        rst  = 1'b0;
        load = 1'b0;
        en   = 1'b0;

        //----------------------------------------------------------------------
        // T11 - Direction change mid-stream around a small value
        //----------------------------------------------------------------------
        $display("--- T11: direction change mid-stream ---");
        @(negedge clk);
        load = 1'b1;
        din  = 16'h0005;
        step_and_check(16'h0005, "T11a: load 0x0005");
        @(negedge clk);
        load      = 1'b0;
        en        = 1'b1;
        up_n_down = 1'b1;
        step_and_check(16'h0006, "T11b: up to 6");
        step_and_check(16'h0007, "T11c: up to 7");
        step_and_check(16'h0008, "T11d: up to 8");
        @(negedge clk);
        up_n_down = 1'b0;
        step_and_check(16'h0007, "T11e: reverse, down to 7");
        @(negedge clk);
        up_n_down = 1'b1;
        step_and_check(16'h0008, "T11f: reverse again, up to 8");

        //----------------------------------------------------------------------
        // T12 - Full-range sweep: reset, then count up through all 65536 states
        //       and verify the counter returns to zero exactly on time.
        //----------------------------------------------------------------------
        $display("--- T12: full-range sweep (65536 counts) ---");
        @(negedge clk);
        rst = 1'b1;
        en  = 1'b0;
        @(posedge clk); #1;
        check_count(16'h0000, "T12a: reset before sweep");
        @(negedge clk);
        rst       = 1'b0;
        en        = 1'b1;
        up_n_down = 1'b1;
        for (i = 1; i <= 65535; i = i + 1) begin
            @(posedge clk); #1;
            if (count !== i[15:0]) begin
                errors = errors + 1;
                $display("[%0t] FAIL : T12 sweep | count = 0x%04h (expected 0x%04h)",
                         $time, count, i[15:0]);
            end
            total = total + 1;
        end
        check_flag(max_tick, 1'b1, "T12b: max_tick at end of sweep (0xFFFF)");
        step_and_check(16'h0000, "T12c: sweep wraps to 0 after 65536 counts");

        //----------------------------------------------------------------------
        // Final summary and automatic termination
        //----------------------------------------------------------------------
        @(negedge clk);
        $display("==============================================================");
        $display(" SUMMARY : %0d checks executed, %0d error(s) detected", total, errors);
        if (errors == 0)
            $display(" >>> OVERALL RESULT : PASS <<<");
        else
            $display(" >>> OVERALL RESULT : FAIL <<<");
        $display("==============================================================");
        $finish;
    end

    //--------------------------------------------------------------------------
    // Watchdog: abort if the testbench ever deadlocks
    //--------------------------------------------------------------------------
    initial begin
        #2000000;                                     // 2 ms of simulation time
        $display("[%0t] ERROR : watchdog timeout - simulation aborted", $time);
        $finish;
    end

endmodule
