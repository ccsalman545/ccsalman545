# WEEK 3 — COUNTERS & SHIFT REGISTERS

## Digital Design & FPGA Laboratory

---

| | |
|---|---|
| **Experiment No.** | 03 |
| **Experiment Title** | Design, Simulation and FPGA Implementation of a 16-bit Synchronous Up/Down Counter and an 8-bit Universal Shift Register |
| **Course** | Digital Design & FPGA Laboratory (M.Sc. Electronics) |
| **Department** | Department of Electronics |
| **University** | Cochin University of Science and Technology (CUSAT) |
| **Student Name** | Muhammed Salman CC |
| **Register Number** | ______________________ |
| **Date of Experiment** | 21 July 2026 |
| **Faculty In-charge** | ______________________ (Signature) |
| **Hardware Platform** | RealDigital Boolean Board — Xilinx Spartan-7 FPGA (xc7s50) |
| **Design Tool** | Xilinx Vivado Design Suite |
| **HDL** | Verilog HDL (IEEE Std 1364-2001) |
| **System Clock** | 100 MHz (on-board oscillator, pin F14) |

---

<!-- page break -->

---

# TABLE OF CONTENTS

1. Aim
2. Objectives
3. Theory
4. Truth Tables
5. State Diagrams
6. Flow Charts
7. Block Diagrams
8. Pin Description
9. Algorithm
10. RTL Design Explanation
11. Verilog Code
12. Self-Checking Testbenches
13. Expected Waveforms and Simulation Results
14. Vivado Simulation Procedure
15. FPGA Constraints (XDC)
16. Vivado Synthesis
17. Timing Analysis
18. Hardware Implementation
19. Hardware Observation Table
20. Result
21. Advantages
22. Disadvantages and Limitations
23. Applications
24. Viva Questions and Answers
25. Common Errors and Debugging
26. Troubleshooting
27. Conclusion
28. References

---

<!-- page break -->

---

# 1. AIM

To design, simulate, synthesize and implement fundamental synchronous sequential building blocks — a **16-bit up/down counter** with synchronous reset, synchronous parallel load and count-enable control, and an **8-bit universal shift register** supporting hold, shift-left, shift-right and parallel-load modes — using Verilog HDL in the Xilinx Vivado Design Suite, to verify their behaviour exhaustively with self-checking testbenches in the Vivado simulator, to constrain and implement the designs on the RealDigital Boolean Board (Spartan-7 FPGA), and to analyze the resource utilization and timing performance of the implemented circuits.

---

# 2. OBJECTIVES

After completing this experiment, the student will be able to:

1. Explain the difference between combinational and sequential logic and identify the role of the clock in synchronous digital systems.
2. Model edge-triggered sequential logic in Verilog using a single clocked `always` block with non-blocking assignments.
3. Design a parameterized 16-bit synchronous binary counter with clearly defined control-signal priority: reset > load > enable > hold.
4. Implement up/down direction control with correct rollover behaviour at the terminal counts 0xFFFF (overflow) and 0x0000 (underflow).
5. Design an 8-bit universal shift register that selects one of four synchronous operations — hold, shift right, shift left and parallel load — using a 2-bit mode field in the style of the classic 74x194 MSI device.
6. Generate one-shot terminal-count flags (`max_tick`, `min_tick`) and serial outputs (`sout_l`, `sout_r`) that make the blocks cascadeable.
7. Write professional self-checking Verilog testbenches that apply stimulus on the inactive clock edge, compare outputs automatically, print PASS/FAIL verdicts and terminate the simulation by themselves.
8. Exercise every operating mode in simulation, including a full-range sweep of all 65,536 counter states, and interpret the resulting waveforms.
9. Create a Xilinx Design Constraints (XDC) file that maps the design ports onto the Boolean board's clock, switches, buttons and LEDs, including a proper `create_clock` timing constraint.
10. Run Vivado synthesis, interpret the utilization report (LUTs, flip-flops, carry chains, IOBs, BUFG), and relate every inferred resource back to the RTL source.
11. Perform static timing analysis and interpret Worst Negative Slack (WNS), Total Negative Slack (TNS) and the estimated maximum clock frequency.
12. Program the Spartan-7 FPGA through the Vivado Hardware Manager, and demonstrate the counter and shift register operating on the physical board at a human-visible rate using a clock-enable tick generator that keeps the design fully synchronous.

