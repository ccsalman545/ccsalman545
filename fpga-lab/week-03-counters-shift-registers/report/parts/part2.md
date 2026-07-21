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
