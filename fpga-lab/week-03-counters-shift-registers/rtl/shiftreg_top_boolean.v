//=============================================================================
// File          : shiftreg_top_boolean.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Board         : RealDigital Boolean Board (Xilinx Spartan-7, 100 MHz clock)
// Description   : Top level for the hardware demonstration of the 8-bit
//                 universal shift register on the Boolean board.
//
//                 Board mapping:
//                   btn[0]   -> rst          (synchronous reset)
//                   sw[1:0]  -> mode         (00 hold, 01 right, 10 left, 11 load)
//                   sw[9:2]  -> pin[7:0]     (parallel data)
//                   sw[10]   -> sin_r        (serial in  for shift right)
//                   sw[11]   -> sin_l        (serial in  for shift left)
//                   led[7:0] -> pout[7:0]    (register contents)
//                   led[14]  -> sout_r       (LSB shifted out on shift-right)
//                   led[15]  -> sout_l       (MSB shifted out on shift-left)
//
//                 The mode is applied only while the 2 Hz tick is active, so
//                 each shift/load step happens at an eye-visible rate and the
//                 register holds between steps.
//=============================================================================
`timescale 1ns / 1ps
`default_nettype none

module shiftreg_top_boolean (
    input  wire        clk,                       // 100 MHz, pin F14
    input  wire [15:0] sw,                        // slide switches
    input  wire [3:0]  btn,                       // push buttons (active high)
    output wire [15:0] led                        // LEDs (active high)
);

    wire slow_tick;
    wire [1:0] mode;
    wire [7:0] pout;
    wire       sout_l;
    wire       sout_r;

    //-------------------------------------------------------------------------
    // 2 Hz strobe generator (100 MHz / 50,000,000)
    //-------------------------------------------------------------------------
    clock_enable_gen #(
        .DIVISOR (50000000)
    ) u_tick (
        .clk  (clk),
        .rst  (btn[0]),
        .tick (slow_tick)
    );

    // Apply the selected operation once per tick; hold in between.
    assign mode = slow_tick ? sw[1:0] : 2'b00;

    //-------------------------------------------------------------------------
    // Unit under test: 8-bit universal shift register
    //-------------------------------------------------------------------------
    universal_shift_register_8bit #(
        .WIDTH (8)
    ) u_shiftreg (
        .clk    (clk),
        .rst    (btn[0]),
        .mode   (mode),
        .sin_r  (sw[10]),
        .sin_l  (sw[11]),
        .pin    (sw[9:2]),
        .pout   (pout),
        .sout_l (sout_l),
        .sout_r (sout_r)
    );

    assign led[7:0]  = pout;
    assign led[13:8] = 6'b000000;
    assign led[14]   = sout_r;
    assign led[15]   = sout_l;

endmodule

`default_nettype wire
