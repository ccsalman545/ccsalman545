# 10. RTL DESIGN EXPLANATION

All modules are written in strict **Verilog-2001** (no SystemVerilog constructs), because Verilog-2001 is the most portable synthesizable dialect across vendor tools. Five source files form the design:

| File | Module | Role |
|---|---|---|
| `rtl/up_down_counter_16bit.v` | `up_down_counter_16bit` | Design block 1 — the counter |
| `rtl/universal_shift_register_8bit.v` | `universal_shift_register_8bit` | Design block 2 — the shift register |
| `rtl/clock_enable_gen.v` | `clock_enable_gen` | 2 Hz tick generator for eye-visible hardware demonstration |
| `rtl/counter_top_boolean.v` | `counter_top_boolean` | Board top for the counter demo |
| `rtl/shiftreg_top_boolean.v` | `shiftreg_top_boolean` | Board top for the shift-register demo |

## 10.1 Why exactly one clocked `always` block per register bank

Every module contains a **single** `always @(posedge clk)` block. This is deliberate and follows the industry "one process per register group" guideline:

1. The block executes only on the rising clock edge, so every signal assigned inside it (`count`, `pout`, `div_cnt`, `tick`) is a **flip-flop output** — the synthesis tool infers registers, never latches. Latches only appear when a signal is assigned in a *level-sensitive* block (`always @(*)`) with an incomplete branch; there are none here.
2. Inside the block, **non-blocking assignments (`<=`)** are used exclusively. `<=` schedules the update *after* all reads of the current time step, so expressions like `count <= count + 1'b1` read the old count and register the new one — an exact model of real flip-flop behaviour. Using blocking `=` here would model a race and is a classic beginner error.
3. **Synchronous control style.** `rst`, `load`, `en` and `mode` all appear *inside* the clocked block, not in the sensitivity list. Nothing is asynchronous, so the entire design is one clock domain, and Vivado maps `rst` onto the dedicated SR pin and `en` onto the dedicated CE pin of the Spartan-7 flip-flops (FDRE primitive) at zero LUT cost.
4. **Priority by if-else nesting.** In `up_down_counter_16bit`, the `if (rst) / else if (load) / else if (en) / else` chain synthesizes to a priority mux feeding the D input: reset dominates, load overrides counting, and holding is the explicit default. Because every branch assigns `count`, the logic is complete — there is again no way to infer a latch, and the explicit `count <= count` hold branch documents intent (it costs nothing, since holding with `en`=0 is precisely what the CE pin does).
5. **Case statement in the shift register.** The four modes map onto a 4:1 mux per bit. A `default` branch (hold) is included even though all four codes are covered, which protects against X-propagation in simulation if `mode` ever goes unknown — bulletproofing recommended by the Xilinx coding guidelines (UG901).

## 10.2 Registers and signals

**`up_down_counter_16bit`:**
- `count[WIDTH-1:0]` — the only flip-flop bank (16 bits); everything else in the module is either an input or a wire.
- `max_tick`, `min_tick` — pure combinational equality decodes of `count` (continuous `assign`), costing approximately one LUT each and giving the module clean cascade/overflow semantics.
- Localparams `ALL_ONES`/`ALL_ZEROS` are built with replication (`{WIDTH{1'b1}}`) so the code is correct for any `WIDTH`.

**`universal_shift_register_8bit`:**
- `pout[WIDTH-1:0]` — the only register bank (8 bits).
- `sout_l = pout[WIDTH-1]`, `sout_r = pout[0]` — combinational taps of the two end flip-flops for cascading and for testbench observability.
- Mode encodings are `localparam`s (`MODE_HOLD`, `MODE_RIGHT`, `MODE_LEFT`, `MODE_LOAD`) so the case statement is self-documenting; the encodings match the 74x194 datasheet, which is the historical reference for universal shift registers.

**`clock_enable_gen`:**
- `div_cnt[31:0]` + `tick` — a classic terminal-count strobe: when `div_cnt` reaches `DIVISOR−1` it reloads to 0 and emits a single-cycle pulse. Feeding this pulse into the counter's `en` input slows the *effective* count rate to 2 Hz **without dividing the clock** — every flip-flop in the design still runs on the same 100 MHz net through a single BUFG, so there are no derived-clock, skew orAsync crossing issues.

## 10.3 Parameterization

