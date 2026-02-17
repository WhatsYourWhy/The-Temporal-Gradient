from __future__ import annotations

import json
from typing import Dict, List, Tuple

from chronos_engine import ClockRateModulator
from chronometric_vector import ChronometricVector
from entropic_decay import DecayEngine, EntropicMemory, initial_strength_from_psi, should_encode
from salience_pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline
from temporal_gradient.config import TemporalGradientConfig, load_config


def run_harness(
    events: List[str],
    config: TemporalGradientConfig | None = None,
    config_path: str = "tg.yaml",
) -> Tuple[Dict[str, float], List[Dict[str, float]]]:
    active_config = config or load_config(config_path)

    clock = ClockRateModulator(
        base_dilation_factor=active_config.clock.base_dilation_factor,
        min_clock_rate=active_config.clock.min_clock_rate,
        salience_mode=active_config.clock.salience_mode,
        legacy_density_scale=active_config.clock.legacy_density_scale,
    )
    decay = DecayEngine(
        half_life=active_config.memory.half_life,
        prune_threshold=active_config.memory.prune_threshold,
    )
    salience = SaliencePipeline(
        RollingJaccardNovelty(window_size=active_config.salience.window_size),
        KeywordImperativeValue(
            keywords=active_config.salience.keywords,
            base_value=active_config.salience.base_value,
            hit_value=active_config.salience.hit_value,
            max_value=active_config.salience.max_value,
        ),
    )

    wall_time = 0.0
    packets: List[Dict[str, float]] = []
    psi_values: List[float] = []
    clock_rates: List[float] = []
    memories_written = 0

    for text in events:
        wall_time += active_config.policies.event_wall_delta
        sal = salience.evaluate(text)
        clock.tick(sal.psi, wall_delta=active_config.policies.event_wall_delta)
        dilation = clock.clock_rate_from_psi(sal.psi)

        memory_strength = 0.0
        if should_encode(sal.psi, threshold=active_config.memory.encode_threshold):
            strength = initial_strength_from_psi(
                sal.psi,
                S_max=active_config.memory.initial_strength_max,
            )
            memory_strength = strength
            mem = EntropicMemory(text, initial_weight=strength)
            decay.add_memory(mem, clock.tau)
            memories_written += 1

        vector = ChronometricVector(
            wall_clock_time=wall_time,
            tau=clock.tau,
            psi=sal.psi,
            recursion_depth=0,
            clock_rate=dilation,
            H=sal.novelty,
            V=sal.value,
            memory_strength=memory_strength,
        )
        packets.append(json.loads(vector.to_packet()))
        psi_values.append(sal.psi)
        clock_rates.append(dilation)

    survivors, _ = decay.entropy_sweep(clock.tau)
    summary = {
        "psi_min": min(psi_values) if psi_values else 0.0,
        "psi_max": max(psi_values) if psi_values else 0.0,
        "psi_mean": sum(psi_values) / len(psi_values) if psi_values else 0.0,
        "clock_rate_min": min(clock_rates) if clock_rates else 0.0,
        "clock_rate_max": max(clock_rates) if clock_rates else 0.0,
        "clock_rate_mean": sum(clock_rates) / len(clock_rates) if clock_rates else 0.0,
        "tau_final": clock.tau,
        "memories_written": float(memories_written),
        "memories_alive_after_tau": float(len(survivors)),
    }
    return summary, packets


def main() -> None:
    events = [
        "System boot sequence initiated.",
        "CRITICAL: SECURITY BREACH DETECTED.",
        "Rain. Water. Liquid.",
        "My name is Sentinel.",
        "System standby.",
    ]
    summary, packets = run_harness(events)
    for packet in packets:
        print(json.dumps(packet))
    print(json.dumps({"summary": summary}))


if __name__ == "__main__":
    main()
