"""Check RP2040 GPIO assignments for aliases of a hardware PWM channel."""

import argparse
from collections import defaultdict
import sys

HEADER_GPIOS = frozenset(range(23)) | {26, 27, 28}


def gpio_number(value: str) -> int:
    """Parse a chip GPIO number such as 16 or GP16."""
    try:
        pin = int(value.upper().removeprefix("GP"))
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected a GPIO number, got {value!r}") from None
    if not 0 <= pin <= 29:
        raise argparse.ArgumentTypeError("RP2040 GPIO numbers range from 0 to 29")
    return pin


def pwm_channel(pin: int) -> tuple[int, str]:
    """Return the PWM slice and compare channel for an RP2040 GPIO."""
    return (pin // 2) % 8, "AB"[pin % 2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--board",
        choices=("rp2040", "pico", "pico-w"),
        default="rp2040",
        help="use pico or pico-w to check the standard header as well",
    )
    parser.add_argument(
        "--header-pin",
        action="append",
        default=[],
        type=gpio_number,
        metavar="GPIO",
        help="also check an auxiliary GPIO, such as an enable pin, for header exposure",
    )
    parser.add_argument("pins", nargs="+", type=gpio_number, metavar="GPIO")
    args = parser.parse_args(argv)
    if args.header_pin and args.board == "rp2040":
        parser.error("--header-pin requires --board pico or --board pico-w")

    channels: dict[tuple[int, str], list[int]] = defaultdict(list)
    print("GPIO  Slice  Channel")
    for pin in args.pins:
        slice_number, channel = pwm_channel(pin)
        channels[slice_number, channel].append(pin)
        print(f"GP{pin:<2}  {slice_number:>5}  {channel:>7}")

    failed = False
    for (slice_number, channel), pins in channels.items():
        if len(pins) > 1:
            names = ", ".join(f"GP{pin}" for pin in pins)
            print(f"Conflict: {names} share PWM{slice_number}{channel}.", file=sys.stderr)
            failed = True

    if args.board != "rp2040":
        used_pins = args.pins + args.header_pin
        unavailable = dict.fromkeys(pin for pin in used_pins if pin not in HEADER_GPIOS)
        for pin in unavailable:
            print(f"GP{pin} is not exposed on the {args.board} header.", file=sys.stderr)
            failed = True

    if failed:
        return 1
    print("No PWM channel conflicts found for these GPIOs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
