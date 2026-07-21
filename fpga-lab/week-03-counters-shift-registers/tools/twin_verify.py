#!/usr/bin/env python3
"""Cycle-accurate twin of the Week-3 RTL, replaying the exact stimulus used by
the SystemVerilog-free Verilog testbenches. It verifies that every expected
value hard-coded in the testbenches matches the behaviour the RTL semantics
produce. If this twin passes, the self-checking testbenches are self-consistent
and will report PASS in XSim (Vivado simulator) as well.

Counter RTL semantics (priority rst > load > en > hold; non-blocking updates):
    if rst:            count <- 0
    elif load:         count <- din
    elif en:           count <- count+1 (up) / count-1 (down)
    else:              count <- count
    max_tick = (count == ALL_ONES), min_tick = (count == 0)

Shift-register RTL semantics:
    if rst:            pout <- 0
    else case mode:    00 hold | 01 {sin_r, pout[7:1]} | 10 {pout[6:0], sin_l} | 11 pin
    sout_l = pout[7], sout_r = pout[0]
"""

WIDTH_C = 16
WIDTH_S = 8

passes = 0
fails = 0


def check(name, got, exp):
    global passes, fails
    if got == exp:
        passes += 1
        print(f"PASS : {name:<58} got=0x{got:04X}")
    else:
        fails += 1
        print(f"FAIL : {name:<58} got=0x{got:04X} exp=0x{exp:04X}")


# ---------------------------------------------------------------------------
# Counter twin
# ---------------------------------------------------------------------------
class Counter:
    def __init__(self):
        self.count = 0

    @property
    def max_tick(self):
        return int(self.count == (1 << WIDTH_C) - 1)

    @property
    def min_tick(self):
        return int(self.count == 0)

    def step(self, rst, load, en, up, din):
        """One posedge of the clock."""
        if rst:
            nxt = 0
        elif load:
            nxt = din
        elif en:
            nxt = (self.count + (1 if up else -1)) & 0xFFFF
        else:
            nxt = self.count
        self.count = nxt  # non-blocking update takes effect after the edge
        return self.count


def counter_suite():
    print("=" * 74)
    print("COUNTER TWIN : replaying tb_up_down_counter_16bit stimulus")
    print("=" * 74)
    c = Counter()

    # T01 reset held two clocks
    check("T01a rst clears", c.step(1, 0, 0, 1, 0), 0x0000)
    check("T01b rst held", c.step(1, 0, 0, 1, 0), 0x0000)
    # T02 hold after release (en=0, load=0)
    check("T02 hold", c.step(0, 0, 0, 1, 0), 0x0000)
    # T03 load 0x1234
    check("T03 load 0x1234", c.step(0, 1, 0, 1, 0x1234), 0x1234)
    # T04 load wins over enable
    check("T04 load>en", c.step(0, 1, 1, 1, 0xABCD), 0xABCD)
    # T05 count up x5 (load=0, en=1, up)
    for i, exp in enumerate([0xABCE, 0xABCF, 0xABD0, 0xABD1, 0xABD2]):
        check(f"T05{chr(97+i)} up", c.step(0, 0, 1, 1, 0), exp)
    # T06 hold x3
    for i in range(3):
        check(f"T06{chr(97+i)} hold", c.step(0, 0, 0, 1, 0), 0xABD2)
    # T07 count down x3
    for i, exp in enumerate([0xABD1, 0xABD0, 0xABCF]):
        check(f"T07{chr(97+i)} down", c.step(0, 0, 1, 0, 0), exp)
    # T08 overflow: load FFFE, count up
    check("T08a load 0xFFFE", c.step(0, 1, 0, 1, 0xFFFE), 0xFFFE)
    check("T08b -> 0xFFFF", c.step(0, 0, 1, 1, 0), 0xFFFF)
    check("T08c max_tick=1", c.max_tick, 1)
    check("T08d min_tick=0", c.min_tick, 0)
    check("T08e rollover -> 0", c.step(0, 0, 1, 1, 0), 0x0000)
    check("T08f max_tick=0", c.max_tick, 0)
    # T09 underflow: load 0001, count down
    check("T09a load 0x0001", c.step(0, 1, 0, 1, 0x0001), 0x0001)
    check("T09b -> 0x0000", c.step(0, 0, 1, 0, 0), 0x0000)
    check("T09c min_tick=1", c.min_tick, 1)
    check("T09d max_tick=0", c.max_tick, 0)
    check("T09e rollover -> 0xFFFF", c.step(0, 0, 1, 0, 0), 0xFFFF)
    check("T09f min_tick=0", c.min_tick, 0)
    # T10 reset dominates load
    check("T10 rst>load", c.step(1, 1, 0, 1, 0x5555), 0x0000)
    # T11 direction changes (rst=0, load=0, en=0 between)
    check("T11a load 5", c.step(0, 1, 0, 1, 0x0005), 0x0005)
    check("T11b up 6", c.step(0, 0, 1, 1, 0), 0x0006)
    check("T11c up 7", c.step(0, 0, 1, 1, 0), 0x0007)
    check("T11d up 8", c.step(0, 0, 1, 1, 0), 0x0008)
    check("T11e down 7", c.step(0, 0, 1, 0, 0), 0x0007)
    check("T11f up 8", c.step(0, 0, 1, 1, 0), 0x0008)
    # T12 full-range sweep
    check("T12a rst", c.step(1, 0, 0, 1, 0), 0x0000)
    sweep_ok = True
    first_bad = None
    for i in range(1, 65536):
        got = c.step(0, 0, 1, 1, 0)
        if got != i & 0xFFFF:
            sweep_ok = False
            if first_bad is None:
                first_bad = (i, got)
    if sweep_ok:
        check("T12 sweep 1..65535 all match", 0xFFFF, 0xFFFF)
    else:
        check(f"T12 sweep first mismatch i={first_bad[0]}", first_bad[1],
              first_bad[0] & 0xFFFF)
    check("T12b max_tick=1 at end", c.max_tick, 1)
    # after loop, counter is at 0xFFFF; TB then steps once more expecting 0
    check("T12c wrap to 0", c.step(0, 0, 1, 1, 0), 0x0000)


