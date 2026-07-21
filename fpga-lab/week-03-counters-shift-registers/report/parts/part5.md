# 21. ADVANTAGES

1. **Fully synchronous single-clock design** — one BUFG, one timing domain, trivially analyzable by static timing analysis and free of clock-domain-crossing hazards.
2. **Synchronous reset/load/enable map onto dedicated flip-flop control pins (SR/CE)** — zero LUT cost for control logic.
3. **Predictable, race-free behaviour** — non-blocking assignments model true flip-flop semantics; simulation and silicon agree.
4. **No latches inferred** — complete branch coverage and explicit hold branches keep the design latch-free, avoiding simulation/synthesis mismatch.
5. **Parameterized width** — one source becomes a counter/shift register of any width by changing `WIDTH`.
6. **Cascadeable** — `max_tick`/`min_tick` and `sout_l`/`sout_r` allow direct chaining into wider counters/registers.
7. **Overflow/rollover signalling** — terminal-count flags turn the plain counter into a timer/overflow detector.
8. **Priority-encoded controls are unambiguous** — rst > load > en gives deterministic behaviour under simultaneous requests (verified by T04 and T10).
9. **Reusable across projects** — the two modules are drop-in IP-style blocks (timers, UARTs, LED drivers) for later labs.
10. **Efficient FPGA mapping** — arithmetic collapses into CARRY8 carry chains; the whole demo uses <0.5 % of the device.
11. **Self-checking verification** — the testbenches need no human waveform inspection to give a verdict; they scale from smoke tests to the 65 k-state sweep.
12. **Simulation speed and cleanliness** — behavioural RTL simulates the entire 65,536-count sweep in milliseconds with clean, human-readable logs.
13. **Hardware-observable** — the tick generator produces eye-visible operation without creating a second clock domain, demonstrating correct engineering practice.
14. **Deterministic timing closure** — measured slack ≈ +6 ns on a 10 ns budget → robust against temperature/voltage variation on the bench.
15. **Portable Verilog-2001** — compiles unchanged in Vivado, Quartus, Icarus, Yosys-class flows.
16. **Readable and maintainable** — named port connections, localparams for modes, and heavy commenting make the code review- and viva-proof.

---

# 22. DISADVANTAGES AND LIMITATIONS

1. **Human-interface signals are not debounced/synchronized.** Push-buttons bounce for milliseconds; for the level-style uses here it is harmless, but no two-flop synchronizer or debounce filter is included in this lab's tops.
2. **Fixed 2ⁿ modulus.** A plain binary counter cannot count, say, 0..999 without extra decode/clear logic (a BCD or modulo-N variant is then needed).
3. **Hold mode wastes no power.** Every clock edge still toggles the clock network; clock gating for power was deliberately avoided (it would hurt timing quality) — a deliberate trade-off.
4. **Tick generator overhead.** The 32-bit prescaler (~33 FFs + comparator) is larger than the DUTs themselves; on resource-critical designs a slower board clock or an enable at a coarser granularity would be cheaper.
5. **Overflow is silent.** The plain counter wraps around; an application needing saturation ("stop at max") or an overflow alarm must add logic.
6. **No glitch filtering on mode switches.** Changing `mode` precisely at a tick edge can apply a half-intended operation; benign here, but relevant in precision systems.
7. **Display bandwidth wasted.** The design shows data on raw LEDs only; a scanned 7-segment interface (extra multiplexing logic) is needed for decimal readout.
8. **Parameters are static.** `WIDTH` and `DIVISOR` are compile-time constants; changing the rate or width requires re-synthesis, not a run-time register write.
9. **Serial inputs are unsynchronized external signals.** `sin_r`/`sin_l` from switches are asynchronous to the 100 MHz domain; industrial practice adds synchronizers.
10. **Testbench ≠ formal proof.** The sweep covers all states of this 16-bit counter, but for parameterized/future variants directed tests must be re-planned; formal verification would generalize the guarantee.
11. **Fine-grained portability of timing numbers.** Slack figures are device/speed-grade specific; moving to another device re-opens timing closure work.

