# 0003. Memory-mapped I/O layout and a reserved range

- **Status:** Accepted
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.2](../specs/cpu-core.md#42-memory-map)

## Context
Devices need addresses. The program, data and stack need one large block of RAM. Future devices need room without anything having to move.

## Decision

| Range | Use | Read | Write |
|---|---|---|---|
| `0x0000–0xBFFF` | RAM: program, data, stack | value | stores |
| `0xC000` | Keys (bit 0 up, 1 down, 2 left, 3 right, 4 action) | key bits | ignored |
| `0xC001` | Frame counter, wraps at 65535 | count | ignored |
| `0xC002` | Random, see [0004](0004-seeded-random-device.md) | new value | reseeds |
| `0xC003–0xC0FF` | Reserved for future devices | 0 | ignored |
| `0xC100–0xCFFF` | Unused RAM | value | stores |
| `0xD000–0xD07F` | Screen, 128 words, see [0005](0005-screen-bit-order-and-display.md) | value | stores |
| `0xD080–0xFFFF` | Unused RAM | value | stores |

- The host sets the keys with `set_keys(bits)`, masked to `0x1F`. Writes from the CPU are ignored.
- The stack starts just below the I/O block; see [0007](0007-reset-state-and-stack.md).

## Consequences
- Programs read input with a plain `LD` and draw with a plain `ST`. There are no special I/O instructions.
- The reserved range reads 0 now. A device added there later won't change programs that never touch it.
- A stack that grows too deep runs down into program data. Nothing checks for this; see [0007](0007-reset-state-and-stack.md).