Both DUTs take a `WIDTH` parameter (16 and 8 by default). All internal expressions — replications, part-selects `pout[WIDTH-1:1]`, `pout[WIDTH-2:0]` — are written in terms of `WIDTH`, so the same source instantly yields counters/shift registers of any width. The testbenches instantiate with the default widths. Instantiation is done with **named port connections** (`.clk(clk), …`), which is the style required for readable, review-safe hierarchical designs.

## 10.4 Top-level modules

The two top modules contain no new *function*; they are structural glue: they instantiate the DUT, the tick generator, and map board signals (`sw`, `btn`, `led`) onto DUT ports. In `shiftreg_top_boolean` the user-selected mode is applied only while the tick is active (`mode = slow_tick ? sw[1:0] : 2'b00`), so each switch-selected operation advances exactly once every 0.5 s and the register holds in between — the whole behaviour is observable by eye on the LEDs, yet the circuit remains fully synchronous.

---

<!-- page break -->

---

# 11. VERILOG CODE

## 11.1 `up_down_counter_16bit.v`

{{FILE:rtl/up_down_counter_16bit.v}}

## 11.2 `universal_shift_register_8bit.v`

{{FILE:rtl/universal_shift_register_8bit.v}}

## 11.3 `clock_enable_gen.v` (hardware-demo support)

{{FILE:rtl/clock_enable_gen.v}}

## 11.4 `counter_top_boolean.v` (board top — counter demo)

{{FILE:rtl/counter_top_boolean.v}}

## 11.5 `shiftreg_top_boolean.v` (board top — shift-register demo)

{{FILE:rtl/shiftreg_top_boolean.v}}

---

<!-- page break -->

---

# 12. SELF-CHECKING TESTBENCHES

Both testbenches follow the same professional pattern:

1. **Clock generation** — `always #(CLK_PERIOD/2) clk = ~clk;` produces the 100 MHz reference.
2. **Stimulus on the inactive edge** — inputs are changed only at `@(negedge clk)`, so every value presented to the DUT is settled well before the rising edge, imitating the setup behaviour of a real source register and eliminating races between stimulus and sampling.
3. **Automatic checking tasks** — `check_count` / `check_flag` / `check_reg` / `check_bit` compare DUT outputs with expected values using case-inequality (`!==`, which also catches X/Z), print a time-stamped PASS/FAIL line, and keep running totals in `total` / `errors`.
4. **`step_and_check` task** — advances one rising edge and checks in a single call, keeping the stimulus readable as a sequence of named test steps (T01…T12 / T01…T09).
5. **Waveform dump** — `$dumpfile`/`$dumpvars` record the full hierarchy; in Vivado all signals are also available in the built-in waveform viewer.
6. **Automatic termination** — after the summary (`>>> OVERALL RESULT : PASS <<<`), `$finish` ends the run without human interaction; a watchdog `initial` block aborts deadlocked simulations.
7. **Full coverage of every mode:**
   - *Counter:* reset, hold, load, load-priority-over-enable, up, down, overflow FFFF→0000, underflow 0000→FFFF, reset-priority-over-load, mid-stream direction reversal, and a complete **65,536-count full-range sweep**.
   - *Shift register:* reset, parallel load, hold with toggling serial inputs, shift-right pattern, shift-left pattern (including an exact round-trip 0xA5 → … → 0xA5), reset dominating the mode field, an 8-step **walking-1**, an 8-step **ones-fill**, and a serial-output-drain test with `sout_l`/`sout_r` checks.

## 12.1 `tb_up_down_counter_16bit.v`

{{FILE:tb/tb_up_down_counter_16bit.v}}

## 12.2 `tb_universal_shift_register_8bit.v`

{{FILE:tb/tb_universal_shift_register_8bit.v}}

---

<!-- page break -->

---

# 13. EXPECTED WAVEFORMS AND SIMULATION RESULTS

Times are in ns; the clock has a 10 ns period with rising edges at 5, 15, 25, … All DUT updates therefore appear one clock period after the inputs are established.

## 13.1 Counter — reset, load, count up, hold

```
ns:      0    10    20    30    40    50    60    70    80    90   100   110
         |     |     |     |     |     |     |     |     |     |     |     |
clk      ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
         └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
rst      ----─────────┐
                      └────────────────────────────────────────────
load     --------------------┐      ┌────┐
                             └──────┘    └────────────────────────
din      ================  1234 ==== ABCD ========================
en       ------------------------------┐                  ┌──────
                                       └──────────────────┘
up_n_down=============================================================
count    0000 0000 0000 0000 1234 1234 ABCD ABCD ABCE ABCF ABD0 ABD1 ...
                   (T01) (T02) (T03) (T04) (T05a..T05e: +1 each edge)
```

