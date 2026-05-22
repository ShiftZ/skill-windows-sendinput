---
name: windows-sendinput
description: Send Windows mouse input from Python through Win32 SendInput. Use when Codex needs to generate or run mouse-delta or mouse-button input patterns on Windows, drive or test a Windows app or game with relative mouse motion or button events, test raw mouse paths such as WM_INPUT, or build parameterized SendInput mouse sender scripts from generator patterns.
---

# Windows SendInput

Use the bundled Python scripts for relative mouse motion and button events on Windows. Keep input generation separate from delivery: generators yield deltas or button event constants and the base runners send them at a fixed rate through Win32 `SendInput`.

## Workflow

1. Prefer `scripts/send_mouse_circle.py` when the requested pattern is a circle.
2. Run `scripts/win_send_input.py` directly for one relative move or one button event.
3. Use `scripts/win_send_input.py` as the base for new mouse sender scripts.
4. Keep new patterns as iterables or generators of signed relative mouse deltas or button event constants.
5. Run real input injection with Windows desktop access. A sandboxed Python run may complete without moving the visible cursor or reaching the interactive target.
6. Treat sender success as sender-side evidence only. Instrument or observe the target application when target receipt matters.

## Circle Sender

Run the parameterized circle sender with Python:

```powershell
python scripts/send_mouse_circle.py --rate-hz 90 --radius 240 --loop-seconds 1 --duration-seconds 5
```

Use `--help` to inspect the current CLI options.

## Primitive Sender

Run one relative move or one mouse button event:

```powershell
python scripts/win_send_input.py mouse_move --dx 40 --dy -10
python scripts/win_send_input.py mouse_button MOUSE_LEFT_CLICK
```

Use `mouse_button --help` to inspect the button event constants.

## Base Sender

Import the base runners for new scripts:

```python
from win_send_input import MOUSE_LEFT_CLICK, send_mouse_button_events, send_mouse_deltas


def line_deltas():
    for _ in range(90):
        yield 4, 0


send_mouse_deltas(90, line_deltas())


def click_events():
    for _ in range(10):
        yield MOUSE_LEFT_CLICK


send_mouse_button_events(10, click_events())
```

The iterable controls duration by exhaustion. A click event occupies one rate tick and emits its down and up inputs together. The runners own rate scheduling and raise if `SendInput` fails.

## Input Notes

- Use relative deltas for unbounded mouse-look style motion. Do not model it with client-area cursor coordinates.
- `SendInput` injects into the Windows input stream; it does not target a specific window or process.
- A target receiving `WM_INPUT` must have the relevant raw input registration. If background receipt matters, verify the target's raw-input flags and target-side handling instead of assuming the sender is sufficient.
