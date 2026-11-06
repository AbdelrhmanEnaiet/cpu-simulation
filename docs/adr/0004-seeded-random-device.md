# 0004. Seeded random device, reseeded by a write

- **Status:** Accepted
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.2](../specs/cpu-core.md#42-memory-map)

## Context
Games need randomness, for example the food position or the ball angle. Tests need the same numbers on every run.

## Decision
- Each read of `0xC002` returns a new value 0–65535 (`randrange(0x10000)`).
- Writing a value to `0xC002` reseeds the generator with that value.
- `Bus(seed=...)` sets the first seed. With no seed, one is picked at random.
- The device keeps its own `random.Random` object and never uses the global `random` module.

## Consequences
- The same seed gives the same sequence, both in tests and in programs (`LDI R0, 42` then `ST R0, [0xC002]`).
- A read changes the device's state. A debugger or memory view that reads `0xC002` changes the sequence. The phase 2 memory view must skip that address or show it without reading it.
