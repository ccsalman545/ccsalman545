#!/usr/bin/env python3
"""Assemble the final Week-3 lab report from the parts, injecting the actual
Verilog/XDC source files verbatim (fenced) wherever a {{FILE:path}} token
appears. Guarantees the report's listings always match the repository code."""
import re
import sys

ROOT = "/home/user/ccsalman545/fpga-lab/week-03-counters-shift-registers"
PARTS = ["part1.md", "part2.md", "part3.md", "part4.md", "part5.md"]
OUT = f"{ROOT}/report/Week3_Counters_and_Shift_Registers_Lab_Report.md"

TOKEN = re.compile(r"\{\{FILE:(.+?)\}\}")

def fence_for(path):
    return "tcl" if path.endswith(".xdc") else "verilog"

def main():
    doc = []
    injected = []
    for part in PARTS:
        text = open(f"{ROOT}/report/parts/{part}").read()
        def repl(m):
            rel = m.group(1).strip()
            code = open(f"{ROOT}/{rel}").read().rstrip("\n")
            injected.append(rel)
            return f"```{fence_for(rel)}\n{code}\n```"
        doc.append(TOKEN.sub(repl, text))
    out = "\n".join(doc).rstrip() + "\n"
    open(OUT, "w").write(out)
    words = len(out.split())
    print(f"Assembled {OUT}")
    print(f"Injected files ({len(injected)}):")
    for f in injected:
        print("   ", f)
    print(f"Approx. word count: {words}  (chars: {len(out)})")
    # sanity: no token left behind
    assert "{{FILE:" not in out, "unresolved token!"
    print("OK: no unresolved tokens")

if __name__ == "__main__":
    sys.exit(main())
