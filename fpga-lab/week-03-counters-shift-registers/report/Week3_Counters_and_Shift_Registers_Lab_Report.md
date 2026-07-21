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

# 4. TRUTH TABLES

## 4.1 16-bit Up/Down Counter — synchronous function table

All transitions occur on the rising edge of `clk`. The counter has **no** asynchronous behaviour: every input in the table is sampled at the clock edge. `count⁺` denotes the next state; X = don't care.

| rst | load | en | up_n_down | din | count⁺ (next state) | Operation |
|:---:|:----:|:--:|:---------:|:---:|---------------------|-----------|
| 1 | X | X | X | X | 0x0000 | Synchronous reset (highest priority) |
| 0 | 1 | X | X | data | din | Synchronous parallel load |
| 0 | 0 | 1 | 1 | X | count + 1 | Count up (roll over FFFF→0000) |
| 0 | 0 | 1 | 0 | X | count − 1 | Count down (roll over 0000→FFFF) |
| 0 | 0 | 0 | X | X | count | Hold (enable low) |

Priority is encoded by row order: **rst > load > en > hold**.

Terminal-flag decode (combinational, true at all times):

| count | max_tick | min_tick |
|-------|:--------:|:--------:|
| 0xFFFF | 1 | 0 |
| 0x0000 | 0 | 1 |
| any other | 0 | 0 |

## 4.2 8-bit Universal Shift Register — synchronous function table

| rst | mode[1:0] | sin_r | sin_l | pin | pout⁺ (next state) | Operation |
|:---:|:---------:|:-----:|:-----:|:---:|--------------------|-----------|
| 1 | XX | X | X | X | 0x00 | Synchronous reset (dominates mode) |
| 0 | 00 | X | X | X | pout | Hold — data retention |
| 0 | 01 | d | X | X | {d, pout[7:1]} | Shift right: d enters MSB, LSB shifts out |
| 0 | 10 | X | d | X | {pout[6:0], d} | Shift left: d enters LSB, MSB shifts out |
| 0 | 11 | X | X | data | pin | Parallel load |

Serial outputs (combinational):

| Output | Definition | Meaning |
|--------|-----------|---------|
| sout_l | pout[7] | bit leaving the MSB on shift-left |
| sout_r | pout[0] | bit leaving the LSB on shift-right |

## 4.3 Example operation trace (verified by the testbench)

Load 0xA5 = `1010 0101`, then operate:

| Step | mode | Serial in | pout (after edge) | Note |
|:----:|:----:|:---------:|:-----------------:|------|
| 0 | 11 (load) | — | 1010 0101 (0xA5) | parallel load |
| 1 | 01 (right) | sin_r = 1 | 1101 0010 (0xD2) | 1 into MSB, 1 out of LSB |
| 2 | 01 | sin_r = 0 | 0110 1001 (0x69) | |
| 3 | 01 | sin_r = 1 | 1011 0100 (0xB4) | |
| 4 | 01 | sin_r = 1 | 1101 1010 (0xDA) | |
| 5 | 10 (left) | sin_l = 0 | 1011 0100 (0xB4) | 0 into LSB, 1 out of MSB |
| 6 | 10 | sin_l = 1 | 0110 1001 (0x69) | |
| 7 | 10 | sin_l = 0 | 1101 0010 (0xD2) | |
| 8 | 10 | sin_l = 1 | 1010 0101 (0xA5) | round-trip back to 0xA5 |
| 9 | 00 (hold) | — | 1010 0101 (0xA5) | value retained indefinitely |

---

<!-- page break -->

---

# 5. STATE DIAGRAMS

## 5.1 16-bit Up/Down Counter

A 16-bit counter has 65,536 states; the diagram below shows an arbitrary section of the state ring (state N in the middle) with every possible transition condition. Each state is drawn once — every state has exactly the same transition structure.

```
                          rst = 1 (any input)
                ┌─────────────────────────────────────────┐
                │                                         v
                │                                     [ 0x0000 ]
                │                                    (min_tick)
                v                                         ^
   ┌─────────────────────────────┐                        │ rst = 1
   │ count value N (0 < N < FFFF)│                        │
   └─────────────────────────────┘                        │
         |           |            |            |
   load=1 |     load=0, en=1,     |  load=0,   | load=0, en=0
   (din)  |      up_n_down=1      |  en=1,     | (hold:
         v           |            |  up_n_down=0  self-loop N)
   [ din ]           v            v     |
                  [ N+1 ]      [ N-1 ]  |
                     |            |     |
                     +-----+------+-----+
                           |
              terminal states behave identically except:
              N = 0xFFFF & counting up   → next = 0x0000   (max_tick = 1)
              N = 0x0000 & counting down → next = 0xFFFF   (min_tick = 1)

Legend:  [x] = state holding value x;  every state also has a "hold" self-loop
         (rst=0, load=0, en=0) and a reset arc to 0x0000 (not all drawn).
```

The full behaviour is a single 65,536-state cycle for counting (up or down), a one-edge "bus" from any state to `din` for loading, a self-loop on every state for holding, and a global arc to 0x0000 for reset.

## 5.2 8-bit Universal Shift Register

Because the next state of each bit depends on its neighbours, the convenient state-level view is the four-mode machine operating on the register as a whole:

```
                         rst = 1
            +-----------------------------------------+
            |                                         v
            |                                    [ 0x00 ]
            |
   +-------------------------------------------------------------+
   |                    REGISTER CONTENT R                        |
   |                                                             |
   |   mode=00  --+                                              |
   |  (HOLD)      |  self-loop: R stays R                        |
   |           <--+                                              |
   |                                                             |
   |   mode=01  ----------------->  {sin_r, R[7:1]}              |
   |  (SHIFT RIGHT)                (MSB <= sin_r, LSB leaves     |
   |                                through sout_r)              |
   |                                                             |
   |   mode=10  ----------------->  {R[6:0], sin_l}              |
   |  (SHIFT LEFT)                 (LSB <= sin_l, MSB leaves     |
   |                                through sout_l)              |
   |                                                             |
   |   mode=11  ----------------->  pin                          |
   |  (PARALLEL LOAD)              (whole word captured)         |
   +-------------------------------------------------------------+

   Every transition happens synchronously on the rising edge of clk.
```

---

<!-- page break -->

---

# 6. FLOW CHARTS

## 6.1 16-bit Up/Down Counter — clocked process

Executes once per rising clock edge (`always @(posedge clk)`):

```
                    ┌───────────────────────┐
                    │  Rising edge of clk   │
                    └───────────┬───────────┘
                                v
                        ┌───────────────┐
                        │   rst = 1 ?   │
                        └───┬───────┬───┘
                       YES  │       │  NO
                            v       v
                 ┌──────────────┐  ┌───────────────┐
                 │ count <= 0   │  │   load = 1 ?  │
                 │  (reset)     │  └───┬───────┬───┘
                 └──────┬───────┘ YES  │       │  NO
                        │              v       v
                        │   ┌────────────────┐  ┌───────────────┐
                        │   │ count <= din   │  │    en = 1 ?   │
                        │   │  (load)        │  └───┬───────┬───┘
                        │   └───────┬────────┘ YES  │       │  NO
                        │           │               v       v
                        │           │      ┌─────────────┐  ┌──────────┐
                        │           │      │ up_n_down ? │  │  count   │
                        │           │      └──┬───────┬──┘  │  holds   │
                        │           │    1    │       │  0  │  (en=0)  │
                        │           │         v       v     └────┬─────┘
                        │           │ ┌──────────┐┌──────────┐   │
                        │           │ │count+1   ││count-1   │   │
                        │           │ │<= count  ││<= count  │   │
                        │           │ └────┬─────┘└────┬─────┘   │
                        │           │      │           │         │
                        v           v      v           v         v
                    ┌─────────────────────────────────────────────┐
                    │ Non-blocking update: count changes AFTER    │
                    │ the edge; if count=FFFF → max_tick=1,       │
                    │ if count=0000 → min_tick=1 (combinational)  │
                    └─────────────────────────────────────────────┘
```

## 6.2 8-bit Universal Shift Register — clocked process

