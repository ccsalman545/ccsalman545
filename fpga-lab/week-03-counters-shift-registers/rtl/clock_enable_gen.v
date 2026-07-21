//=============================================================================
// File          : clock_enable_gen.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Board         : RealDigital Boolean Board (Xilinx Spartan-7, 100 MHz clock)
// Description   : Generates a one-clock-cycle "tick" pulse every DIVISOR
//                 clock cycles. The tick is used as a CLOCK ENABLE so that the
//                 human-eye-visible counting/shifting rate is produced without
//                 creating a second (divided) clock domain - this keeps the
//                 design fully synchronous and timing-clean in Vivado.
//                 Default: 100 MHz / 50,000,000 = 2 Hz tick (0.5 s period).
//=============================================================================
`timescale 1ns / 1ps
`default_nettype none

module clock_enable_gen #(
    parameter DIVISOR = 50000000                  // clocks per tick
)(
    input  wire clk,                              // system clock
    input  wire rst,                              // synchronous reset, active high
    output reg  tick                              // 1-cycle pulse, DIVISOR period
);

    localparam integer MAX = DIVISOR - 1;

    reg [31:0] div_cnt;                           // 32 bits cover up to 4.29e9

    always @(posedge clk) begin
        if (rst) begin
            div_cnt <= 32'd0;
            tick    <= 1'b0;
        end
        else if (div_cnt == MAX) begin            // terminal count reached
            div_cnt <= 32'd0;
            tick    <= 1'b1;                      // emit single-cycle pulse
        end
        else begin
            div_cnt <= div_cnt + 1'b1;
            tick    <= 1'b0;
        end
    end

endmodule

`default_nettype wire
