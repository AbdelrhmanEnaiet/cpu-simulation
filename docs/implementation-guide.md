# Implementation Guide: Phase 1 (CPU Core)

This guide is written in ASD-STE100 Simplified Technical English.

This guide tells you the order of the work. It tells you where to start, what to make, and where to go next.

The rules for each part are in the spec: [specs/cpu-core.md](specs/cpu-core.md). This guide gives the spec section for each step. Read that section before you start the step.

Reference pages:

- [CPU basics](https://claude.ai/artifact/2DrAiX8Stqac2gevigsau2)
- [Instruction set](https://claude.ai/artifact/JqUGFqFodVRYR8dEW1nvxc)

## The map

```
Step 1  Setup
   |
Step 2  Bus and devices            (M1)
   |
Step 3  CPU skeleton               (M2)
   |
   +-- 3.7 Speed test --- too slow? --> 3.8 Make it faster --+
   |                                                         |
   |<--------------------------------------------------------+
   |
Step 4  Math and bit instructions  (M3)
   |
Step 5  Jumps, calls and stack     (M4)
   |
Step 6  Assembler and disassembler (M5)
   |
Step 7  Runner and example programs (M6)
   |
Step 8  Phase 1 complete
```

## Rules for all steps

1. Do the steps in the given order.
2. For each step, write the tests first. Then write the code.
3. Run all tests with this command, from the project folder: `python -m pytest`.
4. Do not go to the next step until all tests pass.
5. If a test fails and you cannot find the cause, stop. Ask Claude for a hint. Do not ask for the code.
6. At the end of each step, ask Claude to review your code.
7. If a rule in the spec is not correct, stop. Change the spec first. Add a line to the spec change log. Then change the code.
8. Write one commit at the end of each sub-step. Use a short message that tells what you added.

---

## Step 1: Setup

**Spec:** section 7 (folder layout).

1. Make these folders: `backend/`, `backend/cpu/`, `backend/memory/`, `backend/devices/`, `backend/assembler/`, `programs/`, `tests/`.
2. Put an empty file `__init__.py` in each folder in `backend/`, and in `backend/` itself.
3. Do the steps in the "Install" section of `README.md`.
4. Write one test in `tests/test_setup.py` that always passes.
5. Run `python -m pytest`. Make sure that 1 test passes.

**Result:** pytest finds your tests and your folders are ready.

**Next:** go to Step 2.

---

## Step 2: Bus and devices (M1)

**Spec:** sections 4.1, 4.2 and 4.4 (the `Bus` part).

**Goal:** the CPU will use the bus to read and write memory. The bus also sends some addresses to the devices.

### 2.1 Memory words

1. Write tests for these rules:
   - All 65,536 words are 0 at the start.
   - A value that you write to a RAM address comes back when you read it.
   - A value above 65535 is masked to 16 bits.
2. Make the `Bus` class in `backend/memory/`. Use a list of 65,536 numbers.
3. Run the tests.

**Next:** go to 2.2.

### 2.2 Keys (`0xC000`)

1. Write tests for these rules:
   - `set_keys(bits)` changes the value at `0xC000`.
   - A write to `0xC000` from the CPU side has no effect.
2. Make the keys device in `backend/devices/`.
3. Connect the device to the bus. The bus must send `0xC000` to the device.
4. Run the tests.

**Next:** go to 2.3.

### 2.3 Frame counter (`0xC001`)

1. Write tests for these rules:
   - `tick_frame()` adds 1 to the value at `0xC001`.
   - After 65535, the next tick gives 0.
   - A write to `0xC001` has no effect.
2. Make the frame counter device and connect it to the bus.
3. Run the tests.

**Next:** go to 2.4.

### 2.4 Random number (`0xC002`)

1. Write tests for these rules:
   - Each read gives a value from 0 to 65535.
   - With the same seed, the bus gives the same numbers in the same order.
2. Make the random device. Use Python's `random.Random` with a seed.
3. Connect the device to the bus.
4. Run the tests.

**Next:** go to 2.5.

### 2.5 Reserved addresses

1. Write a test: a read from `0xC003` to `0xC0FF` gives 0. A write has no effect.
2. Change the bus to obey this rule.
3. Run the tests.

**Next:** go to 2.6.

### 2.6 Screen

1. Write tests for these rules:
   - `screen_pixels()` gives 32 rows of 64 values.
   - A write of `0x8000` to `0xD000` turns on pixel (0, 0) only.
   - Pixel (37, 5) is word `0xD016`, bit 10.
   - A write of `0xFFFF` to all words from `0xD000` to `0xD07F` turns on all 2,048 pixels.
2. Make `screen_pixels()`. Read the screen words from memory. Use the pixel formula in spec section 4.2.
3. Run the tests.

**Result:** acceptance criterion A3 passes.

**Next:** ask Claude to review Step 2. Then go to Step 3.

---

## Step 3: CPU skeleton (M2)

**Spec:** sections 4.1, 4.3 (encoding and errors) and 4.4 (the `CPU` part).

**Goal:** the CPU can do the four phases for a small set of instructions. This step also measures the speed.

### 3.1 CPU state

1. Write tests for these rules:
   - After `reset()`: R0 to R3 are 0, PC is 0, SP is `0xC000`, flags are off, status is `running`.
   - `load(words)` puts the words in memory from address 0.
   - `snapshot()` gives all registers, flags, status and error.
2. Make the `CPU` class in `backend/cpu/`. The CPU gets a `Bus` when you make it.
3. Run the tests.

**Next:** go to 3.2.

### 3.2 Fetch

1. Write a test: the fetch phase reads the word at PC from the bus.
2. Make the fetch phase as a separate method.
3. Run the tests.

**Next:** go to 3.3.

### 3.3 Decode and the instruction table

1. Make an instruction table. For each opcode, keep the name, the number of words and the handler.
2. Write tests for these rules:
   - The decode phase splits the word into opcode, Ra and Rb.
   - For a 2-word instruction, the decode phase also reads the second word.
   - An unknown opcode sets status to `error`. The error message gives the opcode and the PC.
   - A register field above 3 sets status to `error`.
3. Make the decode phase as a separate method.
4. Run the tests.

**Next:** go to 3.4.

### 3.4 Execute and write-back: first instructions

Do this step for these instructions: `NOP`, `HLT`, `LDI`, `MOV`, `LD [addr]`, `ST [addr]`, `LD [Rb]`, `ST [Rb]`, `JMP`.

1. Write tests for each instruction. Write the instruction words by hand in the test. For example, `LDI R0, 5` is `0x0100, 0x0005`.
2. Write a test for the PC rule. After an instruction, PC points to the next instruction. A jump sets PC to the jump address.
3. Write a test: after `HLT`, `step()` does not change the state.
4. Make the execute phase and the write-back phase as separate methods.
5. Write one handler for each instruction. Put each handler in the instruction table.
6. Run the tests.

**Next:** go to 3.5.

### 3.5 Step record

1. Write tests for these rules:
   - `step()` gives a `StepRecord`.
   - The record has 4 phase notes.
   - The record has the correct changed registers and written addresses.
   - The record has the instruction text, for example `LDI R0, 5`.
2. Make the `StepRecord` class.
3. Change `step()` to make a record during the four phases.
4. Run the tests.

**Note:** the instruction text is a small disassembler. Use the instruction table for it. In Step 6, you will move this into the real disassembler.

**Next:** go to 3.6.

### 3.6 Run

1. Write tests for these rules:
   - `run(max_steps)` stops at `HLT`.
   - `run(max_steps)` stops at an error.
   - `run(max_steps)` stops after `max_steps` steps.
   - `run(max_steps)` gives the number of steps it did.
2. Make `run()`.
3. Run the tests.

**Result:** acceptance criteria A2 and A9 pass.

**Next:** go to 3.7.

### 3.7 Speed test

1. Write the file `tests/benchmark.py`. Do not start the file name with `test_`. Pytest must not run it.
2. In the file, make a program from these words: a `NOP`, then a `JMP 0`. This program loops forever.
3. Run the program for 1,000,000 steps. Measure the time with `time.perf_counter()`.
4. Show the result as instructions per second.
5. Run the file: `python tests/benchmark.py`.
6. Write the result in the spec, in the A8 row.

**Decision:**

- If the result is 100,000 instructions per second or more, go to Step 4.
- If the result is less than 100,000, go to 3.8.

### 3.8 Make it faster (only if 3.7 is too slow)

1. Run the speed test with the profiler: `python -m cProfile -s cumtime tests/benchmark.py`.
2. Find the functions that use the most time.
3. Ask Claude to explain the profiler output with you.
4. Make one change at a time. After each change, run all tests. Then run the speed test again.
5. Do not remove the four phases. Do not remove the step record.

**Decision:**

- If the result is now 100,000 or more, go to Step 4.
- If the result is still too slow after three changes, write the result in the spec risk table. Then go to Step 4. The game can draw fewer pixels for each frame.

---

## Step 4: Math and bit instructions (M3)

**Spec:** section 4.3, opcodes `10` to `24`, and the Flags column.

**Goal:** all math and bit instructions work. The flags are correct in all edge cases.

### 4.1 Z and N flags

1. Make one helper that sets Z and N from a result. All math and bit instructions will use it.
2. Write tests for the helper: result 0 sets Z. A result with bit 15 on sets N.
3. Run the tests.

**Next:** go to 4.2.

### 4.2 Add: `ADD`, `ADDI`, `INC`

1. Write tests for each instruction:
   - A normal result, for example 5 + 3 = 8.
   - A wrap: `0xFFFF + 1` gives 0, with Z on and C on.
   - A result with bit 15 on sets N.
2. Make the three handlers.
3. Run the tests.

**Next:** go to 4.3.

### 4.3 Subtract: `SUB`, `DEC`, `CMP`

**Caution:** C is the borrow flag. C is on when Ra is less than Rb. Many people think the opposite. Read the spec row again before you write the tests.

1. Write tests for each instruction:
   - A normal result, for example 8 − 3 = 5, with C off.
   - Equal values give 0, with Z on and C off.
   - A borrow: 3 − 8 wraps, with C on and N on.
   - `CMP` sets the flags but does not change Ra.
2. Make the three handlers.
3. Run the tests.

**Next:** go to 4.4.

### 4.4 Logic: `AND`, `OR`, `XOR`

1. Write tests for each instruction:
   - A normal result.
   - C is always off after the instruction.
   - `XOR R0, R0` gives 0 with Z on.
2. Make the three handlers.
3. Run the tests.

**Next:** go to 4.5.

### 4.5 Shifts: `SHL`, `SHR`

1. Write tests for each instruction:
   - `SHL` of 3 gives 6. `SHR` of 7 gives 3.
   - `SHL` of `0x8000` gives 0, with C on and Z on.
   - `SHR` of 1 gives 0, with C on and Z on.
2. Make the two handlers.
3. Run the tests.

**Result:** acceptance criterion A1 passes for opcodes `10` to `24`.

**Next:** ask Claude to review Step 4. Then go to Step 5.

---

## Step 5: Jumps, calls and stack (M4)

**Spec:** section 4.3, opcodes `31` to `43`, and the push and pop rules.

**Goal:** the program can make decisions, call functions and keep values on the stack.

### 5.1 Conditional jumps

1. Write two tests for each of `JZ`, `JNZ`, `JC` and `JNC`:
   - One test with the flag set so that the jump occurs.
   - One test with the flag set so that the jump does not occur. PC must then point to the next instruction.
2. Make the four handlers.
3. Run the tests.

**Next:** go to 5.2.

### 5.2 Push and pop helpers

1. Write tests for these rules:
   - Push decreases SP by 1, then writes the value at SP. The first push writes to `0xBFFF`.
   - Pop reads the value at SP, then increases SP by 1.
   - Pop when SP is `0xC000` sets status to `error` with the message "stack empty".
2. Make two helper methods: one push and one pop.
3. Run the tests.

**Next:** go to 5.3.

### 5.3 `PUSH` and `POP`

1. Write tests:
   - `PUSH R0` then `POP R1` copies R0 to R1.
   - Two pushes and two pops give the values back in reverse order.
2. Make the two handlers. Use the helpers from 5.2.
3. Run the tests.

**Next:** go to 5.4.

### 5.4 `CALL` and `RET`

1. Write tests:
   - `CALL` pushes the address of the instruction after the `CALL`. This is PC + 2.
   - `CALL` sets PC to the call address.
   - `RET` sets PC to the pushed address.
   - `RET` with an empty stack sets status to `error`.
   - A function that calls a second function returns to the correct places.
2. Make the two handlers.
3. Run the tests.

**Result:** acceptance criterion A1 passes for all 28 instructions.

**Next:** ask Claude to review Step 5. Then go to Step 6.

---

## Step 6: Assembler and disassembler (M5)

**Spec:** sections 4.3 (encoding), 4.4 (`assemble`, `disassemble`) and 4.5.

**Goal:** you can write programs as text. You do not have to write words by hand again.

**Note:** use the CPU instruction table from Step 3.3. The table gives the opcode and the number of words. Do not copy this data into a second table.

### 6.1 Clean the lines

1. Write tests for these rules:
   - The assembler removes comments that start with `;`.
   - The assembler ignores empty lines.
   - The assembler keeps the original line number for each line.
2. Make the line cleaner in `backend/assembler/`.
3. Run the tests.

**Next:** go to 6.2.

### 6.2 Numbers

1. Write tests for these rules:
   - `42`, `0x2A` and `0b101010` all give 42.
   - 65536 or more is an error.
   - A bad number is an error.
2. Make the number parser.
3. Run the tests.

**Next:** go to 6.3.

### 6.3 Operands

1. Write tests. The parser must find each type of operand:
   - a register: `R2`, `r2`
   - a register address: `[R1]`
   - a fixed address: `[0xC000]` or `[KEYS]`
   - a number or a name: `5` or `loop`
2. Make the operand parser.
3. Run the tests.

**Next:** go to 6.4.

### 6.4 Pass 1: labels and constants

1. Write tests for these rules:
   - A label gets the address of the next instruction.
   - Pass 1 counts the words of each instruction. It uses the instruction table.
   - `.equ NAME value` makes a constant.
   - `.word` counts one word for each value.
   - A duplicate label is an error with the line number.
2. Make pass 1. Pass 1 gives a table of names and values.
3. Run the tests.

**Next:** go to 6.5.

### 6.5 Pass 2: make the words

1. Write one test for each instruction form in spec section 4.3. Each test compares the words with the expected words.
2. Write a test: a label that you use before its line gives the correct address.
3. Write tests: `.word 1, 2, 3` gives three words.
4. Make pass 2.
5. Make `assemble(text)`. It gives the words and the line map.
6. Run the tests.

**Result:** acceptance criterion A4 passes.

**Next:** go to 6.6.

### 6.6 Assembler errors

1. Write one test for each error type in spec section 4.5. Each test makes sure that `AsmError` has the correct line number.
2. Make sure that each error has a clear message. For example: "line 12: unknown label 'lop'".
3. Run the tests.

**Result:** acceptance criterion A5 passes.

**Next:** go to 6.7.

### 6.7 Disassembler

1. Write a round-trip test for each instruction form. Assemble one line. Disassemble the words. The result must be the same instruction.
2. Make `disassemble(words, addr)`. Move the instruction text code from Step 3.5 into it.
3. Change `StepRecord` to use the new disassembler.
4. Run all tests.

**Result:** acceptance criterion A6 passes.

**Next:** ask Claude to review Step 6. Then go to Step 7.

---

## Step 7: Runner and example programs (M6)

**Spec:** sections 4.6 and 5 (A7, A8).

**Goal:** you can run `.asm` files and see the result in the terminal.

### 7.1 Example programs

Write these files in `programs/`:

| File | What it does | Expected result |
|---|---|---|
| `add.asm` | Adds 5 and 3 | R0 = 8, status `halted` |
| `sum.asm` | Adds 1 to 10 in a loop | R0 = 55, status `halted` |
| `call.asm` | Calls a function that uses `PUSH` and `POP` | Registers keep their values after the call |
| `pixel.asm` | Turns on pixel (37, 5) | Only that pixel is on |
| `fill.asm` | Turns on all pixels with a loop | All 2,048 pixels are on |

1. Write one test for each program in `tests/test_programs.py`. The test assembles the file, runs it, and examines the snapshot or the screen.
2. Write the programs. Start with `add.asm`. Write the next program only when the previous test passes.
3. Run the tests.

**Note:** if a program does not work, the cause can be in the program or in the CPU. Look at the step records first. Then ask Claude for a hint.

**Result:** acceptance criterion A7 passes.

**Next:** go to 7.2.

### 7.2 Runner: run mode

1. Make `backend/runner.py`. Use `argparse` for the arguments in spec section 4.6.
2. Make the runner call `tick_frame()` each 1,000 instructions.
3. Make the runner print the registers, the flags, PC, the current instruction and the status.
4. Make the runner print the screen: 32 lines of 64 characters, `#` for on and `.` for off.
5. Run `python -m backend.runner programs/fill.asm`. Make sure that the screen is full of `#`.
6. Run `python -m backend.runner programs/pixel.asm`. Make sure that one `#` is in row 5, column 37.

**Next:** go to 7.3.

### 7.3 Runner: step mode

1. Add the `--step` option.
2. In step mode, Enter does one step, `r` runs to the end, and `q` stops the runner.
3. After each step, print the state.
4. Run `python -m backend.runner programs/sum.asm --step`. Step through the loop. Make sure that R0 increases.

**Next:** go to 7.4.

### 7.4 Speed test again

1. Run `python tests/benchmark.py`.
2. Compare the result with the result from 3.7.
3. If the result is now less than 100,000, go to 3.8. Then come back to 7.4.
4. Write the new result in the spec.

**Result:** acceptance criterion A8 passes.

**Next:** go to Step 8.

---

## Step 8: Phase 1 complete

1. Run `python -m pytest`. Make sure that all tests pass.
2. Make sure that acceptance criteria A1 to A9 in the spec all pass.
3. Change the "Status" section in `README.md`.
4. Ask Claude to review all of phase 1.
5. Ask Claude to start the phase 2 spec: the server and the React frontend.
