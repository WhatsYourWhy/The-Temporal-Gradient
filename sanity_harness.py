from __future__ import annotations

import json
from typing import Dict, List, Tuple

from chronos_engine import ClockRateModulator
from chronometric_vector import ChronometricVector
from entropic_decay import DecayEngine, EntropicMemory, initial_strength_from_psi, should_encode
from salience_pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline


def run_harness(events: List[str]) -> Tuple[Dict[str, float], List[Dict[str, float]]]:
    clock = ClockRateModulator(base_dilation_factor=1.0, min_clock_rate=0.05)
    decay = DecayEngine(half_life=20.0, prune_threshold=0.2)
    salience = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())

    wall_time = 0.0
    packets: List[Dict[str, float]] = []
    psi_values: List[float] = []
    clock_rates: List[float] = []
    memories_written = 0

    for text in events:
        wall_time += 1.0
        sal = salience.evaluate(text)
        clock.tick(sal.psi, wall_delta=1.0)
        dilation = clock.clock_rate_from_psi(sal.psi)

        memory_strength = 0.0
        if should_encode(sal.psi, threshold=0.3):
            strength = initial_strength_from_psi(sal.psi, S_max=1.2)
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