Reading: T01 the two reset edges clear `count`; T02 with all controls idle the value holds; T03 the first edge with `load`=1 captures 0x1234; T04 load dominates `en` and 0xABCD is captured; T05 five enabled edges count 0xABCE…0xABD2; T06 with `en`=0 the value freezes at 0xABD2.

## 13.2 Counter — overflow (FFFF → 0000) and underflow (0000 → FFFF)

```
load=1,din=FFFE ──┐
                  v
count    ... FFFC FFFD [FFFE] FFFF 0000 0001   ...   0002 [0001] 0000 FFFF FFFE
                              T08a  T08b T08e               T09a  T09b T09e
max_tick 0    0    0     0    1    0    0
min_tick 0    0    0     0    0    0    0
                                          (and symmetrically min_tick=1 at 0000)
```

At 0xFFFF with `en`=1 and `up_n_down`=1, one more edge rolls the counter to 0x0000 — `max_tick` is high exactly during the terminal state, so a following stage can use it as its enable. The mirror image occurs at 0x0000 when counting down, flagged by `min_tick`.

## 13.3 Shift register — load, shift right, shift left

```
clock edge:     1      2      3      4      5      6      7      8      9
mode        11(LOAD) 01 R   01 R   01 R   01 R   10 L   10 L   10 L   10 L
sin_r           X      1      0      1      1      —      —      —      —
sin_l           —      —      —      —      —      0      1      0      1
pout        10100101 11010010 01101001 10110100 11011010 10110100 01101001 ...
pout(hex)     A5      D2      69      B4      DA      B4      69      D2 → A5
sout_l          1      1      0      1      1      1      0      1      1
sout_r          1      0      1      0      0      0      1      0      1
```

After the four right shifts and four left shifts with the complementary serial patterns the register returns to 0xA5 — a strong self-consistency signature that the testbench checks explicitly ("round trip"). During HOLD edges (mode=00, not drawn) all `pout` waveforms are flat regardless of `sin_r`, `sin_l` or `pin`.

## 13.4 Expected simulation console transcripts

The transcripts below are the exact PASS lines the testbenches produce (verified independently against a cycle-accurate reference model of the RTL; XSim prints identical content with `%0t` in ns).

**Counter testbench (abbreviated — the full log contains 65,573 PASS lines):**

```
==============================================================
 TESTBENCH : tb_up_down_counter_16bit  (100 MHz clock)
==============================================================
[6] PASS : T01a: rst clears counter | count = 0x0000
[16] PASS : T01b: rst held, counter stays 0 | count = 0x0000
[26] PASS : T02: hold after reset release | count = 0x0000
[36] PASS : T03: load 0x1234 | count = 0x1234
[46] PASS : T04: load wins over count-up request | count = 0xABCD
[56] PASS : T05a: up-count 1 | count = 0xABCE
[66] PASS : T05b: up-count 2 | count = 0xABCF
[76] PASS : T05c: up-count 3 | count = 0xABD0
[86] PASS : T05d: up-count 4 | count = 0xABD1
[96] PASS : T05e: up-count 5 | count = 0xABD2
[106] PASS : T06a: hold 1 | count = 0xABD2
[116] PASS : T06b: hold 2 | count = 0xABD2
[126] PASS : T06c: hold 3 | count = 0xABD2
[136] PASS : T07a: down-count 1 | count = 0xABD1
[146] PASS : T07b: down-count 2 | count = 0xABD0
[156] PASS : T07c: down-count 3 | count = 0xABCF
[166] PASS : T08a: load 0xFFFE | count = 0xFFFE
[176] PASS : T08b: count reaches terminal 0xFFFF | count = 0xFFFF
  ... (T08/T09 flag checks, T09 rollover-underflow, T10 reset
       dominance, T11 direction reversal, and the 65535 checks
       of the full-range sweep T12 — all PASS) ...
[286] PASS : T11f: reverse again, up to 8 | count = 0x0008
[296] PASS : T12a: reset before sweep | count = 0x0000
[655646] PASS : T12b: max_tick at end of sweep (0xFFFF) | flag = 1
[655656] PASS : T12c: sweep wraps to 0 after 65536 counts | count = 0x0000
==============================================================
 SUMMARY : 65573 checks executed, 0 error(s) detected
 >>> OVERALL RESULT : PASS <<<
==============================================================
```

**Shift-register testbench (abbreviated — 51 checks, 0 errors):**

