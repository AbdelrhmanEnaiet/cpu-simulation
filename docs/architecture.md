# System Architecture

How the parts of the CPU simulation fit together, what is built, and where it grows next.

- **Contract (what each part must do):** [specs/cpu-core.md](specs/cpu-core.md)
- **Why each choice was made:** [adr/](adr/0000-index.md)
- **Build order:** [implementation-guide.md](implementation-guide.md)

Last updated: 2026-11-06 (M1 complete).

## 1. Summary

- **Goal:** a hand-built 16-bit CPU in Python that runs a small grid game, with a React view of its state.
- **Lane:** Python must reach at least 100k instructions/s (A8). The estimate is 100k–300k. The game needs about 20k–150k.
- **Biggest open risk:** that speed. It gets measured at M2, before most of the CPU is written.

## 2. Layers

```
 ┌──────────────────────────────────────────────────────────────┐
 │ Host                                                         │
 │   phase 1: runner (terminal)     phase 2: server (FastAPI)   │
 │   load program · step/run · set_keys · tick_frame · draw     │
 └───────┬───────────────────────────────┬──────────────────────┘
         │ step() / run() / snapshot()   │ set_keys / tick_frame /
         ▼                               │ screen_pixels
 ┌──────────────────┐                    │
 │ CPU              │                    │
 │ R0–R3 PC SP ZCN  │                    │
 │ fetch → decode → │                    │
 │ execute → write  │                    │
 │ opcode table     │                    │
 └───────┬──────────┘                    │
         │ read(addr) / write(addr, v)   │
         ▼                               ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Bus (router, no logic)                                       │
 └──┬──────────────┬──────────────┬──────────────┬──────────────┘
    ▼              ▼              ▼              ▼
  RAM          Keys 0xC000   FrameCounter    Random 0xC002
  64K words                   0xC001
  (incl. screen words 0xD000–0xD07F)
                                   │ screen_pixels(): 128 words
                                   ▼
                           ┌──────────────┐
                           │ Display      │  32×64 bools
                           └──────┬───────┘
                                  ▼
                 terminal (# and .)  /  React screen panel
```

**Rules between layers**
- The CPU only knows the Bus ([ADR 0002](adr/0002-cpu-talks-only-to-bus.md)).
- The Bus routes addresses. It doesn't decode pixels or run game logic ([ADR 0005](adr/0005-screen-bit-order-and-display.md)).
- Only the host sets keys and ticks the frame. Programs only read them.
- The CPU core doesn't import anything from the runner, server or UI.

## 3. Components

| Component | Path | Job | Status |
|---|---|---|---|
| Bus | `backend/memory/bus.py` | 64K words, mask, route `0xC000–0xC002` to devices, block reserved range, `screen_pixels()`, `set_keys()` | ✅ M1 (`tick_frame()` missing) |
| Devices | `backend/devices/device.py` | `Keys` (mask `0x1F`), `FrameCounter` (wraps), `Random` (seeded, reseed on write) | ✅ M1 |
| Display | `backend/devices/display.py` | 128 words → 32×64 bools, MSB leftmost | ✅ M1 |
| CPU | `backend/cpu/` | registers, flags, 4-phase `step()`, opcode table, `StepRecord`, `run()`, `snapshot()` | M2–M4 |
| Assembler | `backend/assembler/` | two-pass `assemble()`, `AsmError`, `disassemble()` | M5 |
| Runner | `backend/runner.py` | CLI: run and step modes, prints state and screen | M6 |
| Programs | `programs/` | `add`, `sum`, `call`, `pixel`, `fill` `.asm` | M6 |
| Server | `backend/server/` | FastAPI + WebSocket, 60 updates/s, sends changes only | phase 2 |
| Frontend | `frontend/` | React panels: controls, registers, code, memory, screen, keys | phase 2 |

## 4. Memory map

See [ADR 0003](adr/0003-memory-mapped-io-layout.md) and spec §4.2.