---

# 23. APPLICATIONS

**Counters**

1. Frequency dividers and clock managers (divide 100 MHz down to audio/UI rates).
2. Baud-rate generators for UART/SPI/I²C engines.
3. Interval timers, periodic-interrupt timers and watchdog timers in embedded SoCs.
4. Event/pulse counters — tachometers, geiger counters, production-line counting.
5. PWM duty-cycle generation for motor/LED dimming (the Boolean board servo pins use exactly this).
6. Address sequencing for FIFO buffers, ring buffers and framebuffer line addressing.
7. Digital period/frequency measurement instruments.
8. Refresh controllers for DRAM, and row/column scanners for multiplexed 7-segment displays.
9. Test-pattern and pseudo-noise sequence timing in communication testers.
10. Position/angle tracking from incremental (quadrature) encoders in robotics — an up/down counter is exactly the decode output stage.

**Shift Registers**

11. UART/SPI/I²S serial-parallel conversion (PISO receiver, SIPO transmitter).
12. LED chasers, bar-graph effects, and scanned display/keyboard matrices.
13. Linear feedback shift registers (LFSR) for pseudo-random numbers, CRC checkers and scramblers.
14. Data delay lines and deskew elements in high-speed interfaces.
15. Ring/Johnson counters for multi-phase control and decade division.
16. Fixed multiplication/division by powers of two (logical/arithmetic shifts in ALUs).
17. Pattern/sequence detection — preamble and sync-word detection in receivers.
18. Barcode/magnetic-stripe serial stream decoding.
19. I/O expansion — driving many outputs (relays, 7-seg cathodes) through 74HC595-style chains from few pins.
20. JTAG/boundary-scan chains — literally giant shift registers for board test.

**FPGA / embedded context**

21. Timer/counter peripherals inside soft-core (MicroBlaze/RISC-V) SoCs.
22. Debounce + one-shot circuits built from counter comparators.
23. Traffic-light/vending-machine FSM sequencing where counters provide dwell timing.
24. Hardware accelerators — loop counters and bit-serial multipliers (shift-and-add).
25. Teaching/verification platforms: these two blocks are the canonical first self-checked designs on which larger UART, VGA and processor labs build.

---

<!-- page break -->

---

# 24. VIVA QUESTIONS AND ANSWERS

**Q1. What is a sequential circuit?**
A circuit whose outputs depend on present inputs **and** on stored state (history), maintained in flip-flops. It possesses memory; counters and shift registers are examples.

**Q2. Combinational vs sequential — the key difference?**
Combinational logic has no memory and no clock: output = f(present inputs). Sequential logic adds state: output = f(present inputs, present state), advancing on clock edges per a next-state rule.

**Q3. Why use a synchronous counter instead of a ripple counter?**
In a ripple counter each flop is clocked by the previous one, so delays accumulate and transient wrong codes appear at the output. A synchronous counter clocks all flops simultaneously from one net; delay is one flop plus one level of next-state logic, width-independent — and it is the only style that FPGA timing tools and clock trees are built around.

**Q4. Why non-blocking assignments (`<=`) in clocked always blocks?**
`<=` schedules updates after all evaluations in the time step, so every RHS reads pre-edge values — exactly like real flip-flops. Blocking `=` updates immediately and can create order-dependent races and simulation/synthesis mismatch.

**Q5. What is the difference between synchronous and asynchronous reset?**
Asynchronous reset acts instantly (in the sensitivity list: `always @(posedge clk or posedge rst)`) and needs recovery/removal timing closure; synchronous reset is only sampled at the clock edge, keeping the design single-domain, and it maps onto the dedicated SR pin of 7-series flip-flops with no LUT cost. This lab uses synchronous reset.

**Q6. What priority order did you implement among reset, load and enable, and why?**
rst > load > en. Reset must always win (safety/initialization), load must override counting so a programmer can preset regardless of enable, and enable gates only normal counting.

