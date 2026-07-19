// Week 2 Digital Design Lab testbench
// Self-checking simulation for week2_counter.

`timescale 1ns / 1ps

module tb_week2_counter;

    localparam integer DIVISOR = 4;

    reg       clk;
    reg       reset;
    reg       enable;
    reg       up_down;
    wire [3:0] count;
    integer   failures;

    week2_counter #(
        .DIVISOR(DIVISOR)
    ) dut (
        .clk     (clk),
        .reset   (reset),
        .enable  (enable),
        .up_down (up_down),
        .count   (count)
    );

    // 10 ns clock period.
    always #5 clk = ~clk;

    task wait_ticks;
        input integer number_of_ticks;
        begin
            repeat (number_of_ticks * DIVISOR) @(posedge clk);
            #1;
        end
    endtask

    task check_count;
        input [3:0]   expected;
        input [127:0] test_name;
        begin
            if (count !== expected) begin
                $display("FAIL: %s | expected %h, got %h", test_name,
                         expected, count);
                failures = failures + 1;
            end else begin
                $display("PASS: %s | count = %h", test_name, count);
            end
        end
    endtask

    initial begin
        $dumpfile("tb_week2_counter.vcd");
        $dumpvars(0, tb_week2_counter);

        clk      = 1'b0;
        reset    = 1'b1;
        enable   = 1'b0;
        up_down  = 1'b1;
        failures = 0;

        // Synchronous reset must clear the output.
        repeat (2) @(posedge clk);
        #1;
        check_count(4'h0, "synchronous reset");

        // Count upward and verify the programmable divider.
        reset  = 1'b0;
        enable = 1'b1;
        up_down = 1'b1;
        wait_ticks(1);
        check_count(4'h1, "one up-count tick");
        wait_ticks(3);
        check_count(4'h4, "four total up-count ticks");

        // Disable must hold the count and clear the divider.
        enable = 1'b0;
        repeat (6) @(posedge clk);
        #1;
        check_count(4'h4, "enable low holds count");

        // Re-enabling starts a fresh divider interval.
        enable = 1'b1;
        wait_ticks(1);
        check_count(4'h5, "count after re-enable");

        // Count downward.
        up_down = 1'b0;
        wait_ticks(2);
        check_count(4'h3, "two down-count ticks");

        // Reset from a non-zero state, then verify both wrap directions.
        reset = 1'b1;
        @(posedge clk);
        #1;
        check_count(4'h0, "reset from non-zero state");
        reset = 1'b0;
        up_down = 1'b0;
        wait_ticks(1);
        check_count(4'hf, "down-count wrap 0 to f");
        up_down = 1'b1;
        wait_ticks(1);
        check_count(4'h0, "up-count wrap f to 0");

        if (failures == 0)
            $display("\nWEEK 2 LAB: ALL TESTS PASSED");
        else
            $display("\nWEEK 2 LAB: %0d TEST(S) FAILED", failures);

        $finish;
    end

endmodule
