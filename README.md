# CPU Simulation

A simulated CPU with a visual frontend and a simulation backend.
End goal: run a game on it.

This project is built by hand, without AI-written code. It's a learning project.

## Goals

- Simulate a custom 16-bit CPU (backend, Python)
- Visualize its state as it runs (frontend, React)
- Run a simple grid game (snake, breakout style) on the simulated CPU

## Layout

```
cpu-simulation/
├── backend/      (Python)
│   ├── cpu/        CPU core: registers, flags, instruction execution
│   ├── memory/     64 KB memory + memory map
│   ├── devices/    display, keyboard input, timer (memory-mapped)
│   ├── assembler/  assembly text -> machine code
│   └── server/     FastAPI + WebSocket: run/pause/step, streams state
├── frontend/     (React)
│   └── panels: registers, memory view, assembly view, game screen, controls
└── programs/     .asm programs: tests, demos, the game
```

- The CPU core is independent of the server and UI.
- Devices are memory-mapped: the CPU only reads and writes addresses.
- `step()` runs explicit phases (fetch, decode, execute, write-back), ready for a future micro-step view.
- The server streams only what changed each frame.

## CPU (decided so far)

- 16-bit registers, 16-bit word-addressed memory (65,536 words)
- Registers: `R0`–`R3` (general), `PC` (program counter), `SP` (stack pointer)
- Flags: `Z` (zero), `C` (carry), `N` (negative)
- Any register can hold an address: `LD R0, [R1]`
- Instructions are 1 or 2 words: opcode + registers, then an optional constant/address
- Stack starts at `SP = 0xC000` and grows down
- Memory map:

| Range | Use | Read | Write |
|---|---|---|---|
| `0x0000–0xBFFF` | RAM: program, data, stack | value | stores |
| `0xC000` | Keys: bit 0 up, 1 down, 2 left, 3 right, 4 action | key bits | ignored |
| `0xC001` | Frame counter (wraps at 65535) | count | ignored |
| `0xC002` | Random: new value each read | random | reseeds |
| `0xC003–0xC0FF` | Reserved | 0 | ignored |
| `0xC100–0xCFFF` | Unused RAM | value | stores |
| `0xD000–0xD07F` | Screen: 64×32 mono, 16 pixels per word | value | stores |
| `0xD080–0xFFFF` | Unused RAM | value | stores |

Pixel `(x, y)` is in word `0xD000 + y*4 + x//16`, bit `15 - x%16` (the most significant bit is the leftmost pixel).

## Install

Requirements: Python 3.11 or newer, on Windows. The commands below are for Command Prompt (cmd).

1. Open Command Prompt in the project folder:
   ```cmd
   cd C:\projects\cpu-simulation
   ```
2. Make a virtual environment:
   ```cmd
   python -m venv .venv
   ```
3. Start it:
   ```cmd
   .venv\Scripts\activate.bat
   ```
   The prompt now starts with `(.venv)`.
4. Install the libraries:
   ```cmd
   pip install -r requirements.txt
   ```
5. Check that it works:
   ```cmd
   python -m pytest --version
   ```
   It should print `pytest 9.2.0`.

To leave the virtual environment, run `deactivate`.

Start the virtual environment (step 3) each time you open a new terminal.

**Libraries in phase 1** ([requirements.txt](requirements.txt)):

| Library | Version | Why |
|---|---|---|
| pytest | 9.2.0 | runs the tests |
| colorama, iniconfig, packaging, pluggy, Pygments | pinned | pytest's own dependencies |

The simulator itself uses only the Python standard library.

## Run the tests

With the virtual environment active:

```cmd
python -m pytest
```

All tests must pass before moving to the next milestone.

## Docs

| Doc | What it holds |
|---|---|
| [docs/specs/cpu-core.md](docs/specs/cpu-core.md) | The phase 1 contract: machine, memory map, instructions, API, acceptance criteria |
| [docs/architecture.md](docs/architecture.md) | How the parts fit together, data flow, status, risks |
| [docs/adr/](docs/adr/0000-index.md) | Architecture decision records: why each choice was made |
| [docs/implementation-guide.md](docs/implementation-guide.md) | Step-by-step build order with the tests to write |

## Roadmap

| Milestone | What | Status |
|---|---|---|
| M1 | Bus and devices: memory map, keys, frame counter, random, screen words, Display | ✅ done (tag `M1-complete`) |
| M2 | CPU skeleton: 4-phase `step()`, moves, loads/stores, `JMP`, errors, **speed benchmark** | next |
| M3 | Math and bit instructions, flags | planned |
| M4 | Jumps, calls and stack | planned |
| M5 | Assembler and disassembler | planned |
| M6 | Terminal runner and example programs | planned |
| Phase 2 | FastAPI WebSocket server + React frontend | later |
| Phase 3 | The game (snake/breakout style) | later |

## Status

**M1 complete.** The Bus, devices and Display are built and 22 tests pass.

Next: M2, starting with guide step 3.1 (CPU state).
Known gap: `Bus.tick_frame()` is in the spec but not built yet. It's needed by M6.