**Q7. What is rollover, and how is it detected?**
Rollover is the modulo wrap: up-counter FFFF→0000, down-counter 0000→FFFF. It is predicted by the terminal states: `max_tick` (count==FFFF, imminent upward rollover) and `min_tick` (count==0000, imminent downward rollover), i.e., simple equality decoders.

**Q8. What is a clock enable, and why is it better than gating the clock?**
A clock enable keeps the clock running and simply tells the flip-flops whether to accept a new value (CE pin). Gating the clock creates skew, glitch and timing-analysis problems on dedicated clock networks; the enable costs zero fabric. Our 2 Hz visible rate is produced with an enable tick, not a divided clock.

**Q9. Show how a 16-bit up/down counter rolls over.**
Up: …0xFFFE, 0xFFFF (max_tick=1), 0x0000. Down: …0x0001, 0x0000 (min_tick=1), 0xFFFF. The wrap is automatic because the incrementer/decrementer is only 16 bits wide.

**Q10. What are the four modes of a universal shift register?**
Hold (00), shift right (01), shift left (10), parallel load (11) — the 74x194 convention.

**Q11. Why does a universal shift register need two serial inputs and two serial outputs?**
Because it shifts both ways: right shifts inject at the MSB (`sin_r`) and eject the LSB (`sout_r`); left shifts inject at the LSB (`sin_l`) and eject the MSB (`sout_l`). The two outputs also let devices chain into wider registers without losing bits.

**Q12. What are SISO, SIPO, PISO and PIPO?**
Serial-in serial-out (delay line), serial-in parallel-out (receiver/deserializer), parallel-in serial-out (transmitter/serializer), parallel-in parallel-out (storage/pipeline register). The universal register can emulate all four.

**Q13. How is a ring counter different from a Johnson counter?**
Both are shift registers with feedback. Ring feeds sout straight back: n states (one circulating 1). Johnson feeds back the **inverted** sout: 2n states, easily decoded with 2-input gates.

**Q14. What does the 4:1 mux per bit in the shift register do?**
It selects the D input of each flip-flop from four candidates — own bit (hold), right neighbour (shift right), left neighbour (shift left), or the parallel input (load) — under control of the 2-bit mode field.

**Q15. What is setup time?**
The minimum time data must be stable **before** the active clock edge for guaranteed capture.

**Q16. What is hold time?**
The minimum time data must remain stable **after** the active clock edge.

**Q17. What is clock-to-Q (propagation delay of a flip-flop)?**
The delay from the active clock edge until the new value is valid at Q; together with logic, routing and setup time it fills the clock-period budget.

**Q18. What is clock skew?**
The difference in arrival times of the same clock edge at different flip-flops, caused by routing asymmetry. Excessive skew eats setup margin (or causes hold violations). FPGA global clock trees minimize it.

**Q19. What is metastability and when does it strike?**
When setup/hold is violated, a flop can hover between 0 and 1 for an unbounded statistically-distributed time before resolving. It occurs when sampling asynchronous inputs; two-flop synchronizers are the practical cure.

**Q20. Why does Vivado need `create_clock`?**
Without it the timing engine has no performance target and reports nothing meaningful. `create_clock -period 10.000` defines the 100 MHz requirement against which WNS/TNS are computed — a commented-out create_clock (as in some templates) leaves the design unconstrained.

**Q21. Define WNS and TNS.**
WNS = worst (smallest) setup slack among all paths; TNS = sum of all negative slacks. Sign-off requires WNS ≥ 0 and TNS = 0. In this experiment WNS ≈ +6 ns on a 10 ns period.

**Q22. How do you estimate F_MAX from the timing report?**
F_MAX ≈ 1 / (T_constrained − WNS). Here ≈ 1/(10−6.2 ns) ≈ 260 MHz — far above the 100 MHz target.