---

<!-- page break -->

---

# 3. THEORY

## 3.1 Sequential Logic

Digital circuits are broadly classified into two families. A **combinational circuit** produces outputs that depend only on the present combination of its inputs; it has no memory. Adders, multiplexers, decoders and comparators belong to this family. A **sequential circuit**, in contrast, produces outputs that depend on the present inputs **and** on the history of past inputs. History is retained in storage elements — latches and flip-flops — whose collective content is called the **state** of the circuit. Counters, shift registers, finite state machines and register files are sequential circuits.

Practical sequential systems are almost always built as **synchronous** circuits: all storage elements are updated simultaneously, triggered by a common periodic signal called the clock. Between two active clock edges the combinational logic between registers settles to new values; at the active edge these values are captured into the registers, and the machine advances by exactly one state. This strict rhythm is what makes large digital systems analyzable, testable and reliable.

### Combinational vs. Sequential Logic

| Aspect | Combinational Logic | Sequential Logic |
|---|---|---|
| Output depends on | Present inputs only | Present inputs + stored state |
| Memory elements | None | Flip-flops / latches |
| Clock | Not required | Central synchronization signal |
| Feedback | Not allowed (would oscillate or latch) | Essential and controlled |
| Analysis | Truth table | Truth table **and** state table / state diagram |
| Examples | Adder, MUX, decoder, encoder | Counter, shift register, FSM |

## 3.2 The Clock

The clock is a free-running square wave whose **period** T (10 ns for a 100 MHz clock) and **frequency** f = 1/T define the rate at which the machine advances. The **rising (positive) edge** is the active edge in this experiment. Each active edge commands every flip-flop in the design to sample its D input and transfer it to its Q output. All other moments of time the flip-flop outputs are frozen; the combinational cloud between registers uses this quiet interval to compute the **next state**. The maximum usable clock frequency is therefore dictated by the slowest combinational path between any two registers — this is the essence of static timing analysis discussed later.

## 3.3 Flip-Flops

A **flip-flop** is a one-bit edge-triggered storage cell. The D flip-flop is the workhorse of synchronous design: Q follows D only at the active clock edge. Modern SRAM-based FPGAs such as the Spartan-7 provide one D flip-flop per logic-cell output, each with dedicated **clock-enable (CE)** and **synchronous set/reset (SR)** control pins. This is why control styles that map onto these dedicated pins — a single clock, synchronous reset and explicit enable — are strongly preferred in FPGA design: they add no LUT cost and simplify timing closure. In Verilog, edge-triggered behaviour is modelled with an `always @(posedge clk)` block and **non-blocking** assignments (`<=`), which guarantee that every register reads the *old* value of every other register, exactly as real hardware does.

## 3.4 Registers

A **register** is an ordered group of n flip-flops sharing a common clock, storing an n-bit word. An n-bit register holds 2ⁿ distinct states. Registers are the atomic storage of datapaths: counters are registers whose next-state logic is an incrementer/decrementer; shift registers are registers whose next-state logic is a one-position permutation; pipeline stages are registers with raw data feed-through.

## 3.5 Counters

A **counter** is a sequential circuit that steps through a predetermined sequence of states, one state per clock (or per enable tick). A binary counter with n flip-flops visits 2ⁿ states and is called a **modulo-2ⁿ** counter; the 16-bit counter designed here is modulo-65536. Counters are the most widely used sequential building block in digital engineering.

### Applications of Counters

- Frequency division and clock generation (a counter bit toggles at a divided rate)
- Event counting (pulse counting, product counting on conveyor lines)
- Time measurement and interval timing (period measurement, watchdog timers)
- Address sequencing for memories and FIFO pointers
- PWM generation, baud-rate generation in UARTs, refresh timers for DRAM/displays
- As state sequencers ("program counters") inside control units

### Types of Counters

**Ripple (asynchronous) counter.** Each flip-flop is clocked by the output of the previous flip-flop. Simple and cheap, but the bits change one after another like a wave: the propagation delays accumulate, the worst-case resolution time grows linearly with width, and transient invalid states appear at the output. Suitable only for slow, undemanding tasks (e.g., freerun dividers feeding nothing synchronous).

**Synchronous counter.** Every flip-flop receives the *same* clock; the next-state of each bit is computed combinationally from the current value. All bits change simultaneously; the delay is one flip-flop clock-to-Q plus one level of next-state logic, independent of width (wide counters use look-ahead carry, which maps beautifully onto FPGA carry chains). This is the only style appropriate inside an FPGA and is the style used in this experiment.

