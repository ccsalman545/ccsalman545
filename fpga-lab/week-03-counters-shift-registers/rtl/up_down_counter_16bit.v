//=============================================================================
// File          : up_down_counter_16bit.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Board         : RealDigital Boolean Board (Xilinx Spartan-7, 100 MHz clock)
// Tool          : Xilinx Vivado Design Suite
// Description   : Parameterized synchronous binary up/down counter (16-bit
//                 default). Features:
//                   - Synchronous, active-high reset
//                   - Synchronous parallel load
//                   - Count-enable control (clock-enable style, single clock)
//                   - Up/Down direction select
//                   - Terminal-count flags (max_tick / min_tick) for cascade
// Input priority: rst > load > en > hold
// Coding style  : Synthesizable Verilog-2001, non-blocking assignments only
//                 inside the clocked always block.
//=============================================================================
`timescale 1ns / 1ps
`default_nettype none

module up_down_counter_16bit #(
    parameter WIDTH = 16                          // counter width in bits
)(
    input  wire             clk,                  // system clock
    input  wire             rst,                  // synchronous reset, active high
    input  wire             en,                   // count enable (1 = count)
    input  wire             up_n_down,            // direction: 1 = up, 0 = down
    input  wire             load,                 // synchronous load (1 = load din)
    input  wire [WIDTH-1:0] din,                  // parallel load data
    output reg  [WIDTH-1:0] count,                // counter output
    output wire             max_tick,             // 1 when count == all ones
    output wire             min_tick              // 1 when count == all zeros
);

    // Constant patterns, written in a width-agnostic way (parameterization).
    localparam [WIDTH-1:0] ALL_ONES  = {WIDTH{1'b1}};
    localparam [WIDTH-1:0] ALL_ZEROS = {WIDTH{1'b0}};

    //-------------------------------------------------------------------------
    // Synchronous counter process.
    // Everything happens ONLY on the rising edge of clk -> all control inputs
    // (reset, load, enable, direction) are synchronous, which is the style
    // recommended for FPGA flip-flops with CE/SR control ports.
    //-------------------------------------------------------------------------
    always @(posedge clk) begin
        if (rst)
            count <= ALL_ZEROS;                     // (1) reset dominates
        else if (load)
            count <= din;                           // (2) then parallel load
        else if (en) begin                          // (3) then enabled counting
            if (up_n_down)
                count <= count + 1'b1;              //    up-count (rollover at FFFF)
            else
                count <= count - 1'b1;              //    down-count (rollover at 0000)
        end
        else
            count <= count;                         // (4) explicit hold (en = 0)
    end

    //-------------------------------------------------------------------------
    // Terminal-count flags: continuous (combinational) decode of the count.
    // Useful to cascade counters or to detect overflow/underflow events.
    //-------------------------------------------------------------------------
    assign max_tick = (count == ALL_ONES);
    assign min_tick = (count == ALL_ZEROS);

endmodule

`default_nettype wire
