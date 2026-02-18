from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import temporal_gradient as tg
from temporal_gradient.memory.decay import DecayEngine, EntropicMemory
from temporal_gradient.telemetry.chronometric_vector import ChronometricVector
from temporal_gradient.telemetry.schema import validate_packet_schema


NORMAL_EVENTS = [
    "scan ok item=A123 qty=1",
    "scan ok item=B552 qty=2",
    "move ok bin=R12 to=R13",
    "pick ok order=7712 lines=3",
]

ANOMALY_EVENTS = [
    "CRITICAL: temp sensor out of range - freezer_03",
    "URGENT: unexpected inventory delta item=G999 delta=-40",
    "SECURITY: after-hours access badge=UNKNOWN door=Receiving",
    "ALERT: repeated failed pick confirmations station=07",
]


@dataclass(frozen=True)
class SimulatedEvent:
    t: float
    text: str
    kind: str


def simulate_events(n: int = 50) -> list[SimulatedEvent]:
    anomaly_at = {12: 0, 27: 1, 41: 2}
    events: list[SimulatedEvent] = []
    for i in range(n):
        if i in anomaly_at:
            events.append(SimulatedEvent(t=float(i), text=ANOMALY_EVENTS[anomaly_at[i]], kind="anomaly"))
        else:
            events.append(SimulatedEvent(t=float(i), text=random.choice(NORMAL_EVENTS), kind="normal"))
    return events


def run_poc(*, config_path: str = "tg.yaml", n_events: int = 50) -> dict[str, Any]:
    cfg = tg.load_config(config_path)
    random.seed(cfg.policies.deterministic_seed)

    salience = tg.salience.SaliencePipeline(
        tg.salience.RollingJaccardNovelty(window_size=cfg.salience.window_size),
        tg.salience.KeywordImperativeValue(
            keywords=cfg.salience.keywords,
            base_value=cfg.salience.base_value,
            hit_value=cfg.salience.hit_value,
            max_value=cfg.salience.max_value,
        ),
    )

    clock = tg.clock.ClockRateModulator(
        base_dilation_factor=cfg.clock.base_dilation_factor,
        min_clock_rate=cfg.clock.min_clock_rate,
        salience_mode=cfg.clock.salience_mode,
        legacy_density_scale=cfg.clock.legacy_density_scale,
    )

    decay = DecayEngine(
        half_life=cfg.memory.half_life,
        prune_threshold=cfg.memory.prune_threshold,
        decay_lambda=cfg.memory.decay_lambda,
        s_max=cfg.memory.s_max,
    )

    cooldown_policy = tg.policies.ComputeCooldownPolicy(cooldown_tau=cfg.policies.cooldown_tau)
    wall_delta = cfg.policies.event_wall_delta
    sweep_every = max(1, int(cfg.policies.calibration_post_sweep_wall_delta))

    packets: list[dict[str, Any]] = []
    write_log: list[dict[str, float]] = []
    last_compute_tau = float("-inf")

    for idx, event in enumerate(simulate_events(n_events)):
        s = salience.evaluate(event.text)
        clock.tick(psi=s.psi, wall_delta=wall_delta)

        mem_strength = 0.0
        encoded = tg.memory.should_encode(s.psi, threshold=cfg.memory.encode_threshold)
        elapsed_tau = clock.tau - last_compute_tau
        compute_allowed = cooldown_policy.allows_compute(elapsed_tau=elapsed_tau)

        if encoded and compute_allowed:
            strength_cap = min(cfg.memory.initial_strength_max, cfg.memory.s_max)
            mem_strength = tg.memory.initial_strength_from_psi(s.psi, S_max=strength_cap)
            memory = EntropicMemory(content=event.text, initial_weight=mem_strength, s_max=cfg.memory.s_max)
            decay.add_memory(memory, current_tau=clock.tau)
            last_compute_tau = clock.tau
            write_log.append({"tau": round(clock.tau, 4), "strength": round(mem_strength, 6)})

        if (idx + 1) % sweep_every == 0:
            decay.entropy_sweep(current_tau=clock.tau)

        packet = json.loads(
            ChronometricVector(
                wall_clock_time=(idx + 1) * wall_delta,
                tau=clock.tau,
                psi=s.psi,
                recursion_depth=0,
                clock_rate=clock.clock_rate_from_psi(s.psi),
                H=s.novelty,
                V=s.value,
                memory_strength=mem_strength,
            ).to_packet()
        )

        validate_packet_schema(packet, salience_mode=cfg.clock.salience_mode)
        packet["EVENT_KIND"] = event.kind
        packet["ENCODED"] = bool(encoded)
        packet["COMPUTE_ALLOWED"] = bool(compute_allowed)
        packets.append(packet)

    alive, forgotten = decay.entropy_sweep(current_tau=clock.tau)
    total_swept_survivors = len(alive)
    total_swept_forgotten = len(forgotten)

    return {
        "config": {
            "salience": asdict(cfg.salience),
            "clock": asdict(cfg.clock),
            "memory": asdict(cfg.memory),
            "policies": asdict(cfg.policies),
        },
        "seed": cfg.policies.deterministic_seed,
        "n_packets": len(packets),
        "tau_final": packets[-1]["TAU"],
        "avg_salience": sum(p["SALIENCE"] for p in packets) / len(packets),
        "max_salience": max(p["SALIENCE"] for p in packets),
        "encoded_count": sum(1 for p in packets if p["ENCODED"]),
        "compute_allowed_count": sum(1 for p in packets if p["COMPUTE_ALLOWED"]),
        "total_swept_survivors": total_swept_survivors,
        "total_swept_forgotten": total_swept_forgotten,
        # Backward-compatible aliases maintained for one release window.
        "memories_alive": total_swept_survivors,
        "memories_forgotten": total_swept_forgotten,
        "write_log": write_log,
        "anomaly_packets": [p for p in packets if p["EVENT_KIND"] == "anomaly"][:5],
        "head": packets[:3],
        "tail": packets[-3:],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic anomaly-stream PoC for Temporal Gradient.")
    parser.add_argument("--config", default="tg.yaml", help="Path to tg.yaml config")
    parser.add_argument("--events", type=int, default=50, help="Number of simulated events")
    parser.add_argument("--output", type=Path, help="Optional path to write full JSON summary")
    args = parser.parse_args()

    summary = run_poc(config_path=args.config, n_events=args.events)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
