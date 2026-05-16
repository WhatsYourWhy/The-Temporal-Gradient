"""Showcase: salience-weighted memory vs. a naive LRU on a noisy event stream.

Deterministic, no sleeps. Both systems see the same 20 events. The naive
system keeps the last N items. Temporal Gradient retains items by
salience-decayed strength.

The point: the critical event arrives at index 6, then 13 routine events
follow. A flat LRU evicts it. Temporal Gradient does not.

Run:
    python examples/showcase.py
"""

import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from temporal_gradient.clock.chronos import ClockRateModulator
from temporal_gradient.memory.decay import (
    DecayEngine,
    EntropicMemory,
    initial_strength_from_psi,
    should_encode,
)
from temporal_gradient.salience.pipeline import (
    KeywordImperativeValue,
    RollingJaccardNovelty,
    SaliencePipeline,
)

LRU_CAPACITY = 5
WALL_DELTA = 1.0

EVENTS = [
    "request handled ok",
    "disk usage at 42 percent",
    "request handled ok",
    "cache hit ratio nominal",
    "request handled ok",
    "disk usage at 43 percent",
    "CRITICAL auth service unreachable must page oncall",  # <-- the signal
    "request handled ok",
    "cache hit ratio nominal",
    "request handled ok",
    "disk usage at 43 percent",
    "request handled ok",
    "cache hit ratio nominal",
    "request handled ok",
    "disk usage at 44 percent",
    "request handled ok",
    "cache hit ratio nominal",
    "request handled ok",
    "disk usage at 44 percent",
    "request handled ok",
]


def run_naive():
    """Flat LRU: always keep the last N events. No notion of importance."""
    lru: deque[str] = deque(maxlen=LRU_CAPACITY)
    for text in EVENTS:
        lru.append(text)
    return list(lru)


def run_temporal_gradient():
    """Salience-modulated clock + entropic decay."""
    clock = ClockRateModulator(base_dilation_factor=4.0, min_clock_rate=0.1)
    decay = DecayEngine(half_life=8.0, prune_threshold=0.15)
    salience = SaliencePipeline(
        RollingJaccardNovelty(window_size=5),
        KeywordImperativeValue(),
    )

    for text in EVENTS:
        s = salience.evaluate(text)
        clock.tick(s.psi, wall_delta=WALL_DELTA)
        if should_encode(s.psi, threshold=0.25):
            strength = initial_strength_from_psi(s.psi, S_max=1.2)
            decay.add_memory(EntropicMemory(text, initial_weight=strength), clock.tau)

    survivors, _ = decay.entropy_sweep(clock.tau)
    survivors.sort(key=lambda pair: pair[1], reverse=True)
    return survivors


def critical_survived(items) -> bool:
    return any("CRITICAL" in (s if isinstance(s, str) else s[0].content) for s in items)


def main():
    print("=" * 72)
    print("  Temporal Gradient showcase: noisy stream, one critical signal")
    print("=" * 72)
    print(f"  Stream length: {len(EVENTS)} events. Critical signal at index 6.\n")

    naive = run_naive()
    print(f"NAIVE LRU (capacity={LRU_CAPACITY}) — retained:")
    for text in naive:
        marker = "  *" if "CRITICAL" in text else "   "
        print(f"{marker} {text}")
    print(f"\n  critical signal retained: {critical_survived(naive)}\n")

    tg = run_temporal_gradient()
    print(f"TEMPORAL GRADIENT (salience-decayed) — retained ({len(tg)} items):")
    for mem, strength in tg:
        marker = "  *" if "CRITICAL" in mem.content else "   "
        print(f"{marker} [S={strength:.2f}] {mem.content}")
    print(f"\n  critical signal retained: {critical_survived(tg)}")
    print("=" * 72)
    print("  The naive system evicts the critical event with routine traffic.")
    print("  Temporal Gradient retains it because salience drove encoding")
    print("  strength, and routine repeats decay along internal time.")
    print("=" * 72)


if __name__ == "__main__":
    main()
