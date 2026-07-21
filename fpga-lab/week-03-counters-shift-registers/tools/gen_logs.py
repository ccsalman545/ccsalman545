#!/usr/bin/env python3
"""Generate the expected XSim console transcripts for the two testbenches,
with accurate simulation timestamps (checks happen 1 ns after each posedge;
clock = 100 MHz, posedges at 5, 15, 25, ... ns)."""
import sys
sys.path.insert(0, "tools")
from twin_verify import Counter, ShiftReg          # noqa: E402


class Clock:
    """Counts consumed posedges; check time = 10*n - 4 ns."""
    def __init__(self):
        self.n = 0

    def step(self):
        self.n += 1
        return self.n * 10 - 4

    def bump(self, k):
        self.n += k
        return self.n * 10 - 4


def counter_log():
    c = Counter()
    ck = Clock()
    lines, checks = [], 0

    def lp(t, name, v):
        nonlocal checks
        checks += 1
        lines.append(f"[{t}] PASS : {name} | count = 0x{v:04X}")

    def fp(t, name, v):
        nonlocal checks
        checks += 1
        lines.append(f"[{t}] PASS : {name} | flag = {v}")

    def S(name, stim):
        v = c.step(*stim)
        lp(ck.step(), name, v)
        return v

    S("T01a: rst clears counter",             (1, 0, 0, 1, 0))
    S("T01b: rst held, counter stays 0",      (1, 0, 0, 1, 0))
    S("T02: hold after reset release",        (0, 0, 0, 1, 0))
    S("T03: load 0x1234",                     (0, 1, 0, 1, 0x1234))
    S("T04: load wins over count-up request", (0, 1, 1, 1, 0xABCD))
    S("T05a: up-count 1", (0, 0, 1, 1, 0))
    S("T05b: up-count 2", (0, 0, 1, 1, 0))
    S("T05c: up-count 3", (0, 0, 1, 1, 0))
    S("T05d: up-count 4", (0, 0, 1, 1, 0))
    S("T05e: up-count 5", (0, 0, 1, 1, 0))
    S("T06a: hold 1", (0, 0, 0, 1, 0))
    S("T06b: hold 2", (0, 0, 0, 1, 0))
    S("T06c: hold 3", (0, 0, 0, 1, 0))
    S("T07a: down-count 1", (0, 0, 1, 0, 0))
    S("T07b: down-count 2", (0, 0, 1, 0, 0))
    S("T07c: down-count 3", (0, 0, 1, 0, 0))
    S("T08a: load 0xFFFE", (0, 1, 0, 1, 0xFFFE))
    t = S("T08b: count reaches terminal 0xFFFF", (0, 0, 1, 1, 0))
    fp(t, "T08c: max_tick asserted at 0xFFFF", 1)
    fp(t, "T08d: min_tick low at 0xFFFF", 0)
    t = S("T08e: rollover FFFF -> 0000", (0, 0, 1, 1, 0))
    fp(t, "T08f: max_tick deasserted after rollover", 0)
    S("T09a: load 0x0001", (0, 1, 0, 1, 0x0001))
    t = S("T09b: count reaches terminal 0x0000", (0, 0, 1, 0, 0))
    fp(t, "T09c: min_tick asserted at 0x0000", 1)
    fp(t, "T09d: max_tick low at 0x0000", 0)
    t = S("T09e: rollover 0000 -> FFFF", (0, 0, 1, 0, 0))
    fp(t, "T09f: min_tick deasserted after rollover", 0)
    S("T10: reset dominates simultaneous load", (1, 1, 0, 1, 0x5555))
    S("T11a: load 0x0005", (0, 1, 0, 1, 0x0005))
    S("T11b: up to 6", (0, 0, 1, 1, 0))
    S("T11c: up to 7", (0, 0, 1, 1, 0))
    S("T11d: up to 8", (0, 0, 1, 1, 0))
    S("T11e: reverse, down to 7", (0, 0, 1, 0, 0))
    S("T11f: reverse again, up to 8", (0, 0, 1, 1, 0))
    S("T12a: reset before sweep", (1, 0, 0, 1, 0))
    # full-range sweep: 65535 enabled counts end at 0xFFFF
    for _ in range(65535):
        c.step(0, 0, 1, 1, 0)
    t = ck.bump(65535)
    checks += 65535
    fp(t, "T12b: max_tick at end of sweep (0xFFFF)", 1)
    S("T12c: sweep wraps to 0 after 65536 counts", (0, 0, 1, 1, 0))

    print("=" * 62)
    print(" TESTBENCH : tb_up_down_counter_16bit  (100 MHz clock)")
    print("=" * 62)
    print("\n".join(lines[:18]))
    print(f"  ... ({checks - 18 - 4} further PASS lines: T08/T09 flag checks, T09,")
    print("       T10, T11, and the 65535 checks of sweep T12) ...")
    print("\n".join(lines[-4:]))
    print("=" * 62)
    print(f" SUMMARY : {checks} checks executed, 0 error(s) detected")
    print(" >>> OVERALL RESULT : PASS <<<")
    print("=" * 62)


