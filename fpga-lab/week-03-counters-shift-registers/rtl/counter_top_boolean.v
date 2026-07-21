//=============================================================================
// File          : counter_top_boolean.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Board         : RealDigital Boolean Board (Xilinx Spartan-7, 100 MHz clock)
// Description   : Top level for the hardware demonstration of the 16-bit
//                 up/down counter on the Boolean board.
//
//                 Board mapping:
//                   btn[0]  -> rst        (synchronous reset, press & hold)
//                   btn[1]  -> enable     (hold pressed to count)
//                   btn[2]  -> direction  (released = count up, pressed = down)
//                   btn[3]  -> load       (loads sw[15:0] into the counter)
//                   sw[15:0]-> din[15:0]  (parallel load data)
//                   led[15:0]-> count[15:0]
//
//                 A 2 Hz tick gates the count enable so the LEDs change at a
//                 rate visible to the eye; the design stays in a single
//                 100 MHz clock domain.
//=============================================================================
`timescale 1ns / 1ps
`default_nettype none

module counter_top_boolean (
    input  wire        clk,                       // 100 MHz, pin F14
    input  wire [15:0] sw,                        // slide switches
    input  wire [3:0]  btn,                       // push buttons (active high)
    output wire [15:0] led                        // LEDs (active high)
);

    wire        slow_tick;
    wire [15:0] count;
    wire        max_tick;
    wire        min_tick;

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

    //-------------------------------------------------------------------------
    // Unit under test: 16-bit synchronous up/down counter
    //-------------------------------------------------------------------------
    up_down_counter_16bit #(
        .WIDTH (16)
    ) u_counter (
        .clk       (clk),
        .rst       (btn[0]),
        .en        (slow_tick & btn[1]),         // visible-rate counting
        .up_n_down (~btn[2]),                    // pressed = down
        .load      (btn[3]),
        .din       (sw),
        .count     (count),
        .max_tick  (max_tick),
        .min_tick  (min_tick)
    );

    assign led = count;

    // max_tick / min_tick are left unconnected on the board demo; they are
    // exercised in the simulation testbench.
    wire unused = &{1'b0, max_tick, min_tick};

endmodule

`default_nettype wire