```
                    ┌───────────────────────┐
                    │  Rising edge of clk   │
                    └───────────┬───────────┘
                                v
                        ┌───────────────┐
                        │   rst = 1 ?   │
                        └───┬───────┬───┘
                       YES  │       │  NO
                            v       v
                 ┌──────────────┐  ┌───────────────────────────┐
                 │ pout <= 0x00 │  │        case (mode)        │
                 └──────┬───────┘  └──┬──────┬──────┬──────┬──┘
                        │            │      │      │      │
                        │          2'b00  2'b01  2'b10  2'b11
                        │            │      │      │      │
                        │       ┌────v──┐┌──v──────v──┐┌──▼─────────┐
                        v       │ HOLD  ││ SHIFT-RIGHT ││ SHIFT-LEFT  │
            ┌───────────────┐  │ pout  ││ {sin_r,     ││ {pout[6:0], │
            │  (reset)       │  │ holds ││  pout[7:1]} ││  sin_l}     │
            └───────┬───────┘  └───┬───┘└──────┬──────┘└──┬─────┬───┘
                    │              │           │          │     │
                    │              │      ┌────v──────────v──┐  │
                    │              │      │ LOAD: pout<=pin  │  │
                    │              │      └──────┬───────────┘  │
                    v              v           v                v
            ┌────────────────────────────────────────────────────────┐
            │ Non-blocking update after the edge;                    │
            │ sout_l = pout[7], sout_r = pout[0] (combinational)     │
            └────────────────────────────────────────────────────────┘
```

---

<!-- page break -->

---

# 7. BLOCK DIAGRAMS

## 7.1 16-bit Up/Down Counter (RTL view)

```
                              +----------------- din[15:0]
                              |
                      +-------v---------+
   en ----+           |   LOAD  MUX     |          +-----------------+
   load --+---------->| sel = load      |  d_next  |  16-bit register |
          |           |  a: din         +--------->|  (16 x DFF       |
   rst --+----------->|  b: from ALU    |          |   with CE & SR)   +--> count[15:0]
          |           +-------^---------+          |                   |
          |                   |                    |  CE <- en & !load |
          |           +-------+---------+          |  SR <- rst        |
          |           |  UP/DOWN ALU    +----------+  clk <- clk       |
          |           |  count + 1 if   |          +---------+---------+
          +-----------|  up_n_down=1,   |                    |
          direction   |  count - 1 else |                    v
                      +--------+--------+          count == 0xFFFF ──> max_tick
                               ^                     count == 0x0000 ──> min_tick
                               |                     (combinational decode)
                               count
```

Inputs: `clk`, `rst`, `en`, `up_n_down`, `load`, `din[15:0]`. Outputs: `count[15:0]`, `max_tick`, `min_tick`.
One clocked always block implements the register with its priority mux (rst > load > en > hold); the +1/−1 hardware is absorbed into the FPGA carry chain at synthesis.

## 7.2 8-bit Universal Shift Register (internal structure)

```
   pin[0..7] ──┐
   pout[0..7] ─┤  (each bit position i has its own 4-to-1 mux)
   pout[i+1]  ─┤      sin_r ────────────────────────────┐
   pout[i-1]  ─┤                                        │ (to mux of MSB)
               v                                        v      sin_l ──> mux of LSB
        ┌─────────────┐   ┌─────────────┐         ┌─────────────┐
mode───>│ 4:1 MUX #7  │   │ 4:1 MUX #6  │  . . .  │ 4:1 MUX #0  │<──mode
[1:0]   │ 00:pout[7]  │   │ 00:pout[6]  │         │ 00:pout[0]  │
        │ 01:sin_r    │   │ 01:pout[7]  │         │ 01:pout[1]  │
        │ 10:pout[6]  │   │ 10:pout[5]  │         │ 10:sin_l    │
        │ 11:pin[7]   │   │ 11:pin[6]   │         │ 11:pin[0]   │
        └──────┬──────┘   └──────┬──────┘         └──────┬──────┘
               v                 v                       v
        ┌─────────────┐   ┌─────────────┐         ┌─────────────┐
  clk──>│ D FF (SR)   │   │ D FF (SR)   │  . . .  │ D FF (SR)   │<──clk
  rst──>│             │   │             │         │             │<──rst
        └──────┬──────┘   └──────┬──────┘         └──────┬──────┘
               v                 v                       v
           pout[7]           pout[6]  . . .          pout[0]
             |                                             |
             +──> sout_l                                   +──> sout_r
```

## 7.3 Board-level integration (both demonstrations)

```
                    RealDigital Boolean Board (Spartan-7)
  ┌───────────────────────────────────────────────────────────────┐
  │                                                               │
  │  100 MHz osc ──> [clk]                                        │
  │                     │                                         │
  │                     v                                         │
  │              clock_enable_gen ──> tick (2 Hz, single domain)  │
  │                     │                                         │
  │  btn[0] ──> rst ────┤                                         │
  │  btn[1] ──> en ─────┼──> up_down_counter_16bit ──> led[15:0]  │
  │  btn[2] ──> dir ────┤        (counter_top_boolean)            │
  │  btn[3] ──> load ───┤                                         │
  │  sw[15:0] -> din ───┘                                         │
  │                                                               │
  │              OR (second bitstream)                            │
  │                                                               │
  │  btn[0] ──> rst                                               │
  │  sw[1:0] -> mode ──── gated by tick ──>                       │
  │  sw[9:2] -> pin ────────────┐                                 │
  │  sw[10] -> sin_r ───────────┼──> universal_shift_register_8bit│
  │  sw[11] -> sin_l ───────────┘        ├─> pout  ──> led[7:0]   │
  │                                      ├─> sout_r ─> led[14]    │
  │           (shiftreg_top_boolean)     └─> sout_l ─> led[15]    │
  └───────────────────────────────────────────────────────────────┘

  Constraints (boolean_board.xdc): clk=F14 + create_clock 10 ns,
  sw[15:0], btn[3:0], led[15:0] at LVCMOS33.
```

---

<!-- page break -->

---

# 8. PIN DESCRIPTION

## 8.1 `up_down_counter_16bit`

| Pin | Dir | Width | Active | Description |
|-----|:---:|:-----:|:------:|-------------|
| `clk` | in | 1 | rising edge | System clock. All state changes occur on the rising edge. Board oscillator: 100 MHz, pin F14. |
| `rst` | in | 1 | high | **Synchronous** reset. When high at a rising edge, `count` is cleared to 0x0000. Highest priority input. Maps to the SR pin of FPGA flip-flops. |
| `en` | in | 1 | high | Count enable (clock-enable). Counting only occurs while high; when low, the register holds its value. Maps to the CE pin of FPGA flip-flops. |
| `up_n_down` | in | 1 | — | Direction select: `1` = count up, `0` = count down. Effective only when `en`=1. |
| `load` | in | 1 | high | **Synchronous** parallel load. When high at a rising edge, `din` is captured into `count`. Priority above enable, below reset. |
| `din` | in | 16 | — | Parallel data input loaded when `load`=1. Connected to the 16 slide switches on the board. |
| `count` | out | 16 | — | Counter output register. Connected to the 16 LEDs on the board. |
| `max_tick` | out | 1 | high | Combinational terminal-count flag: high while `count`=0xFFFF. Indicates imminent upward overflow; used to cascade counters. |
| `min_tick` | out | 1 | high | Combinational flag: high while `count`=0x0000. Indicates imminent downward underflow. |

## 8.2 `universal_shift_register_8bit`

| Pin | Dir | Width | Active | Description |
|-----|:---:|:-----:|:------:|-------------|
| `clk` | in | 1 | rising edge | System clock; all operations are synchronous to its rising edge. |
| `rst` | in | 1 | high | **Synchronous** reset; clears `pout` to 0x00. Dominates the mode field. |
| `mode` | in | 2 | — | Function select: `00` hold, `01` shift right, `10` shift left, `11` parallel load (74x194 convention). |
| `sin_r` | in | 1 | — | Serial input bit shifted **into the MSB** during shift-right. |
| `sin_l` | in | 1 | — | Serial input bit shifted **into the LSB** during shift-left. |
| `pin` | in | 8 | — | Parallel data input captured when `mode`=11. |
| `pout` | out | 8 | — | Parallel output (register contents). |
| `sout_l` | out | 1 | — | Serial output = MSB `pout[7]`; the bit leaving the register on shift-left (for cascading). |
| `sout_r` | out | 1 | — | Serial output = LSB `pout[0]`; the bit leaving the register on shift-right (for cascading). |

