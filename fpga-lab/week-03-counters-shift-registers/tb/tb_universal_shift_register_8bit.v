//=============================================================================
// File          : tb_universal_shift_register_8bit.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Description   : Self-checking testbench for universal_shift_register_8bit.
//
//                 Stimulus is applied on the NEGATIVE edge of the clock and the
//                 outputs are checked just after each positive edge (#1). Every
//                 check prints a PASS/FAIL line; a final summary is printed and
//                 the simulation terminates automatically with $finish.
//
//                 Tests covered:
//                   T01 synchronous reset
//                   T02 parallel load (mode = 11)
//                   T03 hold (mode = 00) while serial inputs toggle
//                   T04 shift right (mode = 01) with serial input pattern
//                   T05 shift left  (mode = 10) with serial input pattern
//                   T06 mid-stream reset (reset dominates mode)
//                   T07 walking-'1' pattern across all 8 positions
//                   T08 walking-ones fill (0x00 -> 0xFF)
//                   T09 serial outputs sout_l / sout_r observation
//=============================================================================
`timescale 1ns / 1ps

module tb_universal_shift_register_8bit;

    localparam WIDTH      = 8;
    localparam CLK_PERIOD = 10;                     // 10 ns -> 100 MHz

    // Mode encodings (mirror the DUT)
    localparam [1:0] MODE_HOLD  = 2'b00;
    localparam [1:0] MODE_RIGHT = 2'b01;
    localparam [1:0] MODE_LEFT  = 2'b10;
    localparam [1:0] MODE_LOAD  = 2'b11;

    //--------------------------------------------------------------------------
    // Stimulus (regs) and observed outputs (wires)
    //--------------------------------------------------------------------------
    reg              clk;
    reg              rst;
    reg  [1:0]       mode;
    reg              sin_r;
    reg              sin_l;
    reg  [WIDTH-1:0] pin;
    wire [WIDTH-1:0] pout;
    wire             sout_l;
    wire             sout_r;

    //--------------------------------------------------------------------------
    // Book-keeping
    //--------------------------------------------------------------------------
    integer errors;
    integer total;

    //--------------------------------------------------------------------------
    // Device under test
    //--------------------------------------------------------------------------
    universal_shift_register_8bit #(
        .WIDTH (WIDTH)
    ) dut (
        .clk    (clk),
        .rst    (rst),
        .mode   (mode),
        .sin_r  (sin_r),
        .sin_l  (sin_l),
        .pin    (pin),
        .pout   (pout),
        .sout_l (sout_l),
        .sout_r (sout_r)
    );

    //--------------------------------------------------------------------------
    // Clock generator: 100 MHz (T = 10 ns)
    //--------------------------------------------------------------------------
    initial clk = 1'b0;
    always #(CLK_PERIOD/2) clk = ~clk;

    //--------------------------------------------------------------------------
    // Check task: compare pout against expected value, print PASS/FAIL
    //--------------------------------------------------------------------------
    task check_reg;
        input [WIDTH-1:0] exp;
        input [8*64-1:0]  name;                     // message string (vector)
        begin
            total = total + 1;
            if (pout !== exp) begin
                errors = errors + 1;
                $display("[%0t] FAIL : %0s | pout = %b (0x%02h), expected %b (0x%02h)",
                         $time, name, pout, pout, exp, exp);
            end
            else begin
                $display("[%0t] PASS : %0s | pout = %b (0x%02h)",
                         $time, name, pout, pout);
            end
        end
    endtask

    task check_bit;
        input            got;
        input            exp;
        input [8*64-1:0] name;
        begin
            total = total + 1;
            if (got !== exp) begin
                errors = errors + 1;
                $display("[%0t] FAIL : %0s | bit = %b (expected %b)",
                         $time, name, got, exp);
            end
            else begin
                $display("[%0t] PASS : %0s | bit = %b", $time, name, got);
            end
        end
    endtask

    //--------------------------------------------------------------------------
    // Advance one clock edge and check the resulting register value
    //--------------------------------------------------------------------------
    task step_and_check;
        input [WIDTH-1:0] exp;
        input [8*64-1:0]  name;
        begin
            @(posedge clk); #1;
            check_reg(exp, name);
        end
    endtask

    //--------------------------------------------------------------------------
    // Main stimulus
    //--------------------------------------------------------------------------
    initial begin
        // Waveform dump (for external viewers; ignored harmlessly by Vivado)
        $dumpfile("tb_universal_shift_register_8bit.vcd");
        $dumpvars(0, tb_universal_shift_register_8bit);

        errors = 0;
        total  = 0;

        // Initialise all inputs before the first clock edge
        rst   = 1'b1;
        mode  = MODE_HOLD;
        sin_r = 1'b0;
        sin_l = 1'b0;
        pin   = {WIDTH{1'b0}};

        $display("==============================================================");
        $display(" TESTBENCH : tb_universal_shift_register_8bit  (100 MHz clock)");
        $display("==============================================================");

        //----------------------------------------------------------------------
        // T01 - Synchronous reset over two clock edges
        //----------------------------------------------------------------------
        $display("--- T01: synchronous reset ---");
        step_and_check(8'h00, "T01a: rst clears register");
        step_and_check(8'h00, "T01b: rst held, register stays 0");
        @(negedge clk);
        rst = 1'b0;

        //----------------------------------------------------------------------
        // T02 - Parallel load of 8'hA5 = 1010_0101
        //----------------------------------------------------------------------
        $display("--- T02: parallel load ---");
        @(negedge clk);
        mode = MODE_LOAD;
        pin  = 8'hA5;
        step_and_check(8'hA5, "T02a: load 0xA5");
        check_bit(sout_l, 1'b1, "T02b: sout_l = MSB of 0xA5");
        check_bit(sout_r, 1'b1, "T02c: sout_r = LSB of 0xA5");

        //----------------------------------------------------------------------
        // T03 - Hold for three clocks while the serial inputs toggle; the
        //       stored value must not change.
        //----------------------------------------------------------------------
        $display("--- T03: hold with toggling serial inputs ---");
        @(negedge clk);
        mode  = MODE_HOLD;
        sin_r = 1'b1;
        sin_l = 1'b1;
        step_and_check(8'hA5, "T03a: hold 1 (sin = 1,1)");
        @(negedge clk);
        sin_r = 1'b0;
        sin_l = 1'b1;
        step_and_check(8'hA5, "T03b: hold 2 (sin = 0,1)");
        @(negedge clk);
        sin_r = 1'b1;
        sin_l = 1'b1;
        pin   = 8'hFF;
        step_and_check(8'hA5, "T03c: hold 3 (even pin ignored)");

        //----------------------------------------------------------------------
        // T04 - Shift right four times with serial input pattern 1,0,1,1
        //       0xA5 = 1010_0101 ->
        //       -> 1101_0010 -> 0110_1001 -> 1011_0100 -> 1101_1010
        //----------------------------------------------------------------------
        $display("--- T04: shift right x4 (sin_r = 1,0,1,1) ---");
        @(negedge clk);
        mode  = MODE_RIGHT;
        sin_r = 1'b1;
        check_bit(sout_r, 1'b1, "T04a: bit leaving LSB before step 1");
        step_and_check(8'hD2, "T04b: shift right 1 -> 0xD2");
        @(negedge clk);
        sin_r = 1'b0;
        step_and_check(8'h69, "T04c: shift right 2 -> 0x69");
        @(negedge clk);
        sin_r = 1'b1;
        step_and_check(8'hB4, "T04d: shift right 3 -> 0xB4");
        step_and_check(8'hDA, "T04e: shift right 4 -> 0xDA");

        //----------------------------------------------------------------------
        // T05 - Shift left four times with serial input pattern 0,1,0,1
        //       0xDA = 1101_1010 ->
        //       -> 1011_0100 -> 0110_1001 -> 1101_0010 -> 1010_0101 (back!)
        //----------------------------------------------------------------------
        $display("--- T05: shift left x4 (sin_l = 0,1,0,1) ---");
        @(negedge clk);
        mode  = MODE_LEFT;
        sin_l = 1'b0;
        check_bit(sout_l, 1'b1, "T05a: bit leaving MSB before step 1");
        step_and_check(8'hB4, "T05b: shift left 1 -> 0xB4");
        @(negedge clk);
        sin_l = 1'b1;
        step_and_check(8'h69, "T05c: shift left 2 -> 0x69");
        @(negedge clk);
        sin_l = 1'b0;
        step_and_check(8'hD2, "T05d: shift left 3 -> 0xD2");
        @(negedge clk);
        sin_l = 1'b1;
        step_and_check(8'hA5, "T05e: shift left 4 -> 0xA5 (round trip)");

        //----------------------------------------------------------------------
        // T06 - Load a marker, then assert reset in the middle of a shift:
        //       reset must dominate the mode field.
        //----------------------------------------------------------------------
        $display("--- T06: reset dominates mode ---");
        @(negedge clk);
        mode = MODE_LOAD;
        pin  = 8'h3C;
        step_and_check(8'h3C, "T06a: load 0x3C");
        @(negedge clk);
        rst   = 1'b1;
        mode  = MODE_RIGHT;
        sin_r = 1'b1;
        step_and_check(8'h00, "T06b: reset wins over shift-right");
        @(negedge clk);
        rst = 1'b0;

        //----------------------------------------------------------------------
        // T07 - Walking '1' (LED-chaser) pattern: load 0x01 and shift left
        //       with sin_l = 0 until the '1' walks off the MSB end.
        //----------------------------------------------------------------------
        $display("--- T07: walking one ---");
        @(negedge clk);
        mode = MODE_LOAD;
        pin  = 8'h01;
        step_and_check(8'h01, "T07a: load 0x01");
        @(negedge clk);
        mode  = MODE_LEFT;
        sin_l = 1'b0;
        step_and_check(8'h02, "T07b: walk 1 -> 0x02");
        step_and_check(8'h04, "T07c: walk 2 -> 0x04");
        step_and_check(8'h08, "T07d: walk 3 -> 0x08");
        step_and_check(8'h10, "T07e: walk 4 -> 0x10");
        step_and_check(8'h20, "T07f: walk 5 -> 0x20");
        step_and_check(8'h40, "T07g: walk 6 -> 0x40");
        step_and_check(8'h80, "T07h: walk 7 -> 0x80");
        step_and_check(8'h00, "T07i: walk 8 -> 0x00 (1 falls off the end)");

        //----------------------------------------------------------------------
        // T08 - Walking-ones fill: from 0x00 shift left with sin_l = 1
        //----------------------------------------------------------------------
        $display("--- T08: ones fill ---");
        @(negedge clk);
        mode  = MODE_LEFT;
        sin_l = 1'b1;
        step_and_check(8'h01, "T08a: fill 1 -> 0x01");
        step_and_check(8'h03, "T08b: fill 2 -> 0x03");
        step_and_check(8'h07, "T08c: fill 3 -> 0x07");
        step_and_check(8'h0F, "T08d: fill 4 -> 0x0F");
        step_and_check(8'h1F, "T08e: fill 5 -> 0x1F");
        step_and_check(8'h3F, "T08f: fill 6 -> 0x3F");
        step_and_check(8'h7F, "T08g: fill 7 -> 0x7F");
        step_and_check(8'hFF, "T08h: fill 8 -> 0xFF");
        check_bit(sout_l, 1'b1, "T08i: sout_l = 1 at 0xFF");
        check_bit(sout_r, 1'b1, "T08j: sout_r = 1 at 0xFF");

        //----------------------------------------------------------------------
        // T09 - Serial-out observation while shifting right: from 0xFF with
        //       sin_r = 0, ones must pour out of sout_r, LSB first.
        //----------------------------------------------------------------------
        $display("--- T09: serial-out on shift right ---");
        @(negedge clk);
        mode  = MODE_RIGHT;
        sin_r = 1'b0;
        check_bit(sout_r, 1'b1, "T09a: sout_r = 1 (0xFF before step)");
        step_and_check(8'h7F, "T09b: shift right -> 0x7F");
        step_and_check(8'h3F, "T09c: shift right -> 0x3F");
        step_and_check(8'h1F, "T09d: shift right -> 0x1F");
        check_bit(sout_r, 1'b1, "T09e: sout_r still 1");
        step_and_check(8'h0F, "T09f: shift right -> 0x0F");
        step_and_check(8'h07, "T09g: shift right -> 0x07");
        step_and_check(8'h03, "T09h: shift right -> 0x03");
        step_and_check(8'h01, "T09i: shift right -> 0x01");
        step_and_check(8'h00, "T09j: shift right -> 0x00 (register empty)");
        check_bit(sout_l, 1'b0, "T09k: sout_l = 0 at 0x00");
        check_bit(sout_r, 1'b0, "T09l: sout_r = 0 at 0x00");

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
        #100000;                                      // 100 us of simulation time
        $display("[%0t] ERROR : watchdog timeout - simulation aborted", $time);
        $finish;
    end

endmodule
