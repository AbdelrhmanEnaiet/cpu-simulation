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
- Memory map:

| Range | Use |
|---|---|
| `0x0000–0xBFFF` | RAM: program, data, stack |
| `0xC000–0xC0FF` | I/O: keyboard, timer, random |
| `0xD000–0xD07F` | Screen: 64×32 mono, 16 pixels per word |

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

## Current Focus

Phase 1: the CPU core, the assembler and a terminal runner.

- Spec: [docs/specs/cpu-core.md](docs/specs/cpu-core.md)
- Step-by-step guide: [docs/implementation-guide.md](docs/implementation-guide.md)

Phase 2 (server + React frontend) and phase 3 (the game) come later.

## Status

Design done for phase 1. No code yet.