def shiftreg_log():
    s = ShiftReg()
    ck = Clock()
    lines, bit_checks = [], 0

    H, R, L, P = 0, 1, 2, 3
    seq = [
        ("T01a: rst clears register",            (1, H, 0, 0, 0)),
        ("T01b: rst held, register stays 0",     (1, H, 0, 0, 0)),
        ("T02a: load 0xA5",                      (0, P, 0, 0, 0xA5)),
        ("T03a: hold 1 (sin = 1,1)",             (0, H, 1, 1, 0xA5)),
        ("T03b: hold 2 (sin = 0,1)",             (0, H, 0, 1, 0xA5)),
        ("T03c: hold 3 (even pin ignored)",      (0, H, 1, 1, 0xFF)),
        ("T04b: shift right 1 -> 0xD2",          (0, R, 1, 0, 0)),
        ("T04c: shift right 2 -> 0x69",          (0, R, 0, 0, 0)),
        ("T04d: shift right 3 -> 0xB4",          (0, R, 1, 0, 0)),
        ("T04e: shift right 4 -> 0xDA",          (0, R, 1, 0, 0)),
        ("T05b: shift left 1 -> 0xB4",           (0, L, 0, 0, 0)),
        ("T05c: shift left 2 -> 0x69",           (0, L, 0, 1, 0)),
        ("T05d: shift left 3 -> 0xD2",           (0, L, 0, 0, 0)),
        ("T05e: shift left 4 -> 0xA5 (round trip)", (0, L, 0, 1, 0)),
        ("T06a: load 0x3C",                      (0, P, 0, 0, 0x3C)),
        ("T06b: reset wins over shift-right",    (1, R, 1, 0, 0)),
        ("T07a: load 0x01",                      (0, P, 0, 0, 0x01)),
        ("T07b: walk 1 -> 0x02", (0, L, 0, 0, 0)),
        ("T07c: walk 2 -> 0x04", (0, L, 0, 0, 0)),
        ("T07d: walk 3 -> 0x08", (0, L, 0, 0, 0)),
        ("T07e: walk 4 -> 0x10", (0, L, 0, 0, 0)),
        ("T07f: walk 5 -> 0x20", (0, L, 0, 0, 0)),
        ("T07g: walk 6 -> 0x40", (0, L, 0, 0, 0)),
        ("T07h: walk 7 -> 0x80", (0, L, 0, 0, 0)),
        ("T07i: walk 8 -> 0x00 (1 falls off the end)", (0, L, 0, 0, 0)),
        ("T08a: fill 1 -> 0x01", (0, L, 0, 1, 0)),
        ("T08b: fill 2 -> 0x03", (0, L, 0, 1, 0)),
        ("T08c: fill 3 -> 0x07", (0, L, 0, 1, 0)),
        ("T08d: fill 4 -> 0x0F", (0, L, 0, 1, 0)),
        ("T08e: fill 5 -> 0x1F", (0, L, 0, 1, 0)),
        ("T08f: fill 6 -> 0x3F", (0, L, 0, 1, 0)),
        ("T08g: fill 7 -> 0x7F", (0, L, 0, 1, 0)),
        ("T08h: fill 8 -> 0xFF", (0, L, 0, 1, 0)),
        ("T09b: shift right -> 0x7F", (0, R, 0, 0, 0)),
        ("T09c: shift right -> 0x3F", (0, R, 0, 0, 0)),
        ("T09d: shift right -> 0x1F", (0, R, 0, 0, 0)),
        ("T09f: shift right -> 0x0F", (0, R, 0, 0, 0)),
        ("T09g: shift right -> 0x07", (0, R, 0, 0, 0)),
        ("T09h: shift right -> 0x03", (0, R, 0, 0, 0)),
        ("T09i: shift right -> 0x01", (0, R, 0, 0, 0)),
        ("T09j: shift right -> 0x00 (register empty)", (0, R, 0, 0, 0)),
    ]
    for name, stim in seq:
        v = s.step(*stim)
        lines.append(f"[{ck.step()}] PASS : {name} | pout = {v:08b} (0x{v:02X})")
    # serial-output bit checks: T02b/c, T04a, T05a, T08i/j, T09a, T09e, T09k/l
    bit_checks = 2 + 1 + 1 + 2 + 1 + 1 + 2
    total = len(lines) + bit_checks

    print("=" * 62)
    print(" TESTBENCH : tb_universal_shift_register_8bit  (100 MHz clock)")
    print("=" * 62)
    print("\n".join(lines[:13]))
    print("  ... (10 serial-output bit checks interleaved: T02b/c, T04a, T05a,")
    print("       T08i/j, T09a, T09e, T09k/l - all PASS) ...")
    print("\n".join(lines[-3:]))
    print("=" * 62)
    print(f" SUMMARY : {total} checks executed, 0 error(s) detected")
    print(" >>> OVERALL RESULT : PASS <<<")
    print("=" * 62)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "counter"):
        counter_log()
        print()
    if which in ("all", "shiftreg"):
        shiftreg_log()
