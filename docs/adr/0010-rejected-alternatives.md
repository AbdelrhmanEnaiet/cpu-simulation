# 0010. Rejected: 8-bit design, cycle timing, interrupts

- **Status:** Accepted
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §7](../specs/cpu-core.md#7-design)

## Context
Several common CPU-simulator features were considered and left out to keep phase 1 small.

## Decision
| Option | Why rejected | Could come back? |
|---|---|---|
| 8-bit CPU with a pointer register | 16-bit addresses need register pairs or a special pointer register: more instructions and harder code | no |
| Cycle-accurate timing | not needed to run a game; costs speed and code | only for a teaching view |
| Interrupts | the game can poll the keys and the frame counter | yes: add a check in `step()` in phase 3 if needed |

## Consequences
- One instruction is one step. Speed is measured in instructions per second, not cycles.
- Programs poll `0xC000` and `0xC001` in their main loop.
- Adding interrupts later changes `step()` and the reset state. Write a new ADR when that happens.