```
==============================================================
 TESTBENCH : tb_universal_shift_register_8bit  (100 MHz clock)
==============================================================
[6] PASS : T01a: rst clears register | pout = 00000000 (0x00)
[16] PASS : T01b: rst held, register stays 0 | pout = 00000000 (0x00)
[26] PASS : T02a: load 0xA5 | pout = 10100101 (0xA5)
[36] PASS : T03a: hold 1 (sin = 1,1) | pout = 10100101 (0xA5)
[46] PASS : T03b: hold 2 (sin = 0,1) | pout = 10100101 (0xA5)
[56] PASS : T03c: hold 3 (even pin ignored) | pout = 10100101 (0xA5)
[66] PASS : T04b: shift right 1 -> 0xD2 | pout = 11010010 (0xD2)
[76] PASS : T04c: shift right 2 -> 0x69 | pout = 01101001 (0x69)
[86] PASS : T04d: shift right 3 -> 0xB4 | pout = 10110100 (0xB4)
[96] PASS : T04e: shift right 4 -> 0xDA | pout = 11011010 (0xDA)
[106] PASS : T05b: shift left 1 -> 0xB4 | pout = 10110100 (0xB4)
[116] PASS : T05c: shift left 2 -> 0x69 | pout = 01101001 (0x69)
[126] PASS : T05d: shift left 3 -> 0xD2 | pout = 11010010 (0xD2)
  ... (round-trip to 0xA5, reset dominance, walking-one 0x02→0x80→0x00,
       ones-fill 0x01→0xFF, serial-drain 0x7F→0x00 with sout checks) ...
[386] PASS : T09h: shift right -> 0x03 | pout = 00000011 (0x03)
[396] PASS : T09i: shift right -> 0x01 | pout = 00000001 (0x01)
[406] PASS : T09j: shift right -> 0x00 (register empty) | pout = 00000000 (0x00)
==============================================================
 SUMMARY : 51 checks executed, 0 error(s) detected
 >>> OVERALL RESULT : PASS <<<
==============================================================
```

---

<!-- page break -->

---

# 14. VIVADO SIMULATION PROCEDURE

1. **Create the project.** Open Vivado → *Create Project* → name it `week3_counters_shift_registers` → *RTL Project* (do not check "Do not specify sources"). When asked for the part, select the Boolean board part **xc7s50csga324-1** (or choose the "Boolean" entry under the Boards tab if board files are installed).
2. **Add design sources.** *Add Sources → Add or create design sources → Add Files* → select all files in `rtl/`. Verify that the *Design Sources* hierarchy shows `counter_top_boolean` and `shiftreg_top_boolean` as candidate tops.
3. **Add simulation sources.** *Add Sources → Add or create simulation sources → Add Files* → select both files in `tb/`. They appear under *Simulation Sources → sim_1*.
4. **Add constraints.** *Add Sources → Add or create constraints → Add Files* → select `constraints/boolean_board.xdc`.
5. **Select the simulation top.** In *Simulation Sources*, right-click `tb_up_down_counter_16bit` → *Set as Top* (repeat later for the other testbench).
6. **Run behavioral simulation.** *Flow Navigator → Simulation → Run Simulation → Run Behavioral Simulation*. XSim elaborates, compiles and runs; the transcript prints the PASS/FAIL lines and the simulation stops by itself at `$finish`.
7. **View waveforms.** In the *Scope* window, expand `dut`; select internal signals (e.g. `dut/count`, `dut/max_tick`) → right-click → *Add to Wave Window*. For the counter sweep, place the cursor near the interesting region and use *Zoom Fit*; add `count` and `pout` as **Hex** radix (right-click the name → *Radix → Hexadecimal*).
8. **Measure with markers.** Drag a marker to a rising edge and a second marker one period later to confirm the 10 ns period; verify that `count` increments exactly 10 ns after the enable request.
9. **Interpret results.** Confirm all log lines read `PASS` and the final line reads `>>> OVERALL RESULT : PASS <<<`. Match the waveform against the expected ASCII timing diagrams of Section 13 — load event at 30 ns, overflow event at 180 ns, etc.
10. **Re-run for the second DUT.** Change the simulation top to `tb_universal_shift_register_8bit` and relaunch; confirm 51 checks, 0 errors.
11. **(Optional) Post-synthesis timing simulation.** After synthesis: *Run Simulation → Run Post-Synthesis Timing Simulation* to observe propagation delays on the routed model.

---

<!-- page break -->

---
