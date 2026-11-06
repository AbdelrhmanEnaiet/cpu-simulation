# CPU Core (Phase 1) — Spec v0.1

**Summary**
- **Goal:** a custom 16-bit CPU in Python, with an assembler and a terminal runner, tested well enough to build a game on later.
- **Lane:** about 100k–300k instructions/s in plain Python `[estimate]`. A snake-style game needs about 50k–150k/s `[estimate]`.
- **Biggest risk:** Python speed is too low for the game. This is checked early, in M2.

## 1. Goal

The user (learning, building by hand) gets a working CPU simulator, an assembler and a terminal runner. With them they can write `.asm` programs that compute values and draw on a 64×32 screen, and verify them with tests. The simulator is designed so a server and React frontend (phase 2) can plug in without changes.

## 2. Context & constraints

- `[known]` The user writes all code by hand. Claude helps with design, explanations and reviews only.
- `[known]` Python 3.11.9. Tests use pytest. No other runtime dependencies.
- `[known]` Phase 2 (FastAPI + WebSocket + React) and phase 3 (the game) are separate specs. See "Planned later" below.
- `[known]` Reference pages: [CPU basics](https://claude.ai/artifact/2DrAiX8Stqac2gevigsau2) and [instruction set](https://claude.ai/artifact/JqUGFqFodVRYR8dEW1nvxc).
- `[assumed]` Runs on the user's Windows machine. No speed target for other machines.

## 3. Scope

**In:**
- CPU core: registers, flags, a 4-phase `step()`, all 28 instructions
- 64K-word memory with a memory map: RAM, I/O, screen
- Devices: keys, frame counter, random number, screen
- Assembler, with labels, constants and `.word` data
- Disassembler, which turns one instruction back into text
- Terminal runner
- Example programs
- Tests

**Out (explicitly):**
- Server and frontend
- Interrupts
- Multiply and divide
- Sound
- Live keyboard input in the runner
- `.org` and macros in the assembler
- Stack overflow detection
- Cycle timing (every instruction takes 1 step)

## 4. Interface

### 4.1 Machine

| Item | Definition |
|---|---|
| Word | 16-bit unsigned integer, 0–65535. Every result is masked with `& 0xFFFF`. |
| Registers | `R0`–`R3` (general), `PC`, `SP`. All 16-bit. |
| Flags | `Z` = result is 0. `N` = bit 15 of the result is 1. `C` = defined per instruction (§4.3). |
| Memory | 65,536 words. Every address is valid. All words are 0 at reset. |
| Reset | All registers 0, `PC` = 0, `SP` = `0xC000` (empty stack), flags off, memory cleared, program loaded starting at address 0. |
| Status | `running` / `halted` / `error`. When the status is `halted` or `error`, `step()` does nothing. |

### 4.2 Memory map

| Range | Use | Read | Write |
|---|---|---|---|
| `0x0000–0xBFFF` | RAM: program, data, stack | value | stores |
| `0xC000` | Keys. Bit 0 = up, 1 = down, 2 = left, 3 = right, 4 = action. | key bits | ignored |
| `0xC001` | Frame counter. The host calls `tick_frame()`, which adds 1 and wraps at 65535. | count | ignored |
| `0xC002` | Random number: a new value 0–65535 on every read. Writing a value reseeds the generator with it, so the same seed always gives the same sequence. | random | reseeds |
| `0xC003–0xC0FF` | Reserved | 0 | ignored |
| `0xC100–0xCFFF` | Unused RAM | value | stores |
| `0xD000–0xD07F` | Screen: 64×32, 1 bit per pixel | value | stores (draws pixels) |
| `0xD080–0xFFFF` | Unused RAM | value | stores |

**Pixel `(x, y)`**, where x is 0–63 and y is 0–31:
- **Word** = `0xD000 + y*4 + x//16`
- **Bit** = `15 - x%16`, so the most significant bit is the leftmost pixel.

### 4.3 Instructions

**Encoding:** word 1 = `opcode[15:8] | Ra[7:4] | Rb[3:0]`. 2-word instructions add a second word holding `n` or `addr`. Fields an instruction doesn't use are 0 when assembled and ignored by the CPU. A register field above 3 is an **error** ("bad register").

| Op | Instruction | Words | Effect | Flags |
|---|---|---|---|---|
| 00 | `NOP` | 1 | nothing | – |
| 01 | `LDI Ra, n` | 2 | Ra = n | – |
| 02 | `MOV Ra, Rb` | 1 | Ra = Rb | – |
| 03 | `LD Ra, [addr]` | 2 | Ra = mem[addr] | – |
| 04 | `ST Ra, [addr]` | 2 | mem[addr] = Ra | – |
| 05 | `LD Ra, [Rb]` | 1 | Ra = mem[Rb] | – |
| 06 | `ST Ra, [Rb]` | 1 | mem[Rb] = Ra | – |
| 10 | `ADD Ra, Rb` | 1 | Ra = Ra + Rb | Z N; C = sum > 0xFFFF |
| 11 | `SUB Ra, Rb` | 1 | Ra = Ra − Rb | Z N; C = Ra < Rb (borrow) |
| 12 | `ADDI Ra, n` | 2 | Ra = Ra + n | as ADD |
| 13 | `INC Ra` | 1 | Ra = Ra + 1 | Z N; C = wrapped 0xFFFF→0 |
| 14 | `DEC Ra` | 1 | Ra = Ra − 1 | Z N; C = wrapped 0→0xFFFF |
| 15 | `CMP Ra, Rb` | 1 | flags of Ra − Rb; Ra unchanged | as SUB |
| 20 | `AND Ra, Rb` | 1 | Ra = Ra & Rb | Z N; C = 0 |
| 21 | `OR Ra, Rb` | 1 | Ra = Ra \| Rb | Z N; C = 0 |
| 22 | `XOR Ra, Rb` | 1 | Ra = Ra ^ Rb | Z N; C = 0 |
| 23 | `SHL Ra` | 1 | Ra = Ra << 1 | Z N; C = old bit 15 |
| 24 | `SHR Ra` | 1 | Ra = Ra >> 1 (0 shifts in) | Z N; C = old bit 0 |
| 30 | `JMP addr` | 2 | PC = addr | – |
| 31 | `JZ addr` | 2 | jump if Z | – |
| 32 | `JNZ addr` | 2 | jump if not Z | – |
| 33 | `JC addr` | 2 | jump if C | – |
| 34 | `JNC addr` | 2 | jump if not C | – |
| 40 | `CALL addr` | 2 | push(address after this instruction); PC = addr | – |
| 41 | `RET` | 1 | PC = pop() | – |
| 42 | `PUSH Ra` | 1 | push(Ra) | – |
| 43 | `POP Ra` | 1 | Ra = pop() | – |
| FF | `HLT` | 1 | status = halted | – |

- **push(v):** `SP -= 1; mem[SP] = v`.
- **pop():** if `SP == 0xC000`, error ("stack empty"). Otherwise `v = mem[SP]; SP += 1`.
- **Any other opcode** is an error ("unknown opcode XX at PC").
- **PC past `0xFFFF`** wraps to 0 `[assumed]`.

### 4.4 Python API (shape, not code)

- `CPU.reset()` and `CPU.load(words)`
- `CPU.step() -> StepRecord`, which runs one instruction through four phases: fetch → decode → execute → write-back. A `StepRecord` holds:
  - `pc`: the address of the instruction
  - `text`: the disassembled instruction
  - `phases`: one short note per phase, groundwork for the micro-step view
  - `changed_registers`
  - `written_addresses`
  - `status`
- `CPU.run(max_steps) -> int`, which runs until halted, error, or `max_steps`, and returns the number of steps run.
- `CPU.snapshot() -> dict`, containing `R0`–`R3`, `PC`, `SP`, `Z`, `C`, `N`, `status`, `error`.
- `Bus.read(addr)` / `Bus.write(addr, value)`: the memory and device routing. The CPU only talks to the bus.
- `Bus.screen_pixels() -> list of 128 words (0xD000–0xD07F)`, `Bus.set_keys(bits)`, `Bus.tick_frame()`. The bus does not decode pixels.
- `Display.pixels(words) -> 32 rows × 64 bools`. It decodes the screen words with the pixel formula in §4.2, like a video chip.
- `assemble(text) -> (words, line_map)`. It raises `AsmError(line, message)` at the first error.
- `disassemble(words, addr) -> (text, length)`.

### 4.5 Assembly syntax

- One instruction per line.
- `;` starts a comment.
- **Labels:** `name:`, on its own line or before an instruction.
- **Constants:** `.equ NAME value`.
- **Data:** `.word v1, v2, ...` puts raw words at the current address.
- **Numbers:** decimal `42`, hex `0x2A`, binary `0b101010`. A number that doesn't fit in 16 bits is an error.
- Registers and instruction names are case-insensitive.
- `[addr]` and `[Rb]` choose between the two forms of `LD` and `ST`.
- A label or constant can be used anywhere a number or address goes.
- **Errors:** unknown instruction, wrong operand count or type, unknown label, duplicate label, number out of range. Each reports the line number.

### 4.6 Runner

`python -m backend.runner <file.asm> [--step] [--max-steps N]`. `N` defaults to 1,000,000.

- **Run mode:** run until halted, error, or the limit. Call `tick_frame()` every 1,000 instructions `[assumed]`. At the end, print the state and the screen.
- **Step mode:** Enter runs one step, `r` runs to the end, `q` quits.
- **Each print shows:**
  - the registers and flags
  - `PC` and the current instruction
  - the status, plus the error if there is one
  - the screen as 32 lines of 64 characters, `#` for on and `.` for off

## 5. Acceptance criteria

| # | Criterion | Test | Target | Tag |
|---|---|---|---|---|
| A1 | Every instruction does exactly what §4.3 says | pytest: at least 1 test per opcode, plus edge cases for each flag (wrap, borrow, shifted-out bit, zero) | all 28 pass | [known] |
| A2 | Errors stop the CPU cleanly | tests: unknown opcode, bad register, `POP`/`RET` on empty stack → status `error` with a message; `step()` afterwards changes nothing | pass | [known] |
| A3 | Memory map is correct | tests: I/O writes ignored; random changes between reads (seeded); frame counter wraps; `screen_pixels()` returns the 128 screen words | pass | [known] |
| A4 | Assembler output is correct | tests: each instruction form → expected words; labels before and after use; `.equ`; `.word`; hex, binary, decimal | pass | [known] |
| A5 | Assembler errors are helpful | tests: each error type → `AsmError` with the right line number | pass | [known] |
| A6 | Disassembly round-trips | for each instruction form: `disassemble(assemble(x))` gives the same instruction | pass | [known] |
| A7 | Example programs work | `add.asm` (R0 = 8), `sum.asm` (1..10 → 55), `call.asm` (CALL/RET with PUSH/POP keeps registers), `pixel.asm` (pixel (37,5) on), `fill.asm` (all 2,048 pixels on) | each halts with the expected state | [known] |
| A8 | Fast enough for a game | benchmark: a 1M-instruction loop | ≥ 100k instructions/s on the user's PC | [estimate] |
| A9 | Phases are recorded | test: a `StepRecord` has 4 phase entries, plus the correct changed registers and written addresses | pass | [known] |
| A10 | Display decodes the screen | tests: `0x8000` in word 0 → only pixel (0,0) on; pixel (37,5) → word `0xD016`, bit 10; all words `0xFFFF` → all 2,048 pixels on | pass | [known] |

## 6. Baseline

The simplest version is one `step()` function with a big `if/elif` on the opcode, and no phases or step records. It would pass A1–A8. The design adds **phases and step records** (A9). That costs maybe 10–20% speed and a little code `[estimate]`, but it buys the phase 2 micro-step view and the "send only what changed" messages without rewriting the CPU.

## 7. Design

```
backend/
  cpu/        CPU: registers, flags, step() phases, instruction table, disassembler
  memory/     Bus: 64K words + routing to devices
  devices/    Keys, FrameCounter, Random, Screen
  assembler/  two passes: 1) find label addresses, 2) emit words
  runner.py   terminal runner
programs/     example .asm files
tests/        pytest
```

- **The CPU only talks to the bus.** Devices can be added later without touching the CPU.
- **Instructions are looked up in a table, opcode → handler,** not a long `if` chain. Each opcode lives in one place, and the disassembler can use the same table.
- **The assembler has 2 passes,** so a label can be used before it's defined, as jumps forward usually need.
- **Rejected:** an 8-bit design with a pointer register (more complex, see the README history), cycle-accurate timing (not needed for the goal), and interrupts (they can be added later in `step()`).

## 8. Estimates

| Item | Estimate | Dominant factor |
|---|---|---|
| Python speed | 100k–300k instr/s (3–10 µs per step) | Python function calls per step |
| Game need | ~2–5k instructions per redraw × 10–30 redraws/s ≈ 20k–150k/s | how much of the screen redraws each move |
| Code size | CPU ~400–600 lines, assembler ~250–400, runner ~100, tests ~500–800 | number of instructions × edge cases |
| Effort (by hand, while learning) | 20–40 hours | the assembler parser and the flag edge cases |

## 9. Risks & open questions

| Item | Tag | Impact if wrong | Cheapest check | Owner |
|---|---|---|---|---|
| Python is too slow for the game | [estimate] | the game stutters in phase 3 | benchmark a NOP/JMP loop as soon as M2 is done | user |
| SUB/CMP carry convention is confusing (C = borrow) | [assumed] | game code uses `JC`/`JNC` backwards | tests in A1, plus a note on the reference page | user |
| PC wraps instead of raising an error | [assumed] | runaway programs fail silently | runner `--max-steps` catches loops; change to an error if it bites | user |
| No stack overflow check | [assumed] | deep recursion overwrites the program | add the check if it ever happens | user |
| Frame tick every 1,000 instructions in the runner | [assumed] | timing in the terminal differs from the server later | revisit in the phase 2 spec | — |

## 10. Milestones

- **M1: Bus and devices.** Memory map tests pass (A3) and the Display decodes the screen (A10). This builds the base everything uses.
- **M2: CPU skeleton.** `step()` with 4 phases, `NOP`, `HLT`, `LDI`, `MOV`, `LD`/`ST` (both forms), `JMP`, plus error handling (A2, A9). **Run the speed benchmark here (A8).** This settles the biggest risk early.
- **M3: Math and bits.** All flag tests pass (A1 for 1x and 2x).
- **M4: Jumps, calls and stack.** The rest of A1.
- **M5: Assembler and disassembler** (A4–A6).
- **M6: Runner and example programs** (A7). `pixel.asm` and `fill.asm` show on the terminal screen.

## 11. Evaluation plan

- `pytest` runs every test, and all of them must pass before moving to the next milestone.
- The A8 benchmark runs again after M6 to catch slowdowns.
- **Phase 1 is done when A1–A9 all pass,** and `fill.asm` draws a full screen in the runner.

## Planned later (not in this spec)

- **Phase 2:** FastAPI WebSocket server, sending a state update 60 times a second and only what changed; React panels for controls, registers, code, memory, screen and keys.
- **Phase 3:** the game (snake-style), plus interrupts if they turn out to be needed.

## Change log

- v0.1 2026-11-05: initial
