# 0002. The CPU only talks to the Bus; the Bus is a dumb router

- **Status:** Accepted
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.4, §7](../specs/cpu-core.md#7-design)

## Context
The CPU needs RAM plus devices: keys, frame counter, random and screen. If the CPU knew about each device, every new device would mean changing the CPU.

## Decision
- The CPU calls only `Bus.read(addr)` and `Bus.write(addr, value)`.
- The Bus sends each address to RAM or to a device. It holds no game or CPU logic.
- The host (the runner now, the server later) uses three more Bus methods: `set_keys(bits)`, `tick_frame()` and `screen_pixels()`.

## Consequences
- New devices go in the Bus and in `backend/devices/`. The CPU doesn't change.
- The CPU can be tested with a plain Bus.
- Every memory access is one Python method call. That is part of the speed cost; see [0008](0008-step-phases-and-step-record.md) and the A8 benchmark.

## Known gap (M1)
The spec lists `Bus.tick_frame()`, but the code doesn't have it yet. `FrameCounter.tick_frame()` exists. Add the Bus method before the runner needs it (M6).
