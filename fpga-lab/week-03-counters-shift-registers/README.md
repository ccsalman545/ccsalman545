# Week 3 — Counters & Shift Registers

Digital Design & FPGA Laboratory, M.Sc. Electronics (CUSAT)
Board: **RealDigital Boolean Board** (Xilinx Spartan-7, xc7s50) · Tool: **Vivado Design Suite** · HDL: **Verilog-2001**

## Contents

| Path | What it is |
|---|---|
| `report/Week3_Counters_and_Shift_Registers_Lab_Report.md` | Full 28-section lab report (Markdown, ~25–35 pp when set in 12 pt / 1.5 spacing) |
| `report/Week3_Counters_and_Shift_Registers_Lab_Report.docx` | Same report as a Word document (TOC + page breaks) |
| `rtl/up_down_counter_16bit.v` | 16-bit synchronous up/down counter: sync reset, sync load, enable, direction, `max_tick`/`min_tick` |
| `rtl/universal_shift_register_8bit.v` | 8-bit universal shift register: hold / shift right / shift left / parallel load (74x194-style mode field) |
| `rtl/clock_enable_gen.v` | 2 Hz tick generator (single-clock-domain "slow clock", used for eye-visible demos) |
| `rtl/counter_top_boolean.v` | Board top: counter on 16 LEDs, sw = load data, btn[0..3] = rst/en/dir/load |
| `rtl/shiftreg_top_boolean.v` | Board top: shift register on led[7:0], sw controls |
| `tb/tb_up_down_counter_16bit.v` | Self-checking testbench — 65,573 checks incl. full 65,536-state sweep |
| `tb/tb_universal_shift_register_8bit.v` | Self-checking testbench — 51 checks over all four modes |
| `constraints/boolean_board.xdc` | Boolean board XDC (clk F14 + `create_clock`, sw/btn/led; 7-seg/UART/HDMI/etc. kept commented) |
| `tools/parse_check.py` | Two-stage static check: pyverilog grammar parse + structural lint |
| `tools/twin_verify.py` | Cycle-accurate Python twin replaying both TB stimulus sets (90/90 PASS) |
| `tools/gen_logs.py` | Regenerates the expected XSim console transcripts used in the report |
| `tools/assemble_report.py` | Rebuilds the Markdown report, injecting code listings straight from the source files |

## Quick start (Vivado)

1. Create an RTL project for part `xc7s50csga324-1` (Boolean board).
2. Add `rtl/*.v` as Design Sources, `tb/*.v` as Simulation Sources, `constraints/boolean_board.xdc` as constraints.
3. Set `tb_up_down_counter_16bit` (later `tb_universal_shift_register_8bit`) as sim top → **Run Behavioral Simulation** → expect `>>> OVERALL RESULT : PASS <<<`.
4. Set `counter_top_boolean` (or `shiftreg_top_boolean`) as top → **Generate Bitstream** → program via Hardware Manager.
5. Counter demo: `btn[0]` reset · `btn[1]` hold-to-count · `btn[2]` hold-to-count-down · `btn[3]` load `sw[15:0]` · LEDs show the 16-bit count at 2 Hz.
   Shift-register demo: `btn[0]` reset · `sw[1:0]` mode (00 hold · 01 right · 10 left · 11 load) · `sw[9:2]` parallel data · `sw[10]`/`sw[11]` serial in · `led[15:14]` serial out.

## Verification status

- All 7 Verilog files pass grammar parse + structural lint (`tools/parse_check.py`).
- Cycle-accurate twin replays of both testbenches: **90/90 checks PASS** (`tools/twin_verify.py`), including the complete 65,536-count full-range sweep.
- Expected XSim transcripts (with exact ns timestamps) are reproducible via `tools/gen_logs.py`.
