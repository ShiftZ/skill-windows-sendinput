import ctypes
import time
from collections.abc import Iterable
from ctypes import wintypes


INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_MOVE_NOCOALESCE = 0x2000

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


def send_mouse_delta(dx: int, dy: int) -> None:
    event = Input(
        type=INPUT_MOUSE,
        data=InputUnion(
            mi=MouseInput(
                dx=dx,
                dy=dy,
                dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_MOVE_NOCOALESCE,
            )
        ),
    )

    if send_input(1, ctypes.byref(event), ctypes.sizeof(event)) != 1:
        raise ctypes.WinError(ctypes.get_last_error())


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
