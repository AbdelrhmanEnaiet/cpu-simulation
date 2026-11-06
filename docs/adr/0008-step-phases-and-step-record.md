# 0008. step() runs 4 explicit phases and returns a StepRecord

- **Status:** Accepted (not built yet, M2)
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.4, §6](../specs/cpu-core.md#44-python-api-shape-not-code), A8, A9

## Context
Phase 2 wants a micro-step view of the CPU and a server that sends only what changed. The simplest CPU is one `step()` with a big `if` that records nothing.

## Decision
- `step()` runs fetch → decode → execute → write-back as separate parts.
- It returns a `StepRecord` with:
  - `pc`
  - `text`
  - `phases`: one note per phase
  - `changed_registers`
  - `written_addresses`
  - `status`
- `run(max_steps)` loops `step()` and returns the number of steps run.
- `snapshot()` returns the registers, flags, status and error.

## Consequences
- The server can send only the changes, using `changed_registers` and `written_addresses`, without comparing whole states.
- The frontend can show each phase later without rewriting the CPU.
- The estimated cost is 10–20% of speed `[estimate]`. If the A8 benchmark (at least 100k instr/s) fails, `run()` gets a fast path that skips building records (guide step 3.8).
