# 0011. TDD with pytest; all code written by hand

- **Status:** Accepted
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §11](../specs/cpu-core.md#11-evaluation-plan), [implementation guide](../implementation-guide.md)

## Context
This is a learning project. The aim is to understand every part of the CPU by building it.

## Decision
- All code and tests are written by hand. AI tools may explain, design, review and write docs, but they don't write code.
- Each guide step starts with a failing test, followed by the smallest code that makes it pass.
- `python -m pytest` must pass before work moves to the next milestone.
- The simulator uses only the Python standard library. pytest is the only dev dependency.

## Consequences
- Progress is slower, but the code is fully understood.
- The test suite records what the CPU promises. A spec change starts with a test change.
- Each finished milestone gets a git tag (`M1-complete`, and so on), so the history shows progress.