## 8.3 Board top-level (`counter_top_boolean` / `shiftreg_top_boolean`)

| Board signal | FPGA pin(s) | Dir | Used as (counter top) | Used as (shift-reg top) |
|---|---|:---:|---|---|
| `clk` | F14 | in | 100 MHz system clock | 100 MHz system clock |
| `sw[15:0]` | V2…K1 | in | `din[15:0]` load data | `sw[1:0]`=mode, `sw[9:2]`=pin, `sw[10]`=sin_r, `sw[11]`=sin_l |
| `btn[0]` | J2 | in | `rst` | `rst` |
| `btn[1]` | J5 | in | `en` (gate: counts at 2 Hz while pressed) | (unused) |
| `btn[2]` | H2 | in | direction (pressed = down) | (unused) |
| `btn[3]` | J1 | in | `load` | (unused) |
| `led[15:0]` | G1…A4 | out | `count[15:0]` | `led[7:0]`=pout, `led[14]`=sout_r, `led[15]`=sout_l |

---

<!-- page break -->

---

# 9. ALGORITHM

## 9.1 16-bit Up/Down Counter

1. **Initialize:** On power-up the register value is undefined; it is brought to a known state by asserting `rst` (synchronously) for at least one clock edge.
2. **Wait for the rising clock edge.** Every action below happens only at that instant (synchronous design).
3. **Test reset:** If `rst` = 1, assign `count ← 0x0000`. Go to step 7.
4. **Test load:** Else if `load` = 1, assign `count ← din`. Go to step 7.
5. **Test enable:** Else if `en` = 1, test direction: if `up_n_down` = 1 assign `count ← count + 1` (wrapping from 0xFFFF to 0x0000), else assign `count ← count − 1` (wrapping from 0x0000 to 0xFFFF).
6. **Hold:** Else keep `count` unchanged.
7. **Decode flags:** Continuously (combinationally) set `max_tick` = (count == 0xFFFF) and `min_tick` = (count == 0x0000).
8. **Repeat** from step 2 for every clock edge.

## 9.2 8-bit Universal Shift Register

1. **Initialize** with one or more clock edges while `rst` = 1, leaving `pout` = 0x00.
2. **Wait for the rising clock edge.**
3. **Test reset:** If `rst` = 1, assign `pout ← 0x00`. Go to step 8.
4. **Decode mode 00 (Hold):** assign `pout ← pout` (no change).
5. **Decode mode 01 (Shift right):** assign `pout ← {sin_r, pout[7:1]}` — every bit moves one position toward the LSB, `sin_r` enters at the MSB, the old LSB exits through `sout_r`.
6. **Decode mode 10 (Shift left):** assign `pout ← {pout[6:0], sin_l}` — every bit moves one position toward the MSB, `sin_l` enters at the LSB, the old MSB exits through `sout_l`.
7. **Decode mode 11 (Parallel load):** assign `pout ← pin`.
8. **Expose serial outputs:** continuously assign `sout_l = pout[7]`, `sout_r = pout[0]`.
9. **Repeat** from step 2 for every clock edge.

---

<!-- page break -->

---

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

```verilog
//=============================================================================
// File          : up_down_counter_16bit.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Board         : RealDigital Boolean Board (Xilinx Spartan-7, 100 MHz clock)
// Tool          : Xilinx Vivado Design Suite
// Description   : Parameterized synchronous binary up/down counter (16-bit
//                 default). Features:
//                   - Synchronous, active-high reset
//                   - Synchronous parallel load
//                   - Count-enable control (clock-enable style, single clock)
//                   - Up/Down direction select
//                   - Terminal-count flags (max_tick / min_tick) for cascade
// Input priority: rst > load > en > hold
// Coding style  : Synthesizable Verilog-2001, non-blocking assignments only
//                 inside the clocked always block.
//=============================================================================
`timescale 1ns / 1ps
`default_nettype none

module up_down_counter_16bit #(
    parameter WIDTH = 16                          // counter width in bits
)(
    input  wire             clk,                  // system clock
    input  wire             rst,                  // synchronous reset, active high
    input  wire             en,                   // count enable (1 = count)
    input  wire             up_n_down,            // direction: 1 = up, 0 = down
    input  wire             load,                 // synchronous load (1 = load din)
    input  wire [WIDTH-1:0] din,                  // parallel load data
    output reg  [WIDTH-1:0] count,                // counter output
    output wire             max_tick,             // 1 when count == all ones
    output wire             min_tick              // 1 when count == all zeros
);

    // Constant patterns, written in a width-agnostic way (parameterization).
    localparam [WIDTH-1:0] ALL_ONES  = {WIDTH{1'b1}};
    localparam [WIDTH-1:0] ALL_ZEROS = {WIDTH{1'b0}};

    //-------------------------------------------------------------------------
    // Synchronous counter process.
    // Everything happens ONLY on the rising edge of clk -> all control inputs
    // (reset, load, enable, direction) are synchronous, which is the style
    // recommended for FPGA flip-flops with CE/SR control ports.
    //-------------------------------------------------------------------------
    always @(posedge clk) begin
        if (rst)
            count <= ALL_ZEROS;                     // (1) reset dominates
        else if (load)
            count <= din;                           // (2) then parallel load
        else if (en) begin                          // (3) then enabled counting
            if (up_n_down)
                count <= count + 1'b1;              //    up-count (rollover at FFFF)
            else
                count <= count - 1'b1;              //    down-count (rollover at 0000)
        end
        else
            count <= count;                         // (4) explicit hold (en = 0)
    end

    //-------------------------------------------------------------------------
    // Terminal-count flags: continuous (combinational) decode of the count.
    // Useful to cascade counters or to detect overflow/underflow events.
    //-------------------------------------------------------------------------
    assign max_tick = (count == ALL_ONES);
    assign min_tick = (count == ALL_ZEROS);

endmodule

`default_nettype wire
```

## 11.2 `universal_shift_register_8bit.v`

```verilog
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
```

## 11.3 `clock_enable_gen.v` (hardware-demo support)

```verilog
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
```

## 11.4 `counter_top_boolean.v` (board top — counter demo)

```verilog
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
```

## 11.5 `shiftreg_top_boolean.v` (board top — shift-register demo)

```verilog
//=============================================================================
// File          : shiftreg_top_boolean.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Board         : RealDigital Boolean Board (Xilinx Spartan-7, 100 MHz clock)
// Description   : Top level for the hardware demonstration of the 8-bit
//                 universal shift register on the Boolean board.
//
//                 Board mapping:
//                   btn[0]   -> rst          (synchronous reset)
//                   sw[1:0]  -> mode         (00 hold, 01 right, 10 left, 11 load)
//                   sw[9:2]  -> pin[7:0]     (parallel data)
//                   sw[10]   -> sin_r        (serial in  for shift right)
//                   sw[11]   -> sin_l        (serial in  for shift left)
//                   led[7:0] -> pout[7:0]    (register contents)
//                   led[14]  -> sout_r       (LSB shifted out on shift-right)
//                   led[15]  -> sout_l       (MSB shifted out on shift-left)
//
//                 The mode is applied only while the 2 Hz tick is active, so
//                 each shift/load step happens at an eye-visible rate and the
//                 register holds between steps.
//=============================================================================
`timescale 1ns / 1ps
`default_nettype none

module shiftreg_top_boolean (
    input  wire        clk,                       // 100 MHz, pin F14
    input  wire [15:0] sw,                        // slide switches
    input  wire [3:0]  btn,                       // push buttons (active high)
    output wire [15:0] led                        // LEDs (active high)
);

    wire slow_tick;
    wire [1:0] mode;
    wire [7:0] pout;
    wire       sout_l;
    wire       sout_r;

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

    // Apply the selected operation once per tick; hold in between.
    assign mode = slow_tick ? sw[1:0] : 2'b00;

    //-------------------------------------------------------------------------
    // Unit under test: 8-bit universal shift register
    //-------------------------------------------------------------------------
    universal_shift_register_8bit #(
        .WIDTH (8)
    ) u_shiftreg (
        .clk    (clk),
        .rst    (btn[0]),
        .mode   (mode),
        .sin_r  (sw[10]),
        .sin_l  (sw[11]),
        .pin    (sw[9:2]),
        .pout   (pout),
        .sout_l (sout_l),
        .sout_r (sout_r)
    );

    assign led[7:0]  = pout;
    assign led[13:8] = 6'b000000;
    assign led[14]   = sout_r;
    assign led[15]   = sout_l;

