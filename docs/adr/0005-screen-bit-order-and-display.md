# 0005. MSB = leftmost pixel; Display decodes, the Bus doesn't

- **Status:** Accepted
- **Date:** 2026-11-05
- **Spec:** [cpu-core.md §4.2, §4.4](../specs/cpu-core.md#42-memory-map), A10

## Context
The screen is 64×32 mono: 2,048 pixels, 16 per word, in 128 words. The pixel order must be fixed, and one part of the system has to turn words into pixels.

## Decision
- Pixel `(x, y)` lives in word `0xD000 + y*4 + x//16`, at bit `15 - x%16`. The most significant bit is the leftmost pixel.
- The Bus only stores the 128 words and returns them with `screen_pixels()`.
- `Display.pixels(words)` decodes the words into 32 rows × 64 bools, like a video chip.

## Consequences
- Writing `0x8000` to `0xD000` lights pixel (0,0). A binary literal in the source reads left to right, the same as the screen.
- The Bus stays a router (see [0002](0002-cpu-talks-only-to-bus.md)). The terminal runner and the React frontend can both reuse `Display`, or decode on their own side.
- Decoding 2,048 pixels in Python takes time. Decode only when the screen is drawn, not on every step.
