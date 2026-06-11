"""Canonical KoalaByte firmware entry point."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Iterable

from .config import CONFIG, as_dict
from .cyberpet_ai import KoalaByteCompanion
from .safety import assert_safe_runtime
from .drivers import ai_bridge, battery, camera, display, eye_display, gps, ir, nfc, sdr, subghz, wireless

LOG = logging.getLogger("koalabyte")

DRIVERS = [
    display.DisplayDriver,
    camera.CameraDriver,
    eye_display.EyeDisplayDriver,
    ai_bridge.AiBridgeDriver,
    battery.BatteryDriver,
    wireless.WirelessDriver,
    nfc.NfcDriver,
    gps.GpsDriver,
    sdr.SdrDriver,
    subghz.SubGhzDriver,
    ir.IrDriver,
]


def configure_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def run_self_test() -> int:
    results = []
    for driver_cls in DRIVERS:
        driver = driver_cls(CONFIG)
        results.append(driver.self_test())

    print(json.dumps({"config": as_dict(), "self_test": results}, indent=2, default=str))
    failed = [r for r in results if r["status"] == "fail"]
    return 1 if failed else 0


def run_voice_transcript(transcript: str) -> int:
    """Handle a speech-to-text transcript through the AI pet voice router."""
    companion = KoalaByteCompanion()
    response = companion.speak(transcript)
    print(json.dumps(response.__dict__, indent=2, default=str))
    return 0


def run_firmware() -> int:
    assert_safe_runtime()
    companion = KoalaByteCompanion()
    status = companion.boot_message()
    LOG.info("%s", status.message)

    initialized = []
    for driver_cls in DRIVERS:
        driver = driver_cls(CONFIG)
        initialized.append(driver.initialize())

    LOG.info("KoalaByte initialized: %s", ", ".join(initialized))
    LOG.info("%s", companion.explain_guardrail())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KoalaByte firmware runtime")
    parser.add_argument("--self-test", action="store_true", help="Run hardware/config self-test and exit")
    parser.add_argument("--print-config", action="store_true", help="Print resolved KoalaByte config and exit")
    parser.add_argument(
        "--voice-transcript",
        help="Send a speech-to-text transcript to the AI pet and print its answer/action plan",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    if args.print_config:
        print(json.dumps(as_dict(), indent=2, default=str))
        return 0
    if args.self_test:
        return run_self_test()
    if args.voice_transcript:
        return run_voice_transcript(args.voice_transcript)
    return run_firmware()


if __name__ == "__main__":
    sys.exit(main())
