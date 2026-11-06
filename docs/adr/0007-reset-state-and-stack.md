# 0007. Reset state; stack grows down from 0xC000; empty pop is an error

- **Status:** Accepted (not built yet, M2/M4)
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.1, §4.3](../specs/cpu-core.md#41-machine)

## Context
`CALL`, `RET`, `PUSH` and `POP` need a stack. Where it starts, which way it grows and what counts as an error must be fixed before the tests are written.

## Decision
- **Reset:**
  - `R0`–`R3` = 0, `PC` = 0, `SP` = `0xC000` (empty stack)
  - flags off, memory cleared, status `running`
- Programs load at address 0.
- **push(v):** `SP -= 1`, then `mem[SP] = v`. The first push writes `0xBFFF`, the top of RAM.
- **pop():** if `SP == 0xC000`, the status becomes `error` ("stack empty"). Otherwise `v = mem[SP]`, then `SP += 1`.
- `PC` past `0xFFFF` wraps to 0 `[assumed]`.
- Once the status is `halted` or `error`, `step()` does nothing.

## Consequences
- The program and data grow up from 0, and the stack grows down from the top of RAM. They meet only when a program is very large or recurses very deep.
- There is no overflow check `[assumed]`. Deep recursion silently overwrites the program. Add a check if that ever happens.
- `RET` on an empty stack stops the CPU cleanly instead of jumping to garbage.
