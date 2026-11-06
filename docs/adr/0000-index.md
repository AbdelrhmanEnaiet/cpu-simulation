# Architecture Decision Records

Each ADR records one decision: why it was made and what it costs.
The contract itself lives in [../specs/cpu-core.md](../specs/cpu-core.md). The ADRs explain the *why* behind it.
For how the parts fit together, see [../architecture.md](../architecture.md).

**Rules**
- Never edit an ADR to change its decision. Write a new ADR that supersedes it, and set the old one's status to `Superseded by NNNN`.
- When a decision changes, update the spec first, then the ADR, then the code.
- Status values: `Proposed`, `Accepted`, `Superseded`, `Rejected`.

| # | Decision | Status | Built |
|---|---|---|---|
| [0001](0001-16-bit-word-memory.md) | 16-bit words, 64K word-addressed memory, mask every result | Accepted | M1 ✅ |
| [0002](0002-cpu-talks-only-to-bus.md) | The CPU only talks to the Bus; the Bus is a dumb router | Accepted | M1 ✅ (Bus side) |
| [0003](0003-memory-mapped-io-layout.md) | Memory-mapped I/O layout and a reserved range | Accepted | M1 ✅ |
| [0004](0004-seeded-random-device.md) | Seeded random device, reseeded by a write | Accepted | M1 ✅ |
| [0005](0005-screen-bit-order-and-display.md) | MSB = leftmost pixel; Display decodes, the Bus doesn't | Accepted | M1 ✅ |
| [0006](0006-instruction-encoding-and-dispatch-table.md) | Instruction encoding and an opcode → handler table | Accepted | M2 planned |
| [0007](0007-reset-state-and-stack.md) | Reset state; stack grows down from `0xC000`; empty pop is an error | Accepted | M2/M4 planned |
| [0008](0008-step-phases-and-step-record.md) | `step()` runs 4 explicit phases and returns a `StepRecord` | Accepted | M2 planned |
| [0009](0009-two-pass-assembler.md) | Two-pass assembler | Accepted | M5 planned |
| [0010](0010-rejected-alternatives.md) | Rejected: 8-bit design, cycle timing, interrupts | Accepted | – |
| [0011](0011-tdd-and-hand-written-code.md) | TDD with pytest; all code written by hand | Accepted | ongoing |