**Up counter.** Counts 0, 1, 2, …, 2ⁿ−1, then wraps (rolls over) to 0.

**Down counter.** Counts 2ⁿ−1, 2ⁿ−2, …, 1, 0, then wraps to 2ⁿ−1.

**Up/Down counter.** A direction input selects between the two sequences — the device designed in this experiment. It is the standard counter found in interval timers, position encoders and servo/robotics feedback.

**Ring counter.** A shift register with its serial output fed back to its serial input, initialized with a single '1'. The '1' circulates, giving n decoded states from n flip-flops (one-hot). Used for phase sequencers and one-hot control.

**Johnson (twisted ring) counter.** The *inverted* serial output is fed back, doubling the sequence length to 2n states that are decoded with two-input AND gates. Used for multi-phase clock generation and decade dividers.

### Control Features of the Counter Designed Here

- **Enable (`en`).** A clock-enable: when high the counter advances on the next clock edge, when low it holds. In an FPGA this maps to the dedicated CE pin of the flip-flops — zero extra routing fabric. It is also the correct way to slow a counter down: gate the *enable*, never the clock.
- **Synchronous reset (`rst`).** Forces the count to 0 at the next active edge. Being synchronous, it cannot cause partial resets, needs no reset-release (recovery/removal) timing closure across domains, and maps onto the SR pin of the FPGA flip-flops.
- **Synchronous load (`load`, `din`).** Captures an arbitrary 16-bit starting value in one clock, giving the counter the power of a presettable register — essential for programmable timers and baud generators.
- **Overflow / terminal count.** When an up-counter reaches its maximum (0xFFFF here) and is enabled, the next state is 0x0000: the counter **rolls over**. If an application treats this wrap-around as an unintended loss of count, it is an **overflow** event; the `max_tick` flag marks the terminal state so that overflow can be detected or a higher-order counter stage can be ticked.
- **Rollover (wrap-around).** The cyclic return from terminal count back to the start. Down counters roll over from 0x0000 to 0xFFFF (detected by `min_tick`). Modulus behaviour makes counters natural circular address generators.

### Advantages and Disadvantages of Counters

Advantages: extremely simple next-state logic, deterministic modulo behaviour, trivially cascadeable with terminal-count flags, near-free implementation using FPGA carry chains, and naturally self-returning (no illegal states). Disadvantages: a plain binary counter has a fixed modulus of 2ⁿ (arbitrary moduli need extra decode logic), and very wide counters still see enable/fan-out delays that must be considered at high clock rates.

## 3.6 Shift Registers

A **shift register** is a register whose flip-flops transfer their contents to a neighbour on every clock edge, so the stored bit pattern moves bodily by one position. Serial data enters at one end and leaves at the other; the register therefore behaves like a discrete-time delay line and as a converter between serial and parallel data formats. The flip-flops share a common clock, so a shift register is a perfectly synchronous circuit.

### Basic Types

| Type | Name | Data In | Data Out | Typical Use |
|---|---|---|---|---|
| **SISO** | Serial-In Serial-Out | 1 bit/clk | 1 bit/clk | Digital delay lines, serial data alignment |
| **SIPO** | Serial-In Parallel-Out | 1 bit/clk | n-bit word | UART/SPI receive, serial stream deserialization |
| **PISO** | Parallel-In Serial-Out | n-bit word | 1 bit/clk | UART/SPI transmit, serialization |
| **PIPO** | Parallel-In Parallel-Out | n-bit word | n-bit word | Temporary storage, pipelining |
| **Universal** | Bidirectional + all modes | serial or parallel | serial and parallel | General-purpose register block (74x194) |

### Universal Shift Register

The **universal shift register** integrates all the capabilities above. A bank of n flip-flops is fed through a per-bit 4-to-1 multiplexer whose select lines form a 2-bit `mode` field:

| mode[1:0] | Operation | Next state of each bit Q_i |
|---|---|---|
| 00 | Hold | Q_i |
| 01 | Shift right | Q_{i+1} (MSB receives `sin_r`) |
| 10 | Shift left | Q_{i−1} (LSB receives `sin_l`) |
| 11 | Parallel load | pin_i |

