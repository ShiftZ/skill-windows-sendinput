---
name: windows-sendinput
description: Send relative Windows mouse input from Python through Win32 SendInput. Use when Codex needs to generate or run mouse-delta input patterns on Windows, drive or test a Windows app or game with relative mouse motion, test raw mouse paths such as WM_INPUT, or build parameterized SendInput mouse sender scripts from generator patterns.
---

# Windows SendInput

Use the bundled Python scripts for relative mouse motion on Windows. Keep motion generation separate from input delivery: generators yield `(dx, dy)` deltas and `send_mouse_deltas()` sends them at a fixed rate through Win32 `SendInput`.

## Workflow

1. Prefer `scripts/send_mouse_circle.py` when the requested pattern is a circle.
2. Use `scripts/win_send_input.py` as the base for new relative mouse motion scripts.
3. Keep new patterns as iterables or generators of signed relative mouse deltas.
4. Run real input injection with Windows desktop access. A sandboxed Python run may complete without moving the visible cursor or reaching the interactive target.
5. Treat sender success as sender-side evidence only. Instrument or observe the target application when target receipt matters.

## Circle Sender

Run the parameterized circle sender with Python:

```powershell
python scripts/send_mouse_circle.py --rate-hz 90 --radius 240 --loop-seconds 1 --duration-seconds 5
```

Use `--help` to inspect the current CLI options.

## Base Sender

Import the base runner for new scripts:

```python
from win_send_input import send_mouse_deltas


def line_deltas():
    for _ in range(90):
        yield 4, 0


send_mouse_deltas(90, line_deltas())
```

The delta iterable controls duration by exhaustion. The runner owns rate scheduling and raises if `SendInput` fails.

## Input Notes

- Use relative deltas for unbounded mouse-look style motion. Do not model it with client-area cursor coordinates.
- `SendInput` injects into the Windows input stream; it does not target a specific window or process.
- A target receiving `WM_INPUT` must have the relevant raw input registration. If background receipt matters, verify the target's raw-input flags and target-side handling instead of assuming the sender is sufficient.
