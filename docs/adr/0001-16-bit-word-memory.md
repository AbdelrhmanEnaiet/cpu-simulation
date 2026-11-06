# 0001. 16-bit words, 64K word-addressed memory, mask every result

- **Status:** Accepted
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.1](../specs/cpu-core.md#41-machine)

## Context
The CPU must be simple enough to build by hand. It must also hold game state (positions, scores, screen words) without multi-word arithmetic. Python integers have no fixed width, so overflow never happens unless the code forces it.

## Decision
- A word is a 16-bit unsigned integer, 0–65535.
- Memory is 65,536 words. Addresses point at words, not bytes.
- Every value stored or produced is masked with `& 0xFFFF`.
- All words are 0 at reset.

## Consequences
- One word holds any address, so any register can be a pointer (`LD R0, [R1]`).
- There is no byte access. Text or byte data takes a full word per item.
- Every path that makes a value (Bus write, each ALU result) must apply the mask once, or overflow bugs slip in.
- The Bus tests check overflow: `65536 → 0`, `0x30005 → 5`.

## Note on the code (M1)
`Bus.read` and `Bus.write` raise `IndexError` for an address below 0 or above `0xFFFF`. The spec says every address is valid. The two agree as long as the CPU masks addresses before it calls the Bus. The error only catches Python-side bugs.
