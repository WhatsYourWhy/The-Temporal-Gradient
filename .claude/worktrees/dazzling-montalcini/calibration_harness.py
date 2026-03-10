import json
import random
import statistics
import time

from temporal_gradient.clock.chronos import ClockRateModulator
from temporal_gradient.memory.decay import DecayEngine, EntropicMemory, initial_strength_from_psi, should_encode
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy
from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline
from temporal_gradient.config_loader import load_config


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


def run_calibration(config_path: str = "tg.yaml"):
    config = load_config(config_path)
    random.seed(config.policies.deterministic_seed)

    events = [
        "Boot sequence initiated.",
        "Operator note: check coolant levels.",
        "CRITICAL: magnetic field instability detected.",
        "Routine telemetry sweep complete.",
        "Never override the pressure relief protocol.",
        "System idle. Monitoring continues.",
    ]

    salience = SaliencePipeline(
        RollingJaccardNovelty(window_size=config.salience.window_size),
        KeywordImperativeValue(
            keywords=config.salience.keywords,
            base_value=config.salience.base_value,
            hit_value=config.salience.hit_value,
            max_value=config.salience.max_value,
        ),
    )
    salience.reset()
    clock = ClockRateModulator(
        base_dilation_factor=config.clock.base_dilation_factor,
        min_clock_rate=config.clock.min_clock_rate,
        salience_mode=config.clock.salience_mode,
        legacy_density_scale=config.clock.legacy_density_scale,
    )
    decay = DecayEngine(
        half_life=config.memory.half_life,
        prune_threshold=config.memory.prune_threshold,
        decay_lambda=config.memory.decay_lambda,
        s_max=config.memory.s_max,
    )
    cooldown = ComputeCooldownPolicy(cooldown_tau=config.policies.cooldown_tau)

    clock.start_wall_time = 0.0
    clock.last_tick = 0.0
    wall_time = 0.0

    psi_values = []
    clock_rates = []
    last_memory_write_tau = float("-inf")

    for text in events:
        sal = salience.evaluate(text)
        wall_time = deterministic_tick(
            clock,
            sal.psi,
            wall_delta=config.policies.event_wall_delta,
            current_time=wall_time,
        )
        psi_values.append(sal.psi)
        clock_rates.append(clock.clock_rate_from_psi(sal.psi))

        elapsed_since_write = clock.tau - last_memory_write_tau
        if should_encode(sal.psi, threshold=config.memory.encode_threshold) and cooldown.allows_compute(
            elapsed_tau=elapsed_since_write
        ):
            strength_cap = min(config.memory.initial_strength_max, config.memory.s_max)
            strength = initial_strength_from_psi(sal.psi, S_max=strength_cap)
            memory = EntropicMemory(text, initial_weight=strength, s_max=config.memory.s_max)
            decay.add_memory(memory, clock.tau)
            last_memory_write_tau = clock.tau

    wall_time = deterministic_tick(
        clock,
        psi=0.0,
        wall_delta=config.policies.calibration_post_sweep_wall_delta,
        current_time=wall_time,
    )
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
