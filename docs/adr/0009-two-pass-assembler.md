# 0009. Two-pass assembler

- **Status:** Accepted (not built yet, M5)
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.4, §4.5](../specs/cpu-core.md#45-assembly-syntax), A4–A6

## Context
Programs jump forward. For example, `JZ done` comes before the line `done:`. A single pass doesn't know that address yet.

## Decision
- Pass 1 walks the lines, counts each instruction's length (1 or 2 words), and records the value of each label and `.equ`.
- Pass 2 writes the words, using those values.
- `assemble(text)` returns `(words, line_map)`. `line_map` links each address to its source line, for the runner and the debugger.
- The first error raises `AsmError(line, message)`.
- `disassemble(words, addr)` returns `(text, length)`. It uses the CPU's instruction table; see [0006](0006-instruction-encoding-and-dispatch-table.md).

## Consequences
- A label works both before and after its definition.
- Pass 1 must know each instruction's length from its name and operands alone. That holds for this instruction set.
- Stopping at the first error keeps the code simple. Errors get fixed one at a time.
- Round-trip tests (`disassemble(assemble(x)) == x`) keep the assembler and the CPU in step.