**Q23. What FPGA primitives map your Verilog?**
FDRE flip-flops (D + CE + sync reset; CE/SR absorb en/rst), LUT6/LUT5s for next-state logic and muxes, two CARRY8s for the 16-bit increment/decrement, one BUFG for the clock, IBUF/OBUF in the IOBs.

**Q24. What is a carry chain and why does the counter use it?**
A hardened, fast rippling path inside each slice (CARRY8) dedicated to arithmetic carry. Using it makes +1/−1 sub-nanosecond and frees LUTs — the tool infers it automatically from `count + 1'b1`.

**Q25. Why avoid generating a slow clock by `clk_out <= counter[25]` and using it as a clock?**
That creates a derived clock on general routing: huge skew, duty-cycle distortion, a second timing domain, and painful constraint effort. The correct pattern is one fast clock plus enable ticks — exactly what `clock_enable_gen` does.

**Q26. What is a self-checking testbench?**
A testbench that compares DUT outputs against expected values itself (`if (got !== expected)`), logs PASS/FAIL with timestamps, counts errors, prints a final verdict and finishes automatically — no human waveform reading required.

**Q27. Why apply stimulus on the negedge of the clock?**
So that inputs are stable well before the active rising edge (mimicking the output of a real source register and honouring setup time), and so checks after the rising edge see the settled new value. It removes stimulus-vs-DUT races.

**Q28. What does `!==` check that `!=` does not?**
Case-inequality `!==` compares X and Z bits exactly — an X in the DUT output fails the check. `!=` treats X-poisoned comparisons as unknown, which can silently mask bugs.

**Q29. What is the purpose of the watchdog `initial #2000000 … $finish` block?**
A simulation timeout: if stimulus deadlocks (e.g. a waiting edge that never comes), the watchdog forces `$finish` so the run never hangs.

**Q30. Why can a latch never be inferred in your clocked always blocks?**
Latches are inferred only from level-sensitive blocks with incomplete assignment. Our single block is edge-triggered; therefore every assigned variable becomes a flip-flop by construction, and all branches assign their targets anyway.

**Q31. Why expose `max_tick` instead of a registered "overflowed" flag?**
The combinational terminal decode lets a *higher-order* counter use it as its enable — the cascade then increments in the same cycle the low stage rolls over (classic synchronous cascade). A registered event flag can be added by a caller that needs history.

**Q32. How would you cascade two of your counters into a 32-bit counter?**
Feed the low module's `max_tick & en` into the high module's `en` in up mode (and `min_tick & en` in down mode); both share clock, reset and load controls. Synchronous cascade with zero extra timing domains.

**Q33. What happens in your shift register if `mode` is an unknown (X)?**
The `default` branch forces a hold, so the register keeps its value instead of propagating X — defensive coding per UG901 guidelines.

**Q34. Why does the counter `load` have priority over `en` (T04)?**
Because that is the natural use model: presetting a timer must work even while it is enabled for counting; the if/else chain `rst → load → en` synthesizes exactly a priority mux with that order.

**Q35. Give the three roles of an XDC file seen here.**
(1) Pin placement + I/O standards (`PACKAGE_PIN`, `IOSTANDARD`), (2) timing specification (`create_clock`), (3) configuration bank settings (`CFGBVS`, `CONFIG_VOLTAGE`). Only valid Tcl is allowed — a stray `)` breaks the whole file.

**Q36. What does BUFG do and why is there exactly one here?**
BUFG is a global clock buffer driving the low-skew backbone clock tree. Single-clock-domain design = exactly one BUFG, minimum skew everywhere.

**Q37. What is the purpose of `timescale 1ns/1ps`?**
It sets simulation time units (1 ns) and resolution (1 ps) for `#` delays — matching the 10 ns clock period waveform math in this report. Synthesis ignores it.

**Q38. How do you make a modulo-N counter (e.g. decade) from your module?**
Use the synchronous load: decode N−1 and assert `load` with `din = 0` (or decode terminal and use `rst`); with the tick pattern used here, `DIVISOR=N` in `clock_enable_gen` demonstrates the same terminal-count idea.

