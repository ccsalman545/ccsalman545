# Week 2 Digital Design Lab Submission

## Experiment: Parameterised 4-bit Synchronous Up/Down Counter

| Field | Details |
|---|---|
| **Student** | Muhammed Salman CC |
| **Course / class** | M.Sc. Electronics — Digital Design / FPGA Lab |
| **Week** | 2 |
| **Date** | 19 July 2026 |
| **Target board** | Digilent Basys 3, Artix-7 XC7A35T-1CPG236C |
| **HDL** | Verilog-2001/SystemVerilog-compatible Verilog |
| **Tool flow** | Xilinx Vivado for synthesis/implementation; Icarus Verilog for optional simulation |

> **Implementation assumption:** This submission uses the common Week 2 FPGA exercise of a 4-bit synchronous up/down counter. The XDC is specifically for the Digilent Basys 3. If the laboratory handout specifies a different circuit or FPGA board, the RTL interface and pin constraints must be updated before submission/programming.

---

## 1. Aim

To design, simulate, and implement a parameterised 4-bit synchronous up/down counter in Verilog. The counter shall:

1. clear to `0000` when the active-high synchronous reset is asserted;
2. increment on a timing tick when `enable = 1` and `up_down = 1`;
3. decrement on a timing tick when `enable = 1` and `up_down = 0`;
4. hold its value when `enable = 0`; and
5. wrap naturally between `4'hF` and `4'h0`.

The design includes a clock divider so that the count changes are visible on the Basys 3 LEDs instead of occurring too quickly to observe at the 100 MHz system-clock rate.

## 2. Required files

```text
week-2-lab/
├── Week_2_Lab_Submission.md          # this report
├── Makefile                          # optional Icarus Verilog simulation command
├── src/
│   └── week2_counter.v               # synthesizable design-under-test
├── sim/
│   └── tb_week2_counter.v            # self-checking testbench
└── constraints/
    └── basys3_week2_counter.xdc      # Basys 3 pin and clock constraints
```

## 3. Hardware and I/O assignment

| Signal | Direction | Basys 3 control | FPGA pin | Function |
|---|---:|---|---|---|
| `clk` | input | 100 MHz oscillator | `W5` | System clock |
| `reset` | input | Centre pushbutton (`BTNC`) | `U18` | Synchronous active-high reset |
| `enable` | input | `SW0` | `V17` | Enable counting when high |
| `up_down` | input | `SW1` | `V16` | `1`: up; `0`: down |
| `count[0]` | output | `LD0` | `U16` | Least-significant count bit |
| `count[1]` | output | `LD1` | `E19` | Count bit 1 |
| `count[2]` | output | `LD2` | `U19` | Count bit 2 |
| `count[3]` | output | `LD3` | `V19` | Most-significant count bit |

All I/O use `LVCMOS33`. The clock constraint is 10.000 ns, corresponding to 100 MHz.

## 4. Design description

The module contains two sequential functions in one clocked process:

- **Divider counter:** counts system-clock edges from zero to `DIVISOR - 1`. The default value, `50_000_000`, creates one count event every 0.5 seconds from a 100 MHz clock.
- **4-bit data counter:** increments or decrements only when the divider reaches its terminal count.

The reset is synchronous: the input is sampled on a rising edge of `clk`. When `enable` is low, the 4-bit output holds its value and the divider is restarted. Consequently, the first count after re-enabling always occurs after a complete divider interval.

The 4-bit arithmetic intentionally wraps because only the low four bits are retained:

```text
1111 + 0001 = 0000       0000 - 0001 = 1111
```

### Module interface

```verilog
module week2_counter #(
    parameter integer DIVISOR = 50_000_000
) (
    input  wire       clk,
    input  wire       reset,
    input  wire       enable,
    input  wire       up_down,
    output reg  [3:0] count
);
```

The complete synthesizable source is in [`src/week2_counter.v`](src/week2_counter.v).

## 5. Algorithm

```text
On every rising edge of clk:
    if reset = 1:
        divider_count <- 0
        count         <- 0
    else if enable = 0:
        divider_count <- 0
        count         <- count
    else if divider_count = DIVISOR - 1:
        divider_count <- 0
        if up_down = 1: count <- count + 1
        else:            count <- count - 1
    else:
        divider_count <- divider_count + 1
        count         <- count
```

## 6. Simulation and verification

The testbench overrides `DIVISOR` with `4`, allowing the behaviour to be checked quickly. It generates a 10 ns clock and checks:

1. synchronous reset from an unknown/non-zero state to zero;
2. one and four upward count ticks;
3. holding the output while `enable = 0`;
4. restarting the divider after re-enable;
5. two downward count ticks;
6. reset from a non-zero state;
7. downward wrap `0 -> F`; and
8. upward wrap `F -> 0`.

The testbench is self-checking and prints `WEEK 2 LAB: ALL TESTS PASSED` when no check fails. Its source is [`sim/tb_week2_counter.v`](sim/tb_week2_counter.v).

### Run the simulation

From the `week-2-lab` directory, with Icarus Verilog installed:

```bash
make test
```

The optional simulation executable and waveform are written below `sim/build/`, which is ignored by Git. To remove generated simulation files:

```bash
make clean
```

## 7. Vivado implementation procedure

1. Open **Vivado** and create a new RTL project.
2. Select the Basys 3 part: `xc7a35tcpg236-1`.
3. Add `src/week2_counter.v` as a design source.
4. Add `constraints/basys3_week2_counter.xdc` as a constraints file.
5. Set `week2_counter` as the top module.
6. Run **Synthesis**, then **Implementation**, and check for critical warnings.
7. Generate the bitstream.
8. Connect the Basys 3 board and program the FPGA.
9. Set `SW0` high to enable counting. Set `SW1` high for up-counting or low for down-counting.
10. Press and release `BTNC` to reset. Observe the binary count on `LD3..LD0`.

> The pushbutton is intentionally used as a simple synchronous reset for this introductory lab. Mechanical debouncing and input synchronisation should be added for a production design.

## 8. Expected observations

| Control condition | Expected observation |
|---|---|
| `BTNC` pressed at a clock edge | LEDs show `0000` |
| `SW0 = 0` | LEDs hold their current binary value |
| `SW0 = 1`, `SW1 = 1` | Count increases once per divider interval |
| `SW0 = 1`, `SW1 = 0` | Count decreases once per divider interval |
| Up-count from `1111` | Next value is `0000` |
| Down-count from `0000` | Next value is `1111` |

For the default divisor, the visible sequence is approximately two count changes per second. A held reset keeps the output at zero because reset has priority over all other controls.

## 9. Result

A parameterised 4-bit synchronous up/down counter was described in Verilog, accompanied by a self-checking testbench and Basys 3 XDC constraints. The design meets the specified reset, enable, direction, divider, and wrap-around behaviours in simulation and is ready for Vivado synthesis and FPGA programming on the stated board.

## 10. Viva / review points

- **Why is reset called synchronous?** It affects the registers only on a rising edge of `clk`.
- **Why is `DIVISOR = 50_000_000` used?** The Basys 3 clock is 100 MHz; 50 million cycles equal 0.5 seconds.
- **What happens when enable is low?** The output count holds and the divider returns to zero.
- **Why does the counter wrap?** The output is exactly four bits wide, so overflow/underflow discards the carry/borrow.
- **Why is the testbench divisor only 4?** A reduced parameter makes the same hardware behaviour practical to simulate quickly.