| Range | Use | Read | Write |
|---|---|---|---|
| `0x0000–0xBFFF` | RAM: program (from 0, grows up), data, stack (from `0xBFFF`, grows down) | value | stores |
| `0xC000` | Keys: bit 0 up, 1 down, 2 left, 3 right, 4 action | key bits | ignored |
| `0xC001` | Frame counter | count | ignored |
| `0xC002` | Random | new value each read | reseeds |
| `0xC003–0xC0FF` | Reserved | 0 | ignored |
| `0xC100–0xCFFF` | Unused RAM | value | stores |
| `0xD000–0xD07F` | Screen: 64×32, 16 pixels per word | value | stores |
| `0xD080–0xFFFF` | Unused RAM | value | stores |

Pixel `(x, y)` → word `0xD000 + y*4 + x//16`, bit `15 - x%16`.

## 5. Data flow

**One step (M2 onward)**
1. Fetch: read the word at `PC` through the Bus. Read a second word if the opcode needs one.
2. Decode: split it into opcode, `Ra` and `Rb`, and look up the handler. A bad register or unknown opcode sets status `error`.
3. Execute: the handler computes the result and the flags, with every value masked to 16 bits.
4. Write-back: write the registers or memory (through the Bus) and set `PC`.
5. Return a `StepRecord` ([ADR 0008](adr/0008-step-phases-and-step-record.md)).

**One frame (runner now, server later)**
1. The host calls `set_keys(bits)` with the current input.
2. It runs N instructions (the runner ticks every 1,000 instructions `[assumed]`).
3. It calls `tick_frame()`.
4. It reads `screen_pixels()` and sends the words through `Display` (or to the client).
5. Phase 2 only: it sends the changed registers and addresses collected from the `StepRecord`s.

**Program load**
`.asm` text → `assemble()` → `(words, line_map)` → `CPU.load(words)` writes them from address 0. `line_map` lets the runner show the source line for each `PC`.

## 6. Quality targets

| # | Target | Check | Status |
|---|---|---|---|
| A3 | memory map behaves as specified | `tests/test_bus.py`, `tests/test_devices.py` | ✅ |
| A10 | Display decodes the screen | `tests/test_display.py` | ✅ |
| A1, A2, A9 | instructions, errors, phases | CPU tests | M2–M4 |
| A4–A6 | assembler, errors, round-trip | assembler tests | M5 |
| A7 | example programs | runner tests | M6 |
| A8 | at least 100k instr/s | 1M-instruction loop benchmark | M2, again at M6 |

22 tests pass at M1 (`python -m pytest`).

## 7. Risks and known gaps

| Item | Impact | What to do |
|---|---|---|
| Python too slow (A8) | the game stutters | benchmark at M2; fast path in `run()` without records (guide 3.8) |
| `Bus.tick_frame()` not built | runner can't tick frames | add it, test first, before M6 |
| Bus raises `IndexError` for addresses outside 0–`0xFFFF`; spec says every address is valid | none if the CPU masks addresses | keep the CPU masking; leave the guard |
| C means borrow on `SUB`/`CMP` | game code uses `JC`/`JNC` backwards | flag tests in A1, note it in program comments |
| No stack overflow check | deep recursion overwrites the program | add a check if it happens |
| PC wraps silently | runaway programs | `--max-steps` in the runner |
| Reading `0xC002` changes state | a memory view changes the random sequence | phase 2 view skips that address |

## 8. Where it grows next

- **Phase 2, server:** wraps the CPU and Bus without changing them. It uses `step()` and `run()`, the `StepRecord` diffs, `set_keys`, `tick_frame` and `screen_pixels`. The frame rate and tick timing get their own spec, which replaces the runner's 1,000-instruction tick.
- **Phase 2, frontend:** it can show phases using the `phases` notes in `StepRecord`, and memory and code using `line_map` and `disassemble`.
- **Phase 3, the game:** written in `.asm`. It polls keys and the frame counter. If polling isn't enough, interrupts are added in `step()` under a new ADR ([ADR 0010](adr/0010-rejected-alternatives.md)).
- **New devices:** they go in `0xC003–0xC0FF` and the Bus routing. The CPU doesn't change.

## Change log

- 2026-11-06: first version, written after M1 was complete.
