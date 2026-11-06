# 0006. Instruction encoding and an opcode → handler table

- **Status:** Accepted (not built yet, M2)
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.3, §7](../specs/cpu-core.md#43-instructions)

## Context
There are 28 instructions, 4 registers, and constants up to 16 bits. The encoding must be easy to decode by hand, and the CPU must be fast enough in Python.

## Decision
- Word 1 = `opcode[15:8] | Ra[7:4] | Rb[3:0]`.
- 2-word instructions put `n` or `addr` in word 2.
- The assembler sets unused fields to 0, and the CPU ignores them.
- A register field above 3 is an error ("bad register"). An unknown opcode is an error.
- Opcodes are grouped by family:
  - `0x` moves
  - `1x` arithmetic
  - `2x` logic and shifts
  - `3x` jumps
  - `4x` calls and stack
  - `FF` = `HLT`
- The CPU finds each opcode in a table (opcode → handler) instead of an `if/elif` chain. The disassembler uses the same table for names and lengths.

## Consequences
- Each instruction lives in one place. Adding an instruction means adding one table entry.
- The opcode is easy to read in a hex dump: `0x1012` is `ADD R1, R2`.
- The 4-bit register fields leave room for 16 registers later. Only 4 are allowed now.
- A table lookup plus a function call on every step costs speed. The A8 benchmark at M2 checks it.