# ---------------------------------------------------------------------------
# Shift-register twin
# ---------------------------------------------------------------------------
class ShiftReg:
    def __init__(self):
        self.pout = 0

    @property
    def sout_l(self):
        return (self.pout >> 7) & 1

    @property
    def sout_r(self):
        return self.pout & 1

    def step(self, rst, mode, sin_r, sin_l, pin):
        if rst:
            nxt = 0
        elif mode == 0:        # hold
            nxt = self.pout
        elif mode == 1:        # right: sin_r enters MSB
            nxt = ((sin_r << 7) | (self.pout >> 1)) & 0xFF
        elif mode == 2:        # left: sin_l enters LSB
            nxt = ((self.pout << 1) | sin_l) & 0xFF
        else:                  # load
            nxt = pin
        self.pout = nxt
        return self.pout


def check_bit(name, got, exp):
    check(name, got, exp)


def shift_suite():
    print("=" * 74)
    print("SHIFT-REGISTER TWIN : replaying tb_universal_shift_register_8bit stimulus")
    print("=" * 74)
    s = ShiftReg()
    H, R, L, P = 0, 1, 2, 3

    # T01 reset
    check("T01a rst", s.step(1, H, 0, 0, 0), 0x00)
    check("T01b rst held", s.step(1, H, 0, 0, 0), 0x00)
    # T02 load A5
    check("T02a load 0xA5", s.step(0, P, 0, 0, 0xA5), 0xA5)
    check_bit("T02b sout_l", s.sout_l, 1)
    check_bit("T02c sout_r", s.sout_r, 1)
    # T03 hold x3 with toggling serial inputs (and pin=FF on 3rd)
    check("T03a hold", s.step(0, H, 1, 1, 0xA5), 0xA5)
    check("T03b hold", s.step(0, H, 0, 1, 0xA5), 0xA5)
    check("T03c hold", s.step(0, H, 1, 1, 0xFF), 0xA5)
    # T04 shift right, sin_r pattern 1,0,1,1
    check_bit("T04a sout_r(before)=1", s.sout_r, 1)
    check("T04b -> D2", s.step(0, R, 1, 0, 0), 0xD2)
    check("T04c -> 69", s.step(0, R, 0, 0, 0), 0x69)
    check("T04d -> B4", s.step(0, R, 1, 0, 0), 0xB4)
    check("T04e -> DA", s.step(0, R, 1, 0, 0), 0xDA)
    # T05 shift left, sin_l pattern 0,1,0,1
    check_bit("T05a sout_l(before)=1", s.sout_l, 1)
    check("T05b -> B4", s.step(0, L, 0, 0, 0), 0xB4)
    check("T05c -> 69", s.step(0, L, 0, 1, 0), 0x69)
    check("T05d -> D2", s.step(0, L, 0, 0, 0), 0xD2)
    check("T05e -> A5", s.step(0, L, 0, 1, 0), 0xA5)
    # T06 reset dominates mode
    check("T06a load 3C", s.step(0, P, 0, 0, 0x3C), 0x3C)
    check("T06b rst>mode", s.step(1, R, 1, 0, 0), 0x00)
    # T07 walking one
    check("T07a load 01", s.step(0, P, 0, 0, 0x01), 0x01)
    for i, exp in enumerate([0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x00]):
        check(f"T07{chr(98+i)} walk", s.step(0, L, 0, 0, 0), exp)
    # T08 ones fill
    for i, exp in enumerate([0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F, 0x7F, 0xFF]):
        check(f"T08{chr(97+i)} fill", s.step(0, L, 0, 1, 0), exp)
    check_bit("T08i sout_l", s.sout_l, 1)
    check_bit("T08j sout_r", s.sout_r, 1)
    # T09 serial out on shift right
    check_bit("T09a sout_r=1", s.sout_r, 1)
    for i, exp in enumerate([0x7F, 0x3F, 0x1F]):
        check(f"T09{chr(98+i)} ->", s.step(0, R, 0, 0, 0), exp)
    check_bit("T09e sout_r=1", s.sout_r, 1)
    for i, exp in enumerate([0x0F, 0x07, 0x03, 0x01, 0x00]):
        check(f"T09{chr(102+i)} ->", s.step(0, R, 0, 0, 0), exp)
    check_bit("T09k sout_l=0", s.sout_l, 0)
    check_bit("T09l sout_r=0", s.sout_r, 0)


def main():
    counter_suite()
    shift_suite()
    print("=" * 74)
    print(f"TWIN SUMMARY : {passes + fails} checks, {fails} failure(s)")
    print(">>> OVERALL :", "PASS" if fails == 0 else "FAIL", "<<<")
    print("=" * 74)
    raise SystemExit(0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