Because shifting in both directions is supported, the register needs **two serial inputs** (one feeding the MSB on right shifts, one feeding the LSB on left shifts) and exposes **two serial outputs** (the bits falling off the ends), making the device cascadeable into wider registers. This is precisely the architecture of the classic 74194 IC, and precisely the Verilog module developed in this experiment.

### Applications of Shift Registers

- UART/SPI/I²S serial-to-parallel and parallel-to-serial conversion
- Digital delay lines and time skewing between streams
- Pseudo-random sequence generation (LFSR — a shift register with XOR feedback)
- Sequence and pattern detection in communication receivers
- LED chasers, multiplexed 7-segment scanning, keyboard scanning
- Multiplication/division by powers of two (arithmetic shifts)
- Data framing, bit-stuffing and CRC computation in protocols
- Ring/Johnson counters (shift registers with feedback)

### Advantages of Shift Registers

They use the minimum possible interconnect (nearest-neighbour routing, ideal for both ICs and FPGAs), scale linearly with width, provide a clean modular solution to serial interfacing, and — because FPGA logic cells pack flip-flop + LUT pairs densely — cost almost nothing for moderate widths. In FPGAs they are so common that synthesis tools recognize them and can pack them into dedicated shift-register LUT primitives (SRL16/SRL32) when no parallel load is needed.

## 3.7 FPGA Implementation of Synchronous Blocks

A Xilinx 7-series Configurable Logic Block (CLB) contains slices; each slice packs several 6-input look-up tables (LUTs), flip-flops with CE/SR controls, and a fast dedicated **carry chain** (in Spartan-7, the CARRY8 primitives) that ripples arithmetic carry vertically through the slice at zero LUT cost and with sub-nanosecond delay per bit. A counter is therefore implemented as: LUT logic computing the next value → carry chain accelerating the increment/decrement → flip-flop bank capturing it. A shift register with a mode mux is implemented as: per-bit 4:1 mux in LUTs → flip-flop bank. Because all storage elements share one clock and the reset/load/enable are synchronous, the entire design lives in a **single clock domain**, so one global clock buffer (BUFG) and one `create_clock` constraint are enough for complete static timing analysis.

### Why Synchronous Design is Preferred in FPGAs

1. **Dedicated control pins:** FPGA flip-flops have native CE and SR pins — synchronous enable/reset consume no LUT fabric.
2. **Deterministic timing:** one clock, analyzable setup/hold relations, no glitch-sensitive paths.
3. **Tool support:** static timing analysis assumes synchronous structure; asynchronous logic (ripple clocks, gated clocks) defeats or complicates it.
4. **Clock network integrity:** the low-skew global clock trees (BUFG/BUFH) are only useful if everything runs from the same clock.
5. **No clock-domain-crossing hazards:** single-domain designs avoid metastability between domains by construction.

## 3.8 Timing Concepts

**Setup time (t_su).** The minimum interval during which the data at a flip-flop's D input must be stable **before** the active clock edge for reliable capture.

**Hold time (t_h).** The minimum interval during which the data must remain stable **after** the active edge.

**Clock-to-Q / propagation delay (t_co).** The delay from the active edge until the Q output is valid. Register-to-register logic must satisfy: t_co + t_logic + t_routing + t_su ≤ T for every path.

**Clock skew.** The difference in arrival time of the same clock edge at two different flip-flops, caused by routing asymmetry. Positive skew on the destination helps setup but hurts hold and vice versa. FPGA clock trees are engineered to keep skew to tens of picoseconds.

**Metastability.** If setup or hold is violated, the flip-flop may enter a metastable state — an unresolved intermediate voltage that takes an unbounded (statistically characterized) time to settle, possibly propagating wrong values. It is unavoidable when sampling genuinely asynchronous inputs (buttons, UART RX) and is managed in practice with two-flip-flop synchronizers; strictly single-domain synchronous designs eliminate it internally.

**Why Vivado checks timing.** Simulation with ideal #0 RTL delays proves only *logical* correctness; it says nothing about whether the placed-and-routed physical circuit can sustain the 100 MHz (10 ns) clock on the actual silicon. Implemented timing analysis aggregates real cell and routing delays for **every** register-to-register path and reports slack. Only a timing-closed bitstream deserves to go into the board — this is why the constraint `create_clock -period 10.000` is mandatory rather than decorative: without it the tool has no target to check against.

---

<!-- page break -->

---
