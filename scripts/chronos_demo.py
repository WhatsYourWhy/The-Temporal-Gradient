"""Chronos demo entrypoint.

Usage:
    python scripts/chronos_demo.py
"""

from __future__ import annotations

import argparse
import sys
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporal_gradient.clock.chronos import ClockRateModulator
from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline
from temporal_gradient.telemetry.chronometric_vector import ChronometricVector


def run_demo(*, sleep_seconds: float = 1.0) -> None:
    agent_clock = ClockRateModulator()
    salience = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())

    print(
        f"{'EVENT':<20} | {'WALL_T':<8} | {'TAU':<10} | {'SALIENCE':<9} | "
        f"{'CLOCK_RATE':<10} | {'MEMORY_S':<8} | {'DEPTH'}"
    )
    print("-" * 90)

    simulated_events = [
        "",
        "Hello.",
        "The quick brown fox jumps over the dog",
        textwrap.dedent(
            """
            Time is a field gradient formed by memory + change.
            Entropy’s arrow is not time itself, but an emergent
            direction from memory accumulation.
        """
        )
        * 5,
    ]

    start_time = time.time()
    for event in simulated_events:
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

        sal = salience.evaluate(event)
        psi = sal.psi

        agent_clock.tick(psi)
        wall_time = time.time() - start_time

        label = (event[:15] + "...") if len(event) > 15 else (event if event else "[EMPTY INPUT]")

        packet_json = ChronometricVector(
            wall_clock_time=wall_time,
            tau=agent_clock.tau,
            psi=psi,
            recursion_depth=0,
            clock_rate=agent_clock.clock_rate_from_psi(psi),
            H=sal.novelty,
            V=sal.value,
            memory_strength=0.0,
        ).to_packet_json()

        print(
            f"{label:<20} | {wall_time:<8.2f} | {agent_clock.tau:<10.4f} | {psi:<9.3f} | "
            f"{agent_clock.clock_rate_from_psi(psi):<10.4f} | {0.0:<8.2f} | {0}"
        )
        print(f"{'PACKET':<8} | {packet_json}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Chronos salience/clock demo.")
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=1.0,
        help="Seconds to sleep between events (default: 1.0). Use 0 for fast smoke tests.",
    )
    args = parser.parse_args()
    run_demo(sleep_seconds=args.sleep_seconds)


if __name__ == "__main__":
    main()