**Q39. Why is `count <= count` written explicitly in the hold branch?**
It documents the hold intent and guarantees complete branch coverage for reviewers; synthesis folds it into the CE connection (`en`=0) so it costs nothing.

**Q40. Convert the walking-one test into a real application.**
Load 0x01 and shift left each tick — that's an LED chaser / one-hot sequencer. Feed the serial input from `sout_l` instead of 0 (i.e. `sin_l = sout_l`) and it becomes a ring counter rotating forever.

---

<!-- page break -->

---

# 25. COMMON ERRORS AND DEBUGGING

**Compilation (elaboration) errors**

| Symptom (typical message) | Root cause | Fix |
|---|---|---|
| `cannot find port 'D0_AN[0]'` [Common 17-55] | XDC pins constrained that don't exist in the top | Comment out unused groups (as done in our XDC) or add the ports |
| `module 'up_down_counter_16bit' was not found` | File not added / wrong file type | Add all `rtl/*.v` as Design Sources; check `set_property file_type` |
| `syntax error near ')'` in XDC | Stray non-Tcl token (the template's trailing `)`) | Delete the stray character; XDC is pure Tcl |
| Implicit net declaration / `multiple drivers` | Typo in a net name with `\`default_nettype wire` | Keep `\`default_nettype none`; declare every net explicitly |
| Width mismatch warnings | Connecting 16-bit bus to 8-bit port | Match widths; use part-selects `sw[9:2]` |

**Simulation errors**

| Symptom | Root cause | Fix |
|---|---|---|
| Count changes at *both* edges | Clock generated with wrong period or stimulus applied on posedge | `always #(CLK_PERIOD/2)` — apply stimulus at `@(negedge clk)` |
| `X` in `count` at time 0 | No reset applied before first check | Hold `rst=1` for ≥1 clock before releasing (as in T01) |
| Checks pass/fail race (same ns chaos) | Stimulus and sampling at the same edge without `#1` | Check **1 ns after** the posedge (`@(posedge clk); #1;`) |
| "simulation hangs" | Waiting for an edge that never occurs | Watchdog `initial #T $finish`; verify clock `always` runs |
| Rollover never happens | Forgot `en=1` during overflow test, or width of literals wrong | Set `en`/`up_n_down`; size literals (`16'hFFFF`) |
| Case inequality mysteriously passes | Used `!=` instead of `!==` | Use `!==` so X/Z fail the check |

**Synthesis errors**

| Symptom | Root cause | Fix |
|---|---|---|
| `inferred latch` critical warning | Incomplete `if/case` in `always @(*)` | Cover every branch / add `default`; in this design: keep everything in the clocked process |
| Control signals became huge LUT trees | Reset used asynchronously / clock gated | Use synchronous controls (SR/CE pins) and enable ticks |
| Shift register exploded into many LUTs unexpectedly | Fine here, but note: without parallel load the tool could use SRL16/SRL32 | Acceptable; use `(* shreg_extract = "yes" *)` when applicable |
| Black-box / missing top ports | Top module name mismatch with the XDC | Keep top ports exactly: `clk, sw[15:0], btn[3:0], led[15:0]` |

**Constraint / timing errors**

| Symptom | Root cause | Fix |
|---|---|---|
| `No clocks found` / empty timing report | `create_clock` commented out | Un-comment `create_clock -period 10.000 …` (done in our XDC) |
| `timing constraints not met` (negative WNS) | Over-constrained or wrong part | Correct part (xc7s50csga324-1); check critical path; pipeline logic |
| Pins unconstrained warnings | Some top ports missing PACKAGE_PIN | Constrain every used port; leave unused board signals in comments |
| BUFG insertion failed warnings | Multiple "clocks" from logic | Never clock flops from counter bits; use enable ticks |

**Hardware errors**

| Symptom | Root cause | Fix |
|---|---|---|
| LED pattern changes too fast to see | Enable driven by raw 100 MHz | Use `clock_enable_gen` tick (2 Hz) as the enable |
| DONE LED off after programming | Cable/JTAG chain issue, wrong bit file | *Auto Connect* again; regenerate bitstream for the correct part |
| Load/count behaves as if reset stuck | btn polarity expectation wrong (buttons are active high) | Verify with the truth table; probe with ILA (Integrated Logic Analyzer) |
| Random extra load/step events | Button bounce on edge-style use | Use level-style control (as here) or add debouncer |
| LEDs dim/flicker | Accidental PWM-like gating at mid frequency | Confirm `DIVISOR` = 50,000,000 (2 Hz) |

**Debugging method (how these were hunted generally):** read the first error in the log top-down (later errors are usually cascade noise); isolate by commenting blocks (binary search); elaborate `RTL Schematic` to see if the drawing matches the block diagram; use self-checking benches before GUI waveform digging; on hardware, attach Vivado ILA cores to internal signals and trigger on the failing condition.

---

# 26. TROUBLESHOOTING

| # | Problem | Diagnosis | Solution |
|:-:|---|---|---|
| 1 | Vivado aborts while reading the XDC | Tcl syntax error from a stray token at file end (template shipped `)`) | Remove the stray token; re-lint: every line must be a valid `set_property`/`create_clock`/comment |
| 2 | Timing summary shows "unconstrained" | `create_clock` was left commented | Enable the `create_clock` line; re-run implementation |
| 3 | Testbench compiles but `count` stays X | Reset never asserted at time 0 | Drive `rst=1` before the first clock edge (done in T01) |
| 4 | Simulation stops immediately at 0 ns | `$finish` placed outside the timing flow / typo | Keep `$finish` at the end of the main `initial` only; keep watchdog separate |
| 5 | Waveform shows double-speed counting | Clock period 5 ns instead of 10 ns (`#CLK_PERIOD` instead of `#CLK_PERIOD/2` toggle) | Toggle every 5 ns → `always #(CLK_PERIOD/2) clk = ~clk;` |
| 6 | Overflow check fails | `en` low during the rollover edge, or checking *at* the edge without `#1` | Set `en=1`; sample after the edge + 1 ns |
| 7 | Shift register seems to load garbage on hold | `pin` not stable — but on hold pin must be ignored | Inspect `mode`: hold = 00 verified by T03; if mode glitches at the tick edge on hardware, keep mode switches steady |
| 8 | Synthesis infers a latch warning | Missing `else`/`default` in some edit | Restore complete branches (rst/else-if/else; case with default) |
| 9 | Bitstream generates but board LEDs dead | Constraints file not in the active constraint set / wrong top | *Set as Top* + check `boolean_board.xdc` is targeted at the current top; confirm DONE LED |
| 10 | Counter counts while `btn[1]` released | `en` wired to wrong pin (btn mapping) | btn order: btn[0]=J2, btn[1]=J5, btn[2]=H2, btn[3]=J1 — match XDC |
| 11 | LEDs change at 100 MHz blur | tick not connected (`en` tied to 1) | Route `slow_tick & btn[1]` into `en` as in `counter_top_boolean` |
| 12 | One LED never lights | Pin mapping typo or dead IO | Cross-check that LED's PACKAGE_PIN in the XDC against the board manual |
| 13 | Logs differ from Section 13 transcript | Stimulus edited, radix confusion (hex vs decimal) | Re-run unchanged TBs; set `count/pout` radix to Hex in the viewer |
| 14 | Program fails: "Cannot find device" | Cable/driver/power | Re-seat USB, power-cycle, *Open Target → Auto Connect*, check JTAG chain |
| 15 | Everything works except at higher speed | Asynchronous switch sampling / bounce dominates | Add two-flop synchronizers + debounce when inputs drive edge-sensitive logic |

---

<!-- page break -->

---

# 27. CONCLUSION

This experiment took the two most fundamental synchronous building blocks — the binary counter and the universal shift register — from specification to working silicon. Starting from the theory of sequential logic, clocks, flip-flops and timing, a **16-bit up/down counter** with synchronous reset, synchronous load, enable and direction control, and an **8-bit universal shift register** with hold/shift-right/shift-left/parallel-load modes were modelled in clean, parameterized Verilog-2001 using a single clocked process and non-blocking assignments — the style that guarantees flip-flop inference and maps control signals onto the FPGA's dedicated CE/SR pins.

Verification was treated as a first-class deliverable: two self-checking testbenches exercised every mode and boundary condition, including an exhaustive pass through all 65,536 counter states, exact rollover events at both terminal counts, priority disputes between reset/load/enable, a shift round-trip returning exactly to the loaded pattern, and serial-output observation — totalling 65,573 and 51 automated checks respectively, all passing with zero errors. The design was then constrained with a corrected XDC (with the essential `create_clock` active and Tcl-syntax-validated), synthesized onto the Spartan-7 with the expected primitive mapping (FDRE, LUTs, CARRY8, single BUFG) at under 0.5 % device utilization, and implemented with comfortable timing closure (≈ +6 ns slack on the 10 ns budget, ~2.6× frequency margin). Finally, both functions were demonstrated on the Boolean board's switches, buttons and LEDs at a human-visible 2 Hz, engineered through a clock-*enable* tick that preserved a single well-behaved clock domain.

The workflow practiced here — specify, tabulate, draw, code, self-verify, constrain, synthesize, time, program, observe — is exactly the loop used in industry FPGA development, and the two IP-quality modules produced are ready to be reused as timers, serializers and sequencers in the upcoming UART, display-driver and processor-oriented experiments of this laboratory course.

---

# 28. REFERENCES

[1] Xilinx, Inc., *Vivado Design Suite User Guide: Synthesis*, UG901 (v2023.2), AMD Xilinx, San Jose, CA, USA, 2023.

[2] Xilinx, Inc., *UltraFast Design Methodology Guide for the Vivado Design Suite*, UG949 (v2023.2), AMD Xilinx, San Jose, CA, USA, 2023.

[3] Xilinx, Inc., *7 Series FPGAs Configurable Logic Block User Guide*, UG474 (v1.8), AMD Xilinx, San Jose, CA, USA, 2016.

[4] Xilinx, Inc., *7 Series FPGAs Clocking Resources User Guide*, UG472 (v1.14), AMD Xilinx, San Jose, CA, USA, 2018.

[5] RealDigital, *Boolean Board Reference Manual — Spartan-7 FPGA Development Platform*, RealDigital.org, Pullman, WA, USA, 2021. [Online]. Available: https://www.realdigital.org/hardware/boolean

[6] M. Morris Mano and M. D. Ciletti, *Digital Design: With an Introduction to the Verilog HDL*, 5th ed. Upper Saddle River, NJ, USA: Pearson/Prentice Hall, 2013.

[7] S. Palnitkar, *Verilog HDL: A Guide to Digital Design and Synthesis*, 2nd ed. Upper Saddle River, NJ, USA: Prentice Hall PTR, 2003.

[8] J. Bhasker, *A Verilog HDL Primer*, 3rd ed. Allentown, PA, USA: Star Galaxy Publishing, 2005.

[9] IEEE Standard for Verilog Hardware Description Language, IEEE Std 1364-2001, IEEE, New York, NY, USA, 2001.

[10] P. P. Chu, *FPGA Prototyping by Verilog Examples: Xilinx Spartan-3 Version*. Hoboken, NJ, USA: Wiley-Interscience, 2008.

[11] Texas Instruments, *SN74LS194A 4-Bit Bidirectional Universal Shift Register Datasheet*, SDLS038B, Texas Instruments, Dallas, TX, USA, 1988.

[12] C. E. Cummings, "Clock domain crossing (CDC) design & verification techniques using SystemVerilog," in *Proc. Synopsys Users Group (SNUG)*, Boston, MA, USA, 2008.

---

*End of report — Week 3: Counters & Shift Registers.*
