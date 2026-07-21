#!/usr/bin/env python3
"""Two-stage static verification for the Week-3 lab Verilog.

Stage 1 - pyverilog full grammar parse (a real Verilog parser):
    * RTL files parse as-is.
    * For testbenches, call lines of the TB helper tasks are neutralised
      first (pyverilog's grammar intentionally omits task-enable-with-args;
      the calls are standard Verilog-2001 accepted by Vivado/XSim).
Stage 2 - structural lint of the untouched original text:
    * balanced module/endmodule, task/endtask, begin/end, case/endcase,
      function/endfunction, generate/endgenerate
    * balanced (), [], {} outside comments and string literals
    * balanced string quotes per line
"""
import re
import sys
from pyverilog.vparser.parser import VerilogParser

RTL_FILES = [
    "rtl/up_down_counter_16bit.v",
    "rtl/universal_shift_register_8bit.v",
    "rtl/clock_enable_gen.v",
    "rtl/counter_top_boolean.v",
    "rtl/shiftreg_top_boolean.v",
]
TB_FILES = [
    "tb/tb_up_down_counter_16bit.v",
    "tb/tb_universal_shift_register_8bit.v",
]

TB_TASK_CALL = re.compile(r"^\s*(step_and_check|check_count|check_flag|"
                          r"check_reg|check_bit)\s*\(.*\);\s*$")
DIRECTIVE = re.compile(r"^\s*`(timescale|default_nettype|define|include)")


def strip_comments_strings(text, keep_strings=False):
    """Remove // and /* */ comments. Strings are either kept verbatim or
    replaced by spaces (for balance checks)."""
    out = []
    i, n = 0, len(text)
    in_line = in_block = in_str = False
    buf = []
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_line:
            if ch == "\n":
                in_line = False
                buf.append(ch)
            else:
                buf.append(" ")
        elif in_block:
            if ch == "*" and nxt == "/":
                in_block = False
                buf.append("  ")
                i += 1
            else:
                buf.append("\n" if ch == "\n" else " ")
        elif in_str:
            if ch == "\\":
                buf.append("  " if not keep_strings else (ch + nxt))
                i += 1
            elif ch == '"':
                in_str = False
                buf.append('"' if keep_strings else " ")
            else:
                buf.append(ch if keep_strings else " ")
        else:
            if ch == "/" and nxt == "/":
                in_line = True
                buf.append("  ")
                i += 1
            elif ch == "/" and nxt == "*":
                in_block = True
                buf.append("  ")
                i += 1
            elif ch == '"':
                in_str = True
                buf.append('"' if keep_strings else " ")
            else:
                buf.append(ch)
        i += 1
    return "".join(buf)


def lint(fname, text):
    """Structural balance checks on the original source. Returns errors list."""
    errs = []
    code = strip_comments_strings(text)          # strings blanked
    code_str = strip_comments_strings(text, keep_strings=True)

    word_pairs = [("module", "endmodule"), ("task", "endtask"),
                  ("begin", "end"), ("case", "endcase"),
                  ("function", "endfunction"), ("generate", "endgenerate")]
    tokens = re.findall(r"[A-Za-z_]+", code)
    for a, b in word_pairs:
        ca, cb = tokens.count(a), tokens.count(b)
        # 'case' count includes casex/casez? findall gives exact words only.
        if ca != cb:
            errs.append(f"{fname}: unbalanced {a}/{b}: {ca} vs {cb}")

    for op, cl, nm in [("(", ")", "parentheses"), ("[", "]", "brackets"),
                       ("{", "}", "braces")]:
        if code.count(op) != code.count(cl):
            errs.append(f"{fname}: unbalanced {nm}: "
                        f"{code.count(op)} vs {code.count(cl)}")

    # quotes balanced on every line (after comment stripping)
    for ln, line in enumerate(code_str.splitlines(), 1):
        if line.count('"') % 2 != 0:
            errs.append(f"{fname}:{ln}: odd number of double quotes")

    return errs


def parseable_text(fname, text):
    out = []
    for line in text.splitlines():
        if DIRECTIVE.match(line):
            continue                       # simulator directives not needed
        if fname.startswith("tb/") and TB_TASK_CALL.match(line):
            continue                       # helper task call lines (see header)
        out.append(line)
    return "\n".join(out)


def main():
    parser = VerilogParser(debug=False)
    ok = True
    for f in RTL_FILES + TB_FILES:
        orig = open(f).read()
        # ---- stage 2: lint the untouched file
        errs = lint(f, orig)
        for e in errs:
            print("LINT FAILED   :", e)
        if errs:
            ok = False
            continue
        # ---- stage 1: pyverilog parse
        try:
            ast = parser.parse(parseable_text(f, orig))
            n = len(ast.description.definitions)
            print(f"PARSE+LINT OK : {f} ({n} module definition(s))")
        except Exception as e:                   # noqa: BLE001
            ok = False
            print(f"PARSE FAILED  : {f}\n    {e}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
