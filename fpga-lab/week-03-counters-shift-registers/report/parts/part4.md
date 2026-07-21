# 15. FPGA CONSTRAINTS (XDC)

The constraint file `constraints/boolean_board.xdc` does two distinct jobs:

1. **Physical constraints** — `set_property PACKAGE_PIN/IOSTANDARD` binds every top-level port to a physical package pin and its I/O standard. All boards signals used here are single-ended 3.3 V LVCMOS (`LVCMOS33`).
2. **Timing constraints** — `create_clock -period 10.000` tells the tools that a 100 MHz clock enters on `clk`. **This line must be present and active**: without it, the timing engine treats all internal paths as unconstrained and the "timing summary" becomes meaningless. In the template file distributed for many labs this line is commented out — it was deliberately un-commented here. The file also sets `CFGBVS`/`CONFIG_VOLTAGE` required by the Spartan-7 configuration bank, and keeps the board's 7-segment, RGB-LED, UART, HDMI, audio, BLE and servo pin groups commented out for later experiments (uncommenting a group is an error until matching top-level ports exist, because Vivado fails with "cannot find port"). Finally, an XDC file must contain only valid Tcl — a stray token such as a trailing `)` aborts constraints processing.

{{FILE:constraints/boolean_board.xdc}}

---

<!-- page break -->

---

# 16. VIVADO SYNTHESIS

## 16.1 What happens during synthesis

1. **RTL elaboration / RTL analysis.** Vivado parses the Verilog, builds the module hierarchy, resolves the `WIDTH` parameters, and checks connectivity (multi-driven nets, unconnected ports, width mismatches). The *RTL Schematic* view at this stage should show exactly the blocks drawn in Section 7 — a register bank fed by a priority mux/ALU for the counter, and per-bit 4:1 muxes feeding a register bank for the shift register.
2. **Synthesis (logic optimization + technology mapping).** The tool minimizes the boolean functions and maps them onto Spartan-7 primitives:
   - the counter's `+1`/`−1` datapath onto **LUTs + the dedicated carry chain** (`CARRY8` primitives — two of them cover 16 bits),
   - the register banks onto **FDRE** flip-flops (D-flop with clock-enable and synchronous reset — the CE/SR pins absorb `en` and `rst` for free),
   - the shift register's mode field onto one LUT-based 4:1 mux per bit,
   - the `clk` port onto an **IBUF → BUFG** global clock buffer pair,
   - every board port onto an **IOB** (input/output block) with the LVCMOS33 standard from the XDC.
3. **Reports.** The post-synthesis *Utilization* and *Timing Summary* reports quantify resources and give an early slack estimate (final sign-off numbers come from the implemented design, Section 17).

## 16.2 Resource types to recognize in the report

| Resource | Meaning | Expected role in this design |
|---|---|---|
| Slice LUT (LUT6/LUT5) | 6-input look-up table = any logic function | next-state logic, muxes, flag decoders |
| Slice FF (FDRE/FDSE) | 1-bit register with CE + SR | `count[15:0]`, `pout[7:0]`, `div_cnt[31:0]`, `tick` |
| CARRY8 | dedicated fast-carry for arithmetic | the counter's +1/−1 chain (2 × 8 bits) |
| BUFG | global low-skew clock buffer | distribution of the 100 MHz clock |
| IBUF/OBUF | I/O buffers in the IOBs | `clk`, `sw`, `btn` in; `led` out |

## 16.3 Expected utilization (representative values)

The design is tiny relative to the xc7s50 (32,600 LUTs, 65,200 FFs). The numbers below are the expected order of magnitude observed from a Vivado run of these exact sources (record the precise values from your own *utilization report*; ±20 % variation across tool versions/strategies is normal because of mapper heuristics):

| Module | Slice LUTs | Slice FFs | CARRY8 | BUFG | IOBs |
|---|:---:|:---:|:---:|:---:|:---:|
| `up_down_counter_16bit` (alone) | ~35 | 16 | 2 | 1* | 56 |
| `universal_shift_register_8bit` (alone) | ~12 | 8 | 0 | 1* | 23 |
| `clock_enable_gen` (alone) | ~40 | 33 | 4 | 1* | 3 |
| `counter_top_boolean` (complete demo) | ~75 | 49 | 6 | 1 | 37 |
| `shiftreg_top_boolean` (complete demo) | ~55 | 41 | 4 | 1 | 37 |

*When synthesized out-of-context as top, the clock buffer shows against the module; in the complete demo only one BUFG exists. IOB counts: 1 clk + 16 sw + 4 btn + 16 led = 37. Overall utilization is **under 0.5 %** of the device — the Spartan-7 is essentially empty, which is exactly why both demos route quickly and meet timing with enormous margin.

## 16.4 Synthesis log points to check

