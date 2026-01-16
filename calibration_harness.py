import json
import random
import statistics
import time

from chronos_engine import ClockRateModulator
from entropic_decay import DecayEngine, EntropicMemory, initial_strength_from_psi, should_encode
from salience_pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline


def deterministic_tick(clock, psi, wall_delta, current_time):
    clock.last_tick = current_time
    next_time = current_time + wall_delta
    original_time = time.time
    try:
        time.time = lambda: next_time
        clock.tick(psi=psi)
    finally:
        time.time = original_time
    return next_time


def run_calibration():
    random.seed(1337)

    events = [
        "Boot sequence initiated.",
        "Operator note: check coolant levels.",
        "CRITICAL: magnetic field instability detected.",
        "Routine telemetry sweep complete.",
        "Never override the pressure relief protocol.",
        "System idle. Monitoring continues.",
    ]

    salience = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())
    clock = ClockRateModulator(base_dilation_factor=1.0, min_clock_rate=0.05)
    decay = DecayEngine(half_life=30.0, prune_threshold=0.2)

    clock.start_wall_time = 0.0
    clock.last_tick = 0.0
    wall_time = 0.0

    psi_values = []
    clock_rates = []

    for text in events:
        sal = salience.evaluate(text)
        wall_time = deterministic_tick(clock, sal.psi, wall_delta=1.0, current_time=wall_time)
        psi_values.append(sal.psi)
        clock_rates.append(clock.clock_rate_from_psi(sal.psi))

        if should_encode(sal.psi, threshold=0.3):
            strength = initial_strength_from_psi(sal.psi, S_max=1.2)
            memory = EntropicMemory(text, initial_weight=strength)
            decay.add_memory(memory, clock.tau)

    wall_time = deterministic_tick(clock, psi=0.0, wall_delta=5.0, current_time=wall_time)
    survivors, pruned = decay.entropy_sweep(clock.tau)

    summary = {
        "SALIENCE_MEAN": round(statistics.mean(psi_values), 4),
        "SALIENCE_MEDIAN": round(statistics.median(psi_values), 4),
        "CLOCK_RATE_MIN": round(min(clock_rates), 4),
        "CLOCK_RATE_MAX": round(max(clock_rates), 4),
        "MEMORY_COUNT": len(decay.vault),
        "MEMORY_SURVIVORS": len(survivors),
        "MEMORY_PRUNED": len(pruned),
        "TAU": round(clock.tau, 4),
    }

    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    run_calibration()
