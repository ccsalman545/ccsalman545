// Week 2 Digital Design Lab
// Experiment: Parameterised 4-bit synchronous up/down counter
// Target: Digilent Basys 3 (100 MHz system clock)
//
// reset   : synchronous, active-high
// enable  : high enables counting; low holds count and clears the divider
// up_down : high = increment, low = decrement
// count   : 4-bit LED/display output

`timescale 1ns / 1ps

module week2_counter #(
    // For the Basys 3, 50_000_000 gives one count event every 0.5 s,
    // or two visible count changes per second, from a 100 MHz clock.
    // Set DIVISOR = 1 for a count on every rising edge in simulation.
    parameter integer DIVISOR = 50_000_000
) (
    input  wire       clk,
    input  wire       reset,
    input  wire       enable,
    input  wire       up_down,
    output reg  [3:0] count
);

    // $clog2(1) is zero in some tools, so keep the counter at least one bit.
    localparam integer DIVIDER_WIDTH = (DIVISOR < 2) ? 1 : $clog2(DIVISOR);

    reg [DIVIDER_WIDTH-1:0] divider_count;

    // The parameter is a constant, so Vivado will optimise the comparison.
    wire divider_terminal = (DIVISOR <= 1) ||
                            (divider_count == DIVISOR - 1);

    always @(posedge clk) begin
        if (reset) begin
            divider_count <= {DIVIDER_WIDTH{1'b0}};
            count         <= 4'b0000;
        end else if (!enable) begin
            // Restart the timing interval when counting is disabled. This
            // makes the first enabled count deterministic.
            divider_count <= {DIVIDER_WIDTH{1'b0}};
        end else if (divider_terminal) begin
            divider_count <= {DIVIDER_WIDTH{1'b0}};
            if (up_down)
                count <= count + 4'd1;  // 4-bit arithmetic wraps at 15 -> 0
            else
                count <= count - 4'd1;  // 4-bit arithmetic wraps at 0 -> 15
        end else begin
            divider_count <= divider_count + 1'b1;
        end
    end

endmodule