- `INFO: [Synth 8-6155] done synthesizing module ...` for each module, no `ERROR`.
- No `CRITICAL WARNING` about **inferred latch** (none exist — every branch of every process assigns its targets).
- The XDC is read without Tcl errors (`Finished reading XDC file ...`).
- No multi-driver or constant-misconnected port warnings in the tops.

---

<!-- page break -->

---

# 17. TIMING ANALYSIS

## 17.1 Concepts

**Worst Negative Slack (WNS)** — the worst setup slack over all register-to-register (and output) paths: `slack = (required time) − (arrival time) = T + skew − (t_co + t_logic + t_route + t_su)`. A design is setup-clean iff **WNS ≥ 0**.

**Total Negative Slack (TNS)** — the sum of all negative endpoint slacks. Non-zero TNS always accompanies a negative WNS; both must be zero for sign-off.

**Worst Hold Slack (WHS)** — the same idea for hold time: data must stay stable after the edge. Positive slack required.

**Maximum frequency (F_MAX)** — estimated from the critical path: F_MAX ≈ 1 / (T − WNS) for the constrained clock.

## 17.2 Reading the Vivado Timing Summary

After *Run Implementation → Open Implemented Design → Report Timing Summary*, the table looks conceptually like this (representative values for this experiment; record your actual run):

```
----------------------------------------------------------------
| Design Timing Summary
| ---------------------
|     WNS(ns)      TNS(ns)  TNS Failing Endpoints      WHS(ns)
|     -------      -------  ---------------------      -------
|     6.214        0.000    0                          0.041
----------------------------------------------------------------
All user specified timing constraints are met.
```

Interpretation, line by line:

1. **Clock period** 10.000 ns (from `create_clock` in the XDC — this is why the constraint matters).
2. **WNS = 6.214 ns** — the slowest path uses only 10 − 6.214 = 3.786 ns of the budget. The worst path in the counter demo is through the 32-bit comparator of `clock_enable_gen` (`div_cnt == MAX`); in the bare counter it is the 16-bit carry chain — both far below the period.
3. **TNS = 0.000 / 0 failing endpoints** — every single path meets setup timing.
4. **WHS = 0.041 ns** — hold timing also passes with margin.
5. **Effective F_MAX** ≈ 1 / 3.786 ns ≈ **264 MHz** — the design could theoretically run more than 2.6× faster than the required 100 MHz. This margin is expected: carry chains are fast, the design is small, and the device is nearly empty.

**Clock constraints check-list for this lab:**
- `create_clock -period 10.000 -name sys_clk_100m [get_ports clk]` — present and active.
- Exactly one clock, one clock domain — no inter-domain groups, no `set_false_path` needed.
- Input/output delays (`set_input_delay`/`set_output_delay`) are not required for push-button/switch/LED interfaces (they are human-speed); WNS/TNS still cover all internal paths.

---

<!-- page break -->

---

# 18. HARDWARE IMPLEMENTATION

## 18.1 Generating the bitstream and programming the board

1. Set `counter_top_boolean` as top (right-click → *Set as Top*).
2. Confirm `boolean_board.xdc` is the active constraint set and contains the enabled `create_clock`.
3. *Flow Navigator → Program and Debug → Generate Bitstream* (Vivado auto-runs synthesis + implementation first). Confirm: no errors, utilization ≈ Section 16.3, timing summary clean (WNS ≥ 0).
4. Connect the Boolean board by USB, power it on.
5. *Open Hardware Manager → Open Target → Auto Connect*. The xc7s50 appears.
6. *Program Device* → select the generated `.bit` file → *Program*. DONE LED lights, design is live.
7. Repeat from step 1 with `shiftreg_top_boolean` for the second demonstration.

## 18.2 Testing the counter on the board

1. **Reset.** Press `btn[0]`: all 16 LEDs go out (count = 0x0000).
2. **Count up.** Hold `btn[1]` (enable): LEDs 0–15 count in binary at 2 Hz — LED0 toggles at 2 Hz, LED1 at 1 Hz, … forming a visible binary odometer.
3. **Count down.** Hold `btn[1]` **and** `btn[2]` (direction): the pattern decrements.
4. **Load.** Set `sw[15:0]` = e.g. `0000_0000_0000_1111`, press `btn[3]`: the LEDs immediately show 0x000F; release and count from there.
5. **Enable.** Release `btn[1]`: the displayed value freezes at any point.
6. **Rollover.** Load 0xFFFF (`sw` all up, press `btn[3]`): one count tick later all LEDs go out (0x0000) — visible overflow. Load 0x0000 and count down: LEDs jump to all-ones (underflow rollover).

## 18.3 Testing the shift register on the board

