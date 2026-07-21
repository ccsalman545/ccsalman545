//=============================================================================
// File          : universal_shift_register_8bit.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Board         : RealDigital Boolean Board (Xilinx Spartan-7, 100 MHz clock)
// Tool          : Xilinx Vivado Design Suite
// Description   : Parameterized (8-bit default) universal shift register in the
//                 style of the classic 74x194 MSI device. A 2-bit mode input
//                 selects one of four synchronous operations:
//                   mode = 2'b00 : HOLD          (retain data)
//                   mode = 2'b01 : SHIFT RIGHT   (sin_r enters the MSB, LSB leaves)
//                   mode = 2'b10 : SHIFT LEFT    (sin_l enters the LSB, MSB leaves)
//                   mode = 2'b11 : PARALLEL LOAD (pout <= pin)
//                 The register also provides a synchronous, active-high reset
//                 and exposes both serial outputs (bits leaving the register).
// Coding style  : Synthesizable Verilog-2001, non-blocking assignments only
//                 inside the clocked always block. A default branch in the
//                 case statement and explicit hold branches guarantee that no
//                 latch can be inferred.
//=============================================================================
`timescale 1ns / 1ps
`default_nettype none

module universal_shift_register_8bit #(
    parameter WIDTH = 8                           // register width in bits
)(
    input  wire             clk,                  // system clock
    input  wire             rst,                  // synchronous reset, active high
    input  wire [1:0]       mode,                 // function select (see above)
    input  wire             sin_r,                // serial input for shift-right (enters MSB)
    input  wire             sin_l,                // serial input for shift-left  (enters LSB)
    input  wire [WIDTH-1:0] pin,                  // parallel data input
    output reg  [WIDTH-1:0] pout,                 // parallel data output (register)
    output wire             sout_l,               // serial output: MSB (leaves on shift-left)
    output wire             sout_r                // serial output: LSB (leaves on shift-right)
);

    //-------------------------------------------------------------------------
    // Mode encoding (same convention as the classic 74194 universal register)
    //-------------------------------------------------------------------------
    localparam [1:0] MODE_HOLD  = 2'b00;
    localparam [1:0] MODE_RIGHT = 2'b01;
    localparam [1:0] MODE_LEFT  = 2'b10;
    localparam [1:0] MODE_LOAD  = 2'b11;

    //-------------------------------------------------------------------------
    // Synchronous register process. The case statement describes the mux that
    // feeds the register bank's D inputs; the flops themselves are updated
    // only on the rising clock edge.
    //-------------------------------------------------------------------------
    always @(posedge clk) begin
        if (rst)
            pout <= {WIDTH{1'b0}};                          // synchronous clear
        else begin
            case (mode)
                MODE_HOLD  : pout <= pout;                              // hold
                MODE_RIGHT : pout <= {sin_r, pout[WIDTH-1:1]};          // shift right
                MODE_LEFT  : pout <= {pout[WIDTH-2:0], sin_l};          // shift left
                MODE_LOAD  : pout <= pin;                               // parallel load
                default    : pout <= pout;                              // safety: hold
            endcase
        end
    end

    //-------------------------------------------------------------------------
    // Serial outputs are continuous decodes of the two end flip-flops, so a
    // cascaded chain (or a testbench) can observe the bits shifted out.
    //-------------------------------------------------------------------------
    assign sout_l = pout[WIDTH-1];
    assign sout_r = pout[0];

endmodule

`default_nettype wire
