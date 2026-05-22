import argparse
import ctypes
import time
from collections.abc import Iterable
from ctypes import wintypes


INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
MOUSEEVENTF_MOVE_NOCOALESCE = 0x2000

MOUSE_LEFT_DOWN = ((MOUSEEVENTF_LEFTDOWN, 0),)
MOUSE_LEFT_UP = ((MOUSEEVENTF_LEFTUP, 0),)
MOUSE_LEFT_CLICK = (*MOUSE_LEFT_DOWN, *MOUSE_LEFT_UP)

MOUSE_RIGHT_DOWN = ((MOUSEEVENTF_RIGHTDOWN, 0),)
MOUSE_RIGHT_UP = ((MOUSEEVENTF_RIGHTUP, 0),)
MOUSE_RIGHT_CLICK = (*MOUSE_RIGHT_DOWN, *MOUSE_RIGHT_UP)

MOUSE_MIDDLE_DOWN = ((MOUSEEVENTF_MIDDLEDOWN, 0),)
MOUSE_MIDDLE_UP = ((MOUSEEVENTF_MIDDLEUP, 0),)
MOUSE_MIDDLE_CLICK = (*MOUSE_MIDDLE_DOWN, *MOUSE_MIDDLE_UP)

MOUSE_X1_DOWN = ((MOUSEEVENTF_XDOWN, 0x0001),)
MOUSE_X1_UP = ((MOUSEEVENTF_XUP, 0x0001),)
MOUSE_X1_CLICK = (*MOUSE_X1_DOWN, *MOUSE_X1_UP)

MOUSE_X2_DOWN = ((MOUSEEVENTF_XDOWN, 0x0002),)
MOUSE_X2_UP = ((MOUSEEVENTF_XUP, 0x0002),)
MOUSE_X2_CLICK = (*MOUSE_X2_DOWN, *MOUSE_X2_UP)

MOUSE_BUTTON_EVENTS = {
    name: event
    for name, event in globals().items()
    if name.startswith("MOUSE_") and name.endswith(("DOWN", "UP", "CLICK"))
}

ULONG_PTR = ctypes.c_size_t


class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class InputUnion(ctypes.Union):
    _fields_ = [("mi", MouseInput)]


class Input(ctypes.Structure):
    _anonymous_ = ("data",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("data", InputUnion),
    ]


user32 = ctypes.WinDLL("user32", use_last_error=True)
send_input = user32.SendInput
send_input.argtypes = (wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int)
send_input.restype = wintypes.UINT


def wait_until(deadline: float) -> None:
    while True:
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return

        time.sleep(min(remaining, 0.001))


def send_mouse_input(dx: int = 0, dy: int = 0, mouse_data: int = 0, flags: int = 0) -> None:
    event = Input(
        type=INPUT_MOUSE,
        data=InputUnion(
            mi=MouseInput(
                dx=dx,
                dy=dy,
                mouseData=mouse_data,
                dwFlags=flags,
            )
        ),
    )

    if send_input(1, ctypes.byref(event), ctypes.sizeof(event)) != 1:
        raise ctypes.WinError(ctypes.get_last_error())


def send_mouse_delta(dx: int, dy: int) -> None:
    send_mouse_input(dx=dx, dy=dy, flags=MOUSEEVENTF_MOVE | MOUSEEVENTF_MOVE_NOCOALESCE)


def send_mouse_button_event(event: tuple[tuple[int, int], ...]) -> None:
    for flags, mouse_data in event:
        send_mouse_input(mouse_data=mouse_data, flags=flags)


def send_mouse_deltas(rate_hz: float, deltas: Iterable[tuple[int, int]]) -> int:
    if rate_hz <= 0:
        raise ValueError("rate_hz must be positive")

    frame_seconds = 1.0 / rate_hz
    start_time = time.perf_counter()
    sent = 0

    for sent, (dx, dy) in enumerate(deltas, start=1):
        send_mouse_delta(dx, dy)
        wait_until(start_time + sent * frame_seconds)

    return sent


def send_mouse_button_events(rate_hz: float, events: Iterable[tuple[tuple[int, int], ...]]) -> int:
    if rate_hz <= 0:
        raise ValueError("rate_hz must be positive")

    frame_seconds = 1.0 / rate_hz
    start_time = time.perf_counter()
    sent = 0

    for sent, event in enumerate(events, start=1):
        send_mouse_button_event(event)
        wait_until(start_time + sent * frame_seconds)

    return sent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send primitive Windows mouse inputs through Win32 SendInput.")
    commands = parser.add_subparsers(dest="command", required=True)

    mouse_move = commands.add_parser("mouse_move", help="Send one relative mouse move.")
    mouse_move.add_argument("--dx", type=int, required=True, help="Relative horizontal mouse delta.")
    mouse_move.add_argument("--dy", type=int, required=True, help="Relative vertical mouse delta.")

    mouse_button = commands.add_parser("mouse_button", help="Send one mouse button event.")
    mouse_button.add_argument(
        "event",
        choices=MOUSE_BUTTON_EVENTS,
        help="Button event constant name.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "mouse_move":
        send_mouse_delta(args.dx, args.dy)
        return

    send_mouse_button_event(MOUSE_BUTTON_EVENTS[args.event])


if __name__ == "__main__":
    main()