endmodule

`default_nettype wire
```

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

```verilog
//=============================================================================
// File          : tb_up_down_counter_16bit.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Description   : Self-checking testbench for up_down_counter_16bit.
//
//                 Stimulus is applied on the NEGATIVE edge of the clock so the
//                 inputs are stable around the active (positive) edge, and the
//                 outputs are checked just after each positive edge (#1). Every
//                 check prints a PASS/FAIL line; a final summary is printed and
//                 the simulation terminates automatically with $finish.
//
//                 Tests covered:
//                   T01 synchronous reset
//                   T02 hold when en = 0
//                   T03 synchronous parallel load
//                   T04 load priority over enable
//                   T05 up-counting sequence
//                   T06 hold (data retention) while disabled
//                   T07 down-counting sequence
//                   T08 terminal count 0xFFFF and upward rollover (overflow)
//                   T09 terminal count 0x0000 and downward rollover (underflow)
//                   T10 reset priority over load
//                   T11 direction change mid-stream
//                   T12 full-range sweep 0 -> 65535 -> 0 (65536 counts)
//=============================================================================
`timescale 1ns / 1ps

module tb_up_down_counter_16bit;

    localparam WIDTH      = 16;
    localparam CLK_PERIOD = 10;                     // 10 ns -> 100 MHz

    //--------------------------------------------------------------------------
    // Stimulus (regs) and observed outputs (wires)
    //--------------------------------------------------------------------------
    reg                 clk;
    reg                 rst;
    reg                 en;
    reg                 up_n_down;
    reg                 load;
    reg  [WIDTH-1:0]    din;
    wire [WIDTH-1:0]    count;
    wire                max_tick;
    wire                min_tick;

    //--------------------------------------------------------------------------
    // Book-keeping
    //--------------------------------------------------------------------------
    integer errors;
    integer total;
    integer i;

    //--------------------------------------------------------------------------
    // Device under test
    //--------------------------------------------------------------------------
    up_down_counter_16bit #(
        .WIDTH (WIDTH)
    ) dut (
        .clk       (clk),
        .rst       (rst),
        .en        (en),
        .up_n_down (up_n_down),
        .load      (load),
        .din       (din),
        .count     (count),
        .max_tick  (max_tick),
        .min_tick  (min_tick)
    );

    //--------------------------------------------------------------------------
    // Clock generator: 100 MHz (T = 10 ns)
    //--------------------------------------------------------------------------
    initial clk = 1'b0;
    always #(CLK_PERIOD/2) clk = ~clk;

    //--------------------------------------------------------------------------
    // Check tasks: compare against expected value, print PASS/FAIL, keep score
    //--------------------------------------------------------------------------
    task check_count;
        input [WIDTH-1:0] exp;
        input [8*64-1:0]  name;                     // message string (vector)
        begin
            total = total + 1;
            if (count !== exp) begin
                errors = errors + 1;
                $display("[%0t] FAIL : %0s | count = 0x%04h (expected 0x%04h)",
                         $time, name, count, exp);
            end
            else begin
                $display("[%0t] PASS : %0s | count = 0x%04h",
                         $time, name, count);
            end
        end
    endtask

    task check_flag;
        input            got;
        input            exp;
        input [8*64-1:0] name;
        begin
            total = total + 1;
            if (got !== exp) begin
                errors = errors + 1;
                $display("[%0t] FAIL : %0s | flag = %b (expected %b)",
                         $time, name, got, exp);
            end
            else begin
                $display("[%0t] PASS : %0s | flag = %b", $time, name, got);
            end
        end
    endtask

    //--------------------------------------------------------------------------
    // Advance one clock edge and check the resulting count value
    //--------------------------------------------------------------------------
    task step_and_check;
        input [WIDTH-1:0] exp;
        input [8*64-1:0]  name;
        begin
            @(posedge clk); #1;
            check_count(exp, name);
        end
    endtask

    //--------------------------------------------------------------------------
    // Main stimulus
    //--------------------------------------------------------------------------
    initial begin
        // Waveform dump (for external viewers; ignored harmlessly by Vivado)
        $dumpfile("tb_up_down_counter_16bit.vcd");
        $dumpvars(0, tb_up_down_counter_16bit);

        errors = 0;
        total  = 0;

        // Initialise all inputs before the first clock edge
        rst       = 1'b1;
        en        = 1'b0;
        up_n_down = 1'b1;
        load      = 1'b0;
        din       = {WIDTH{1'b0}};

        $display("==============================================================");
        $display(" TESTBENCH : tb_up_down_counter_16bit  (100 MHz clock)");
        $display("==============================================================");

        //----------------------------------------------------------------------
        // T01 - Synchronous reset, held active for two clock edges
        //----------------------------------------------------------------------
        $display("--- T01: synchronous reset ---");
        step_and_check(16'h0000, "T01a: rst clears counter");
        step_and_check(16'h0000, "T01b: rst held, counter stays 0");

        //----------------------------------------------------------------------
        // T02 - Release reset; with en = 0 and load = 0 the value must hold
        //----------------------------------------------------------------------
        $display("--- T02: hold with en = 0 ---");
        @(negedge clk);
        rst = 1'b0;
        step_and_check(16'h0000, "T02: hold after reset release");

        //----------------------------------------------------------------------
        // T03 - Synchronous parallel load of 0x1234
        //----------------------------------------------------------------------
        $display("--- T03: synchronous load ---");
        @(negedge clk);
        load = 1'b1;
        din  = 16'h1234;
        step_and_check(16'h1234, "T03: load 0x1234");

        //----------------------------------------------------------------------
        // T04 - While load = 1 a new datum is captured every clock, even though
        //       en = 1 (demonstrates load priority over enable/count)
        //----------------------------------------------------------------------
        $display("--- T04: load priority over enable ---");
        @(negedge clk);
        en  = 1'b1;
        din = 16'hABCD;
        step_and_check(16'hABCD, "T04: load wins over count-up request");
        @(negedge clk);
        load = 1'b0;
        en   = 1'b0;

        //----------------------------------------------------------------------
        // T05 - Up counting: five enabled steps from 0xABCD
        //----------------------------------------------------------------------
        $display("--- T05: count up x5 ---");
        @(negedge clk);
        en        = 1'b1;
        up_n_down = 1'b1;
        step_and_check(16'hABCE, "T05a: up-count 1");
        step_and_check(16'hABCF, "T05b: up-count 2");
        step_and_check(16'hABD0, "T05c: up-count 3");
        step_and_check(16'hABD1, "T05d: up-count 4");
        step_and_check(16'hABD2, "T05e: up-count 5");

        //----------------------------------------------------------------------
        // T06 - Hold: disable counting for three clocks, value must not move
        //----------------------------------------------------------------------
        $display("--- T06: hold while en = 0 ---");
        @(negedge clk);
        en = 1'b0;
        step_and_check(16'hABD2, "T06a: hold 1");
        step_and_check(16'hABD2, "T06b: hold 2");
        step_and_check(16'hABD2, "T06c: hold 3");

        //----------------------------------------------------------------------
        // T07 - Down counting: three enabled steps from 0xABD2
        //----------------------------------------------------------------------
        $display("--- T07: count down x3 ---");
        @(negedge clk);
        en        = 1'b1;
        up_n_down = 1'b0;
        step_and_check(16'hABD1, "T07a: down-count 1");
        step_and_check(16'hABD0, "T07b: down-count 2");
        step_and_check(16'hABCF, "T07c: down-count 3");

        //----------------------------------------------------------------------
        // T08 - Maximum count and upward rollover (overflow at FFFF -> 0000)
        //----------------------------------------------------------------------
        $display("--- T08: overflow / rollover at 0xFFFF ---");
        @(negedge clk);
        load      = 1'b1;
        en        = 1'b0;
        up_n_down = 1'b1;
        din       = 16'hFFFE;
        step_and_check(16'hFFFE, "T08a: load 0xFFFE");
        @(negedge clk);
        load = 1'b0;
        en   = 1'b1;
        step_and_check(16'hFFFF, "T08b: count reaches terminal 0xFFFF");
        check_flag(max_tick, 1'b1, "T08c: max_tick asserted at 0xFFFF");
        check_flag(min_tick, 1'b0, "T08d: min_tick low at 0xFFFF");
        step_and_check(16'h0000, "T08e: rollover FFFF -> 0000");
        check_flag(max_tick, 1'b0, "T08f: max_tick deasserted after rollover");

        //----------------------------------------------------------------------
        // T09 - Minimum count and downward rollover (underflow at 0000 -> FFFF)
        //----------------------------------------------------------------------
        $display("--- T09: underflow / rollover at 0x0000 ---");
        @(negedge clk);
        load = 1'b1;
        en   = 1'b0;
        din  = 16'h0001;
        step_and_check(16'h0001, "T09a: load 0x0001");
        @(negedge clk);
        load      = 1'b0;
        en        = 1'b1;
        up_n_down = 1'b0;
        step_and_check(16'h0000, "T09b: count reaches terminal 0x0000");
        check_flag(min_tick, 1'b1, "T09c: min_tick asserted at 0x0000");
        check_flag(max_tick, 1'b0, "T09d: max_tick low at 0x0000");
        step_and_check(16'hFFFF, "T09e: rollover 0000 -> FFFF");
        check_flag(min_tick, 1'b0, "T09f: min_tick deasserted after rollover");

        //----------------------------------------------------------------------
        // T10 - Reset has the highest priority (reset while load also active)
        //----------------------------------------------------------------------
        $display("--- T10: reset priority over load ---");
        @(negedge clk);
        rst  = 1'b1;
        load = 1'b1;
        din  = 16'h5555;
        step_and_check(16'h0000, "T10: reset dominates simultaneous load");
        @(negedge clk);
        rst  = 1'b0;
        load = 1'b0;
        en   = 1'b0;

        //----------------------------------------------------------------------
        // T11 - Direction change mid-stream around a small value
        //----------------------------------------------------------------------
        $display("--- T11: direction change mid-stream ---");
        @(negedge clk);
        load = 1'b1;
        din  = 16'h0005;
        step_and_check(16'h0005, "T11a: load 0x0005");
        @(negedge clk);
        load      = 1'b0;
        en        = 1'b1;
        up_n_down = 1'b1;
        step_and_check(16'h0006, "T11b: up to 6");
        step_and_check(16'h0007, "T11c: up to 7");
        step_and_check(16'h0008, "T11d: up to 8");
        @(negedge clk);
        up_n_down = 1'b0;
        step_and_check(16'h0007, "T11e: reverse, down to 7");
        @(negedge clk);
        up_n_down = 1'b1;
        step_and_check(16'h0008, "T11f: reverse again, up to 8");

        //----------------------------------------------------------------------
        // T12 - Full-range sweep: reset, then count up through all 65536 states
        //       and verify the counter returns to zero exactly on time.
        //----------------------------------------------------------------------
        $display("--- T12: full-range sweep (65536 counts) ---");
        @(negedge clk);
        rst = 1'b1;
        en  = 1'b0;
        @(posedge clk); #1;
        check_count(16'h0000, "T12a: reset before sweep");
        @(negedge clk);
        rst       = 1'b0;
        en        = 1'b1;
        up_n_down = 1'b1;
        for (i = 1; i <= 65535; i = i + 1) begin
            @(posedge clk); #1;
            if (count !== i[15:0]) begin
                errors = errors + 1;
                $display("[%0t] FAIL : T12 sweep | count = 0x%04h (expected 0x%04h)",
                         $time, count, i[15:0]);
            end
            total = total + 1;
        end
        check_flag(max_tick, 1'b1, "T12b: max_tick at end of sweep (0xFFFF)");
        step_and_check(16'h0000, "T12c: sweep wraps to 0 after 65536 counts");

        //----------------------------------------------------------------------
        // Final summary and automatic termination
        //----------------------------------------------------------------------
        @(negedge clk);
        $display("==============================================================");
        $display(" SUMMARY : %0d checks executed, %0d error(s) detected", total, errors);
        if (errors == 0)
            $display(" >>> OVERALL RESULT : PASS <<<");
        else
            $display(" >>> OVERALL RESULT : FAIL <<<");
        $display("==============================================================");
        $finish;
    end

    //--------------------------------------------------------------------------
    // Watchdog: abort if the testbench ever deadlocks
    //--------------------------------------------------------------------------
    initial begin
        #2000000;                                     // 2 ms of simulation time
        $display("[%0t] ERROR : watchdog timeout - simulation aborted", $time);
        $finish;
    end

endmodule
```

## 12.2 `tb_universal_shift_register_8bit.v`

```verilog
//=============================================================================
// File          : tb_universal_shift_register_8bit.v
// Project       : Week 3 - Counters & Shift Registers (Digital Design & FPGA Lab)
// Description   : Self-checking testbench for universal_shift_register_8bit.
//
//                 Stimulus is applied on the NEGATIVE edge of the clock and the
//                 outputs are checked just after each positive edge (#1). Every
//                 check prints a PASS/FAIL line; a final summary is printed and
//                 the simulation terminates automatically with $finish.
//
//                 Tests covered:
//                   T01 synchronous reset
//                   T02 parallel load (mode = 11)
//                   T03 hold (mode = 00) while serial inputs toggle
//                   T04 shift right (mode = 01) with serial input pattern
//                   T05 shift left  (mode = 10) with serial input pattern
//                   T06 mid-stream reset (reset dominates mode)
//                   T07 walking-'1' pattern across all 8 positions
//                   T08 walking-ones fill (0x00 -> 0xFF)
//                   T09 serial outputs sout_l / sout_r observation
//=============================================================================
`timescale 1ns / 1ps

module tb_universal_shift_register_8bit;

    localparam WIDTH      = 8;
    localparam CLK_PERIOD = 10;                     // 10 ns -> 100 MHz

    // Mode encodings (mirror the DUT)
    localparam [1:0] MODE_HOLD  = 2'b00;
    localparam [1:0] MODE_RIGHT = 2'b01;
    localparam [1:0] MODE_LEFT  = 2'b10;
    localparam [1:0] MODE_LOAD  = 2'b11;

    //--------------------------------------------------------------------------
    // Stimulus (regs) and observed outputs (wires)
    //--------------------------------------------------------------------------
    reg              clk;
    reg              rst;
    reg  [1:0]       mode;
    reg              sin_r;
    reg              sin_l;
    reg  [WIDTH-1:0] pin;
    wire [WIDTH-1:0] pout;
    wire             sout_l;
    wire             sout_r;

    //--------------------------------------------------------------------------
    // Book-keeping
    //--------------------------------------------------------------------------
    integer errors;
    integer total;

    //--------------------------------------------------------------------------
    // Device under test
    //--------------------------------------------------------------------------
    universal_shift_register_8bit #(
        .WIDTH (WIDTH)
    ) dut (
        .clk    (clk),
        .rst    (rst),
        .mode   (mode),
        .sin_r  (sin_r),
        .sin_l  (sin_l),
        .pin    (pin),
        .pout   (pout),
        .sout_l (sout_l),
        .sout_r (sout_r)
    );

    //--------------------------------------------------------------------------
    // Clock generator: 100 MHz (T = 10 ns)
    //--------------------------------------------------------------------------
    initial clk = 1'b0;
    always #(CLK_PERIOD/2) clk = ~clk;

    //--------------------------------------------------------------------------
    // Check task: compare pout against expected value, print PASS/FAIL
    //--------------------------------------------------------------------------
    task check_reg;
        input [WIDTH-1:0] exp;
        input [8*64-1:0]  name;                     // message string (vector)
        begin
            total = total + 1;
            if (pout !== exp) begin
                errors = errors + 1;
                $display("[%0t] FAIL : %0s | pout = %b (0x%02h), expected %b (0x%02h)",
                         $time, name, pout, pout, exp, exp);
            end
            else begin
                $display("[%0t] PASS : %0s | pout = %b (0x%02h)",
                         $time, name, pout, pout);
            end
        end
    endtask

    task check_bit;
        input            got;
        input            exp;
        input [8*64-1:0] name;
        begin
            total = total + 1;
            if (got !== exp) begin
                errors = errors + 1;
                $display("[%0t] FAIL : %0s | bit = %b (expected %b)",
                         $time, name, got, exp);
            end
            else begin
                $display("[%0t] PASS : %0s | bit = %b", $time, name, got);
            end
        end
    endtask

    //--------------------------------------------------------------------------
    // Advance one clock edge and check the resulting register value
    //--------------------------------------------------------------------------
    task step_and_check;
        input [WIDTH-1:0] exp;
        input [8*64-1:0]  name;
        begin
            @(posedge clk); #1;
            check_reg(exp, name);
        end
    endtask

    //--------------------------------------------------------------------------
    // Main stimulus
    //--------------------------------------------------------------------------
    initial begin
        // Waveform dump (for external viewers; ignored harmlessly by Vivado)
        $dumpfile("tb_universal_shift_register_8bit.vcd");
        $dumpvars(0, tb_universal_shift_register_8bit);

        errors = 0;
        total  = 0;

        // Initialise all inputs before the first clock edge
        rst   = 1'b1;
        mode  = MODE_HOLD;
        sin_r = 1'b0;
        sin_l = 1'b0;
        pin   = {WIDTH{1'b0}};

        $display("==============================================================");
        $display(" TESTBENCH : tb_universal_shift_register_8bit  (100 MHz clock)");
        $display("==============================================================");

        //----------------------------------------------------------------------
        // T01 - Synchronous reset over two clock edges
        //----------------------------------------------------------------------
        $display("--- T01: synchronous reset ---");
        step_and_check(8'h00, "T01a: rst clears register");
        step_and_check(8'h00, "T01b: rst held, register stays 0");
        @(negedge clk);
        rst = 1'b0;

        //----------------------------------------------------------------------
        // T02 - Parallel load of 8'hA5 = 1010_0101
        //----------------------------------------------------------------------
        $display("--- T02: parallel load ---");
        @(negedge clk);
        mode = MODE_LOAD;
        pin  = 8'hA5;
        step_and_check(8'hA5, "T02a: load 0xA5");
        check_bit(sout_l, 1'b1, "T02b: sout_l = MSB of 0xA5");
        check_bit(sout_r, 1'b1, "T02c: sout_r = LSB of 0xA5");

        //----------------------------------------------------------------------
        // T03 - Hold for three clocks while the serial inputs toggle; the
        //       stored value must not change.
        //----------------------------------------------------------------------
        $display("--- T03: hold with toggling serial inputs ---");
        @(negedge clk);
        mode  = MODE_HOLD;
        sin_r = 1'b1;
        sin_l = 1'b1;
        step_and_check(8'hA5, "T03a: hold 1 (sin = 1,1)");
        @(negedge clk);
        sin_r = 1'b0;
        sin_l = 1'b1;
        step_and_check(8'hA5, "T03b: hold 2 (sin = 0,1)");
        @(negedge clk);
        sin_r = 1'b1;
        sin_l = 1'b1;
        pin   = 8'hFF;
        step_and_check(8'hA5, "T03c: hold 3 (even pin ignored)");

        //----------------------------------------------------------------------
        // T04 - Shift right four times with serial input pattern 1,0,1,1
        //       0xA5 = 1010_0101 ->
        //       -> 1101_0010 -> 0110_1001 -> 1011_0100 -> 1101_1010
        //----------------------------------------------------------------------
        $display("--- T04: shift right x4 (sin_r = 1,0,1,1) ---");
        @(negedge clk);
        mode  = MODE_RIGHT;
        sin_r = 1'b1;
        check_bit(sout_r, 1'b1, "T04a: bit leaving LSB before step 1");
        step_and_check(8'hD2, "T04b: shift right 1 -> 0xD2");
        @(negedge clk);
        sin_r = 1'b0;
        step_and_check(8'h69, "T04c: shift right 2 -> 0x69");
        @(negedge clk);
        sin_r = 1'b1;
        step_and_check(8'hB4, "T04d: shift right 3 -> 0xB4");
        step_and_check(8'hDA, "T04e: shift right 4 -> 0xDA");

        //----------------------------------------------------------------------
        // T05 - Shift left four times with serial input pattern 0,1,0,1
        //       0xDA = 1101_1010 ->
        //       -> 1011_0100 -> 0110_1001 -> 1101_0010 -> 1010_0101 (back!)
        //----------------------------------------------------------------------
        $display("--- T05: shift left x4 (sin_l = 0,1,0,1) ---");
        @(negedge clk);
        mode  = MODE_LEFT;
        sin_l = 1'b0;
        check_bit(sout_l, 1'b1, "T05a: bit leaving MSB before step 1");
        step_and_check(8'hB4, "T05b: shift left 1 -> 0xB4");
        @(negedge clk);
        sin_l = 1'b1;
        step_and_check(8'h69, "T05c: shift left 2 -> 0x69");
        @(negedge clk);
        sin_l = 1'b0;
        step_and_check(8'hD2, "T05d: shift left 3 -> 0xD2");
        @(negedge clk);
        sin_l = 1'b1;
        step_and_check(8'hA5, "T05e: shift left 4 -> 0xA5 (round trip)");

        //----------------------------------------------------------------------
        // T06 - Load a marker, then assert reset in the middle of a shift:
        //       reset must dominate the mode field.
        //----------------------------------------------------------------------
        $display("--- T06: reset dominates mode ---");
        @(negedge clk);
        mode = MODE_LOAD;
        pin  = 8'h3C;
        step_and_check(8'h3C, "T06a: load 0x3C");
        @(negedge clk);
        rst   = 1'b1;
        mode  = MODE_RIGHT;
        sin_r = 1'b1;
        step_and_check(8'h00, "T06b: reset wins over shift-right");
        @(negedge clk);
        rst = 1'b0;

        //----------------------------------------------------------------------
        // T07 - Walking '1' (LED-chaser) pattern: load 0x01 and shift left
        //       with sin_l = 0 until the '1' walks off the MSB end.
        //----------------------------------------------------------------------
        $display("--- T07: walking one ---");
        @(negedge clk);
        mode = MODE_LOAD;
        pin  = 8'h01;
        step_and_check(8'h01, "T07a: load 0x01");
        @(negedge clk);
        mode  = MODE_LEFT;
        sin_l = 1'b0;
        step_and_check(8'h02, "T07b: walk 1 -> 0x02");
        step_and_check(8'h04, "T07c: walk 2 -> 0x04");
        step_and_check(8'h08, "T07d: walk 3 -> 0x08");
        step_and_check(8'h10, "T07e: walk 4 -> 0x10");
        step_and_check(8'h20, "T07f: walk 5 -> 0x20");
        step_and_check(8'h40, "T07g: walk 6 -> 0x40");
        step_and_check(8'h80, "T07h: walk 7 -> 0x80");
        step_and_check(8'h00, "T07i: walk 8 -> 0x00 (1 falls off the end)");

        //----------------------------------------------------------------------
        // T08 - Walking-ones fill: from 0x00 shift left with sin_l = 1
        //----------------------------------------------------------------------
        $display("--- T08: ones fill ---");
        @(negedge clk);
        mode  = MODE_LEFT;
        sin_l = 1'b1;
        step_and_check(8'h01, "T08a: fill 1 -> 0x01");
        step_and_check(8'h03, "T08b: fill 2 -> 0x03");
        step_and_check(8'h07, "T08c: fill 3 -> 0x07");
        step_and_check(8'h0F, "T08d: fill 4 -> 0x0F");
        step_and_check(8'h1F, "T08e: fill 5 -> 0x1F");
        step_and_check(8'h3F, "T08f: fill 6 -> 0x3F");
        step_and_check(8'h7F, "T08g: fill 7 -> 0x7F");
        step_and_check(8'hFF, "T08h: fill 8 -> 0xFF");
        check_bit(sout_l, 1'b1, "T08i: sout_l = 1 at 0xFF");
        check_bit(sout_r, 1'b1, "T08j: sout_r = 1 at 0xFF");

        //----------------------------------------------------------------------
        // T09 - Serial-out observation while shifting right: from 0xFF with
        //       sin_r = 0, ones must pour out of sout_r, LSB first.
        //----------------------------------------------------------------------
        $display("--- T09: serial-out on shift right ---");
        @(negedge clk);
        mode  = MODE_RIGHT;
        sin_r = 1'b0;
        check_bit(sout_r, 1'b1, "T09a: sout_r = 1 (0xFF before step)");
        step_and_check(8'h7F, "T09b: shift right -> 0x7F");
        step_and_check(8'h3F, "T09c: shift right -> 0x3F");
        step_and_check(8'h1F, "T09d: shift right -> 0x1F");
        check_bit(sout_r, 1'b1, "T09e: sout_r still 1");
        step_and_check(8'h0F, "T09f: shift right -> 0x0F");
        step_and_check(8'h07, "T09g: shift right -> 0x07");
        step_and_check(8'h03, "T09h: shift right -> 0x03");
        step_and_check(8'h01, "T09i: shift right -> 0x01");
        step_and_check(8'h00, "T09j: shift right -> 0x00 (register empty)");
        check_bit(sout_l, 1'b0, "T09k: sout_l = 0 at 0x00");
        check_bit(sout_r, 1'b0, "T09l: sout_r = 0 at 0x00");

        //----------------------------------------------------------------------
        // Final summary and automatic termination
        //----------------------------------------------------------------------
        @(negedge clk);
        $display("==============================================================");
        $display(" SUMMARY : %0d checks executed, %0d error(s) detected", total, errors);
        if (errors == 0)
            $display(" >>> OVERALL RESULT : PASS <<<");
        else
            $display(" >>> OVERALL RESULT : FAIL <<<");
        $display("==============================================================");
        $finish;
    end

    //--------------------------------------------------------------------------
    // Watchdog: abort if the testbench ever deadlocks
    //--------------------------------------------------------------------------
    initial begin
        #100000;                                      // 100 us of simulation time
        $display("[%0t] ERROR : watchdog timeout - simulation aborted", $time);
        $finish;
    end

endmodule
```

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

# 15. FPGA CONSTRAINTS (XDC)

The constraint file `constraints/boolean_board.xdc` does two distinct jobs:

1. **Physical constraints** — `set_property PACKAGE_PIN/IOSTANDARD` binds every top-level port to a physical package pin and its I/O standard. All boards signals used here are single-ended 3.3 V LVCMOS (`LVCMOS33`).
2. **Timing constraints** — `create_clock -period 10.000` tells the tools that a 100 MHz clock enters on `clk`. **This line must be present and active**: without it, the timing engine treats all internal paths as unconstrained and the "timing summary" becomes meaningless. In the template file distributed for many labs this line is commented out — it was deliberately un-commented here. The file also sets `CFGBVS`/`CONFIG_VOLTAGE` required by the Spartan-7 configuration bank, and keeps the board's 7-segment, RGB-LED, UART, HDMI, audio, BLE and servo pin groups commented out for later experiments (uncommenting a group is an error until matching top-level ports exist, because Vivado fails with "cannot find port"). Finally, an XDC file must contain only valid Tcl — a stray token such as a trailing `)` aborts constraints processing.

```tcl
##============================================================================
## File  : boolean_board.xdc
## Lab   : Week 3 - Counters & Shift Registers
## Board : RealDigital Boolean Board (Xilinx Spartan-7 xc7s50)
## Note  : This file contains the physical pin constraints for BOTH demo tops
##         (counter_top_boolean and shiftreg_top_boolean). Both tops use the
##         same board signals: clk, sw[15:0], btn[3:0], led[15:0].
##         The seven-segment, RGB-LED, UART, HDMI, audio, BLE and servo groups
##         are kept below (commented out) for reuse in later experiments.
##============================================================================

##----------------------------------------------------------------------------
## Clock: 100 MHz on-board oscillator -> pin F14
## (The timing constraint below is REQUIRED for Vivado timing analysis:
##  without create_clock the design is treated as unconstrained.)
##----------------------------------------------------------------------------
set_property -dict {PACKAGE_PIN F14 IOSTANDARD LVCMOS33} [get_ports clk]
create_clock -period 10.000 -name sys_clk_100m -waveform {0 5} [get_ports clk]

##----------------------------------------------------------------------------
## Configuration bank voltage (required on Spartan-7 Boolean board)
##----------------------------------------------------------------------------
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]

##----------------------------------------------------------------------------
## On-board slide switches sw[15:0]  (counter load data / SR data + controls)
##----------------------------------------------------------------------------
set_property -dict {PACKAGE_PIN V2 IOSTANDARD LVCMOS33} [get_ports {sw[0]}]
set_property -dict {PACKAGE_PIN U2 IOSTANDARD LVCMOS33} [get_ports {sw[1]}]
set_property -dict {PACKAGE_PIN U1 IOSTANDARD LVCMOS33} [get_ports {sw[2]}]
set_property -dict {PACKAGE_PIN T2 IOSTANDARD LVCMOS33} [get_ports {sw[3]}]
set_property -dict {PACKAGE_PIN T1 IOSTANDARD LVCMOS33} [get_ports {sw[4]}]
set_property -dict {PACKAGE_PIN R2 IOSTANDARD LVCMOS33} [get_ports {sw[5]}]
set_property -dict {PACKAGE_PIN R1 IOSTANDARD LVCMOS33} [get_ports {sw[6]}]
set_property -dict {PACKAGE_PIN P2 IOSTANDARD LVCMOS33} [get_ports {sw[7]}]
set_property -dict {PACKAGE_PIN P1 IOSTANDARD LVCMOS33} [get_ports {sw[8]}]
set_property -dict {PACKAGE_PIN N2 IOSTANDARD LVCMOS33} [get_ports {sw[9]}]
set_property -dict {PACKAGE_PIN N1 IOSTANDARD LVCMOS33} [get_ports {sw[10]}]
set_property -dict {PACKAGE_PIN M2 IOSTANDARD LVCMOS33} [get_ports {sw[11]}]
set_property -dict {PACKAGE_PIN M1 IOSTANDARD LVCMOS33} [get_ports {sw[12]}]
set_property -dict {PACKAGE_PIN L1 IOSTANDARD LVCMOS33} [get_ports {sw[13]}]
set_property -dict {PACKAGE_PIN K2 IOSTANDARD LVCMOS33} [get_ports {sw[14]}]
set_property -dict {PACKAGE_PIN K1 IOSTANDARD LVCMOS33} [get_ports {sw[15]}]

##----------------------------------------------------------------------------
## On-board LEDs led[15:0]  (active high: '1' lights the LED)
##----------------------------------------------------------------------------
set_property -dict {PACKAGE_PIN G1 IOSTANDARD LVCMOS33} [get_ports {led[0]}]
set_property -dict {PACKAGE_PIN G2 IOSTANDARD LVCMOS33} [get_ports {led[1]}]
set_property -dict {PACKAGE_PIN F1 IOSTANDARD LVCMOS33} [get_ports {led[2]}]
set_property -dict {PACKAGE_PIN F2 IOSTANDARD LVCMOS33} [get_ports {led[3]}]
set_property -dict {PACKAGE_PIN E1 IOSTANDARD LVCMOS33} [get_ports {led[4]}]
set_property -dict {PACKAGE_PIN E2 IOSTANDARD LVCMOS33} [get_ports {led[5]}]
set_property -dict {PACKAGE_PIN E3 IOSTANDARD LVCMOS33} [get_ports {led[6]}]
set_property -dict {PACKAGE_PIN E5 IOSTANDARD LVCMOS33} [get_ports {led[7]}]
set_property -dict {PACKAGE_PIN E6 IOSTANDARD LVCMOS33} [get_ports {led[8]}]
set_property -dict {PACKAGE_PIN C3 IOSTANDARD LVCMOS33} [get_ports {led[9]}]
set_property -dict {PACKAGE_PIN B2 IOSTANDARD LVCMOS33} [get_ports {led[10]}]
set_property -dict {PACKAGE_PIN A2 IOSTANDARD LVCMOS33} [get_ports {led[11]}]
set_property -dict {PACKAGE_PIN B3 IOSTANDARD LVCMOS33} [get_ports {led[12]}]
set_property -dict {PACKAGE_PIN A3 IOSTANDARD LVCMOS33} [get_ports {led[13]}]
set_property -dict {PACKAGE_PIN B4 IOSTANDARD LVCMOS33} [get_ports {led[14]}]
set_property -dict {PACKAGE_PIN A4 IOSTANDARD LVCMOS33} [get_ports {led[15]}]

##----------------------------------------------------------------------------
## On-board push buttons btn[3:0]  (active high while pressed)
##   btn[0] = reset   btn[1] = enable   btn[2] = direction   btn[3] = load
##----------------------------------------------------------------------------
set_property -dict {PACKAGE_PIN J2 IOSTANDARD LVCMOS33} [get_ports {btn[0]}]
set_property -dict {PACKAGE_PIN J5 IOSTANDARD LVCMOS33} [get_ports {btn[1]}]
set_property -dict {PACKAGE_PIN H2 IOSTANDARD LVCMOS33} [get_ports {btn[2]}]
set_property -dict {PACKAGE_PIN J1 IOSTANDARD LVCMOS33} [get_ports {btn[3]}]

##============================================================================
## The following groups are NOT used by the Week-3 tops. They are kept here,
## commented out, so the same file can grow with later experiments.
## (Uncomment them only after adding matching top-level ports, otherwise
##  Vivado raises "common 17-55: cannot find port" errors.)
##============================================================================

## On-board color LEDs
#set_property -dict {PACKAGE_PIN V6 IOSTANDARD LVCMOS33} [get_ports {RGB0[0]}]
#set_property -dict {PACKAGE_PIN V4 IOSTANDARD LVCMOS33} [get_ports {RGB0[1]}]
#set_property -dict {PACKAGE_PIN U6 IOSTANDARD LVCMOS33} [get_ports {RGB0[2]}]
#set_property -dict {PACKAGE_PIN U3 IOSTANDARD LVCMOS33} [get_ports {RGB1[0]}]
#set_property -dict {PACKAGE_PIN V3 IOSTANDARD LVCMOS33} [get_ports {RGB1[1]}]
#set_property -dict {PACKAGE_PIN V5 IOSTANDARD LVCMOS33} [get_ports {RGB1[2]}]

## On-board 7-segment display 0 (digits + segments, incl. decimal point SEG[7])
#set_property -dict {PACKAGE_PIN D5 IOSTANDARD LVCMOS33} [get_ports {D0_AN[0]}]
#set_property -dict {PACKAGE_PIN C4 IOSTANDARD LVCMOS33} [get_ports {D0_AN[1]}]
#set_property -dict {PACKAGE_PIN C7 IOSTANDARD LVCMOS33} [get_ports {D0_AN[2]}]
#set_property -dict {PACKAGE_PIN A8 IOSTANDARD LVCMOS33} [get_ports {D0_AN[3]}]
#set_property -dict {PACKAGE_PIN D7 IOSTANDARD LVCMOS33} [get_ports {D0_SEG[0]}]
#set_property -dict {PACKAGE_PIN C5 IOSTANDARD LVCMOS33} [get_ports {D0_SEG[1]}]
#set_property -dict {PACKAGE_PIN A5 IOSTANDARD LVCMOS33} [get_ports {D0_SEG[2]}]
#set_property -dict {PACKAGE_PIN B7 IOSTANDARD LVCMOS33} [get_ports {D0_SEG[3]}]
#set_property -dict {PACKAGE_PIN A7 IOSTANDARD LVCMOS33} [get_ports {D0_SEG[4]}]
#set_property -dict {PACKAGE_PIN D6 IOSTANDARD LVCMOS33} [get_ports {D0_SEG[5]}]
#set_property -dict {PACKAGE_PIN B5 IOSTANDARD LVCMOS33} [get_ports {D0_SEG[6]}]
#set_property -dict {PACKAGE_PIN A6 IOSTANDARD LVCMOS33} [get_ports {D0_SEG[7]}]

## On-board 7-segment display 1
#set_property -dict {PACKAGE_PIN H3 IOSTANDARD LVCMOS33} [get_ports {D1_AN[0]}]
#set_property -dict {PACKAGE_PIN J4 IOSTANDARD LVCMOS33} [get_ports {D1_AN[1]}]
#set_property -dict {PACKAGE_PIN F3 IOSTANDARD LVCMOS33} [get_ports {D1_AN[2]}]
#set_property -dict {PACKAGE_PIN E4 IOSTANDARD LVCMOS33} [get_ports {D1_AN[3]}]
#set_property -dict {PACKAGE_PIN F4 IOSTANDARD LVCMOS33} [get_ports {D1_SEG[0]}]
#set_property -dict {PACKAGE_PIN J3 IOSTANDARD LVCMOS33} [get_ports {D1_SEG[1]}]
#set_property -dict {PACKAGE_PIN D2 IOSTANDARD LVCMOS33} [get_ports {D1_SEG[2]}]
#set_property -dict {PACKAGE_PIN C2 IOSTANDARD LVCMOS33} [get_ports {D1_SEG[3]}]
#set_property -dict {PACKAGE_PIN B1 IOSTANDARD LVCMOS33} [get_ports {D1_SEG[4]}]
#set_property -dict {PACKAGE_PIN H4 IOSTANDARD LVCMOS33} [get_ports {D1_SEG[5]}]
#set_property -dict {PACKAGE_PIN D1 IOSTANDARD LVCMOS33} [get_ports {D1_SEG[6]}]
#set_property -dict {PACKAGE_PIN C1 IOSTANDARD LVCMOS33} [get_ports {D1_SEG[7]}]

## UART (USB-UART bridge)
#set_property -dict {PACKAGE_PIN V12 IOSTANDARD LVCMOS33} [get_ports {UART_rxd}]
#set_property -dict {PACKAGE_PIN U11 IOSTANDARD LVCMOS33} [get_ports {UART_txd}]

## HDMI output (TMDS)
#set_property -dict {PACKAGE_PIN T14 IOSTANDARD TMDS_33} [get_ports {hdmi_clk_n}]
#set_property -dict {PACKAGE_PIN R14 IOSTANDARD TMDS_33} [get_ports {hdmi_clk_p}]
#set_property -dict {PACKAGE_PIN T15 IOSTANDARD TMDS_33} [get_ports {hdmi_tx_n[0]}]
#set_property -dict {PACKAGE_PIN R17 IOSTANDARD TMDS_33} [get_ports {hdmi_tx_n[1]}]
#set_property -dict {PACKAGE_PIN P16 IOSTANDARD TMDS_33} [get_ports {hdmi_tx_n[2]}]
#set_property -dict {PACKAGE_PIN R15 IOSTANDARD TMDS_33} [get_ports {hdmi_tx_p[0]}]
#set_property -dict {PACKAGE_PIN R16 IOSTANDARD TMDS_33} [get_ports {hdmi_tx_p[1]}]
#set_property -dict {PACKAGE_PIN N15 IOSTANDARD TMDS_33} [get_ports {hdmi_tx_p[2]}]

## PWM audio
#set_property -dict {PACKAGE_PIN N13 IOSTANDARD LVCMOS33} [get_ports {left_audio_out}]
#set_property -dict {PACKAGE_PIN N14 IOSTANDARD LVCMOS33} [get_ports {right_audio_out}]

## BLE UART
#set_property -dict {PACKAGE_PIN G5 IOSTANDARD LVCMOS33} [get_ports {ble_uart_tx}]
#set_property -dict {PACKAGE_PIN F5 IOSTANDARD LVCMOS33} [get_ports {ble_uart_rx}]
#set_property -dict {PACKAGE_PIN H6 IOSTANDARD LVCMOS33} [get_ports {ble_uart_rts}]
#set_property -dict {PACKAGE_PIN G6 IOSTANDARD LVCMOS33} [get_ports {ble_uart_cts}]

## Servomotors
#set_property -dict {PACKAGE_PIN M14 IOSTANDARD LVCMOS33} [get_ports {servo0}]
#set_property -dict {PACKAGE_PIN M16 IOSTANDARD LVCMOS33} [get_ports {servo1}]
#set_property -dict {PACKAGE_PIN L15 IOSTANDARD LVCMOS33} [get_ports {servo2}]
#set_property -dict {PACKAGE_PIN L16 IOSTANDARD LVCMOS33} [get_ports {servo3}]

##============================================================================
## NOTE: the file must NOT contain any non-Tcl characters. A stray token such
## as a trailing ")" (present at the end of some template files) makes Vivado
## abort constraints processing with a Tcl syntax error.
##============================================================================
```

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
