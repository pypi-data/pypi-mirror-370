"""Command-line interface for MH-Z14A CO₂ sensor."""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import NoReturn

from .exceptions import MHZ14AError
from .sensor import MHZ14A, VALID_RANGES


def error_exit(message: str) -> NoReturn:
    """Print error message to stderr and exit with code 1."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="MH-Z14A CO₂ sensor command-line interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mhz14a --port /dev/mhz14a read
  mhz14a --port /dev/ttyUSB0 sample --interval 5 --count 10 --json
  mhz14a --port /dev/mhz14a zero
  mhz14a --port /dev/mhz14a span --ppm 2000
  mhz14a --port /dev/mhz14a abc --on
  mhz14a --port /dev/mhz14a range --max 5000
        """
    )

    parser.add_argument(
        "--port",
        default="/dev/mhz14a",
        help="Serial port path (default: /dev/mhz14a)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Serial timeout in seconds (default: 1.0)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # read command
    subparsers.add_parser("read", help="Read CO₂ concentration")

    # sample command
    sample_parser = subparsers.add_parser(
        "sample",
        help="Take multiple CO₂ readings"
    )
    sample_parser.add_argument(
        "--interval",
        type=float,
        required=True,
        help="Interval between readings in seconds"
    )
    sample_parser.add_argument(
        "--count",
        type=int,
        required=True,
        help="Number of readings to take"
    )
    sample_parser.add_argument(
        "--json",
        action="store_true",
        help="Output readings in JSON format"
    )

    # zero command
    subparsers.add_parser(
        "zero",
        help="Perform zero point calibration (400 ppm fresh air)"
    )

    # span command
    span_parser = subparsers.add_parser(
        "span",
        help="Perform span calibration"
    )
    span_parser.add_argument(
        "--ppm",
        type=int,
        required=True,
        help="Known CO₂ concentration for calibration"
    )

    # abc command
    abc_parser = subparsers.add_parser(
        "abc",
        help="Configure Automatic Baseline Correction"
    )
    abc_group = abc_parser.add_mutually_exclusive_group(required=True)
    abc_group.add_argument("--on", action="store_true", help="Enable ABC")
    abc_group.add_argument("--off", action="store_true", help="Disable ABC")

    # range command
    range_parser = subparsers.add_parser(
        "range",
        help="Set measurement range"
    )
    range_parser.add_argument(
        "--max",
        type=int,
        choices=list(VALID_RANGES),
        required=True,
        help="Maximum measurement range in ppm"
    )

    return parser


def cmd_read(sensor: MHZ14A) -> None:
    """Execute read command."""
    try:
        ppm = sensor.read_co2()
        print(f"{ppm}")
    except MHZ14AError as e:
        error_exit(f"Failed to read CO₂: {e}")


def cmd_sample(sensor: MHZ14A, interval: float, count: int, json_output: bool) -> None:
    """Execute sample command."""
    readings = []

    try:
        for i in range(count):
            if i > 0:
                time.sleep(interval)

            timestamp = datetime.now().isoformat()
            ppm = sensor.read_co2()

            if json_output:
                readings.append({"timestamp": timestamp, "ppm": ppm})
            else:
                print(f"{timestamp}: {ppm} ppm")

    except MHZ14AError as e:
        error_exit(f"Failed to read CO₂: {e}")
    except KeyboardInterrupt:
        if json_output and readings:
            print(json.dumps(readings))
        sys.exit(130)  # 128 + SIGINT

    if json_output:
        print(json.dumps(readings))


def cmd_zero(sensor: MHZ14A) -> None:
    """Execute zero calibration command."""
    try:
        sensor.zero_calibrate()
        print("Zero point calibration completed")
    except MHZ14AError as e:
        error_exit(f"Zero calibration failed: {e}")


def cmd_span(sensor: MHZ14A, ppm: int) -> None:
    """Execute span calibration command."""
    try:
        sensor.span_calibrate(ppm)
        print(f"Span calibration completed with {ppm} ppm")
    except (MHZ14AError, ValueError) as e:
        error_exit(f"Span calibration failed: {e}")


def cmd_abc(sensor: MHZ14A, enable: bool) -> None:
    """Execute ABC configuration command."""
    try:
        sensor.set_abc(enable)
        status = "enabled" if enable else "disabled"
        print(f"Automatic Baseline Correction {status}")
    except MHZ14AError as e:
        error_exit(f"ABC configuration failed: {e}")


def cmd_range(sensor: MHZ14A, max_ppm: int) -> None:
    """Execute range configuration command."""
    try:
        sensor.set_range(max_ppm)
        print(f"Measurement range set to 0-{max_ppm} ppm")
    except (MHZ14AError, ValueError) as e:
        error_exit(f"Range configuration failed: {e}")


def main() -> None:
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        with MHZ14A(args.port, args.timeout) as sensor:
            if args.command == "read":
                cmd_read(sensor)
            elif args.command == "sample":
                cmd_sample(sensor, args.interval, args.count, args.json)
            elif args.command == "zero":
                cmd_zero(sensor)
            elif args.command == "span":
                cmd_span(sensor, args.ppm)
            elif args.command == "abc":
                enable = args.on
                cmd_abc(sensor, enable)
            elif args.command == "range":
                cmd_range(sensor, args.max)

    except MHZ14AError as e:
        error_exit(str(e))
    except KeyboardInterrupt:
        sys.exit(130)  # 128 + SIGINT


if __name__ == "__main__":
    main()
