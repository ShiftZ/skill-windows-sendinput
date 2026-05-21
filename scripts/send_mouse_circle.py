import argparse
import math
import time
from collections.abc import Iterable

from win_send_input import send_mouse_deltas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send relative mouse deltas in a circle via Win32 SendInput.")
    parser.add_argument("--rate-hz", type=float, default=90, help="Mouse delta rate. Default: 90.")
    parser.add_argument("--radius", type=int, default=240, help="Circle radius in relative mouse units. Default: 240.")
    parser.add_argument("--loop-seconds", type=float, default=1.0, help="Seconds per circle. Default: 1.0.")
    parser.add_argument("--duration-seconds", type=float, default=5.0, help="Total send duration. Default: 5.0.")
    return parser.parse_args()


def circle_deltas(
    radius: int,
    rate_hz: float,
    loop_seconds: float,
    duration_seconds: float,
) -> Iterable[tuple[int, int]]:
    if rate_hz <= 0:
        raise ValueError("rate_hz must be positive")
    if loop_seconds <= 0:
        raise ValueError("loop_seconds must be positive")
    if duration_seconds < 0:
        raise ValueError("duration_seconds cannot be negative")

    samples_per_loop = round(rate_hz * loop_seconds)
    total_samples = round(rate_hz * duration_seconds)
    if samples_per_loop == 0:
        raise ValueError("loop_seconds is shorter than one sample")

    previous_x = round(radius * math.cos(0.0))
    previous_y = round(radius * math.sin(0.0))

    for sample in range(1, total_samples + 1):
        angle = math.tau * sample / samples_per_loop
        next_x = round(radius * math.cos(angle))
        next_y = round(radius * math.sin(angle))

        yield next_x - previous_x, next_y - previous_y

        previous_x = next_x
        previous_y = next_y


def main() -> None:
    args = parse_args()
    deltas = circle_deltas(
        radius=args.radius,
        rate_hz=args.rate_hz,
        loop_seconds=args.loop_seconds,
        duration_seconds=args.duration_seconds,
    )

    start_time = time.perf_counter()
    total_samples = send_mouse_deltas(args.rate_hz, deltas)
    elapsed = time.perf_counter() - start_time
    print(f"Sent {total_samples} relative moves in {elapsed:.3f} seconds.")


if __name__ == "__main__":
    main()