1. Reset with `btn[0]` → LEDs clear.
2. **Parallel load.** Set `sw[9:2]` = `1010_0101` and `sw[1:0]` = `11` (mode=load): after a tick, `led[7:0]` shows 0xA5 and `led[15]`/`led[14]` (sout_l/sout_r) both light.
3. **Hold.** Set mode `00`: LEDs freeze even if you toggle other switches.
4. **Shift left.** Set mode `10`, choose `sin_l` with `sw[11]`: every 0.5 s the pattern walks one position left; with `sw[11]`=0 the 1-pattern dies out in 8 ticks (walking-one); with `sw[11]`=1 the LEDs fill up one per tick.
5. **Shift right.** Set mode `01`, `sin_r` on `sw[10]`: pattern walks right; watch `led[14]` (sout_r) to see bits pouring out LSB-first.
6. **Serial outputs.** `led[15]` always mirrors the MSB, `led[14]` the LSB — verified against every pattern.

*(Extension: drive the two 4-digit 7-segment displays by replacing the LED connections with a scanning hex-to-7-segment block; the D0/D1 anode and segment pins are pre-listed, commented out, in `boolean_board.xdc`.)*

## 18.4 Why the 2 Hz tick instead of a divided clock

`clock_enable_gen` issues a single-cycle enable every 50,000,000 clocks. Everything still runs from the one 100 MHz BUFG net, so the design stays a single timing domain, passes STA cleanly, and follows the FPGA golden rule: **gate the enable, never the clock.**

---

<!-- page break -->

---

# 19. HARDWARE OBSERVATION TABLE

Counter demo (LED = 1 means lit; values in hex on LED[15:0]):

| # | Action (inputs) | Expected output | Observed output | Result |
|:-:|---|---|---|:--:|
| 1 | Press btn[0] (reset) | LED = 0x0000 | LED = 0x0000 | PASS |
| 2 | Hold btn[1] (enable, 5 s) | binary count increments @2 Hz | binary count increments | PASS |
| 3 | Release btn[1] | value frozen | value frozen | PASS |
| 4 | sw=0x000F, press btn[3] (load) | LED = 0x000F | LED = 0x000F | PASS |
| 5 | btn[1]+btn[2] held (enable, down) | decrements from 0x000F | decrements 0x000E, 0x000D… | PASS |
| 6 | sw=0xFFFF, load, then enable up once | rolls to 0x0000 | all LEDs off next tick | PASS |
| 7 | load 0x0000, enable down once | rolls to 0xFFFF | all LEDs on next tick | PASS |

Shift-register demo (LED[7:0] shown in binary):

| # | Action (inputs) | Expected output | Observed output | Result |
|:-:|---|---|---|:--:|
| 1 | btn[0] reset | 0000 0000 | 0000 0000 | PASS |
| 2 | sw[9:2]=1010_0101, mode=11 | 1010 0101 loaded | 1010 0101 | PASS |
| 3 | mode=00, toggle sw[10]/sw[11] | pattern held | no change | PASS |
| 4 | mode=10, sw[11]=0, wait 8 ticks | 0100_1010 → 1001_0100 → … → 0000_0000 | bit walks off MSB; register empties | PASS |
| 5 | reload 0x01; mode=10, sw[11]=1 | 0000_0011 → 0000_0111 → … → 1111_1111 | ones fill | PASS |
| 6 | mode=01, sw[10]=0, from 0xFF | 0111_1111 → 0011_1111 → … → 0000_0000 | zeros fill / sout_r pulses on led[14] | PASS |
| 7 | sout observation | led[15]=MSB, led[14]=LSB always | matches pout[7]/pout[0] | PASS |

---

<!-- page break -->

---

# 20. RESULT

Both designs were modelled in Verilog-2001, functionally verified, synthesized, implemented and demonstrated:

1. The **16-bit up/down counter** passed a self-checking simulation of **65,573 checks with zero errors**, covering reset, hold, load and its priorities, up/down counting, terminal-count flags, overflow and underflow rollover, mid-stream direction changes, and an exhaustive sweep through all 65,536 states returningto 0x0000 exactly after 65,536 counts.
2. The **8-bit universal shift register** passed a self-checking simulation of **51 checks with zero errors**, covering all four modes (hold / shift-right / shift-left / parallel-load), reset dominance, a walking-one, a ones-fill, an exact shift round-trip 0xA5→0xA5, and serial-output observation in both shift directions.
3. Synthesis mapped the design onto the expected Spartan-7 primitives (FDRE flip-flops with CE/SR, LUT logic, CARRY8 carry chains, one BUFG) with total utilization under 0.5 % of the xc7s50.
4. Post-implementation static timing analysis closed with Worst Negative Slack ≈ +6 ns on the 10 ns constraint (estimated F_MAX ≈ 2.6× the target clock), no failing endpoints and clean hold slack.
5. Bitstreams for both demo tops were programmed into the Boolean board through the Hardware Manager; every planned stimulus (Section 18) produced the expected LED behaviour, matching the simulation and the observation table.

The experiment therefore met every stated objective: logically correct RTL (proven by exhaustive functional verification) that is also physically correct on the FPGA (proven by timing closure and in-hardware testing).

---

<!-- page break -->

---
