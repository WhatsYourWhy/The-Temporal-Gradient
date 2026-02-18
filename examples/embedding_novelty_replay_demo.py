"""Deterministic replay demo for embedding novelty provenance hashes.

This script intentionally avoids model downloads by generating deterministic
"fake" embeddings from event text and pre-populating a local JSON cache.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import random
import sys
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from temporal_gradient.salience.embedding_novelty import JsonDirectoryEmbeddingCache, NoveltyScorer
from temporal_gradient.salience.pipeline import KeywordImperativeValue, SaliencePipeline
from temporal_gradient.salience.provenance import compute_provenance_hash

EVENTS: tuple[str, ...] = (
    "CRITICAL: rotate signing keys before deploy",
    "Reminder: update runbook links",
    "URGENT: stop rollout and inspect anomaly bucket",
    "Reminder: update runbook links",  # repeated to exercise novelty history
)


def _seed_from_text(text: str) -> int:
    digest = sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def _fake_embedding(text: str, *, dim: int = 12) -> tuple[float, ...]:
    rng = random.Random(_seed_from_text(text))
    return tuple(round(rng.uniform(-1.0, 1.0), 6) for _ in range(dim))


def _build_cache(
    *,
    cache_dir: Path,
    events: Iterable[str],
    window_size: int,
    quantization: str,
) -> NoveltyScorer:
    cache = JsonDirectoryEmbeddingCache(cache_dir)
    scorer = NoveltyScorer(
        model_id="demo-mini-embed",
        model_hash="sha256:demo-mini-embed-v1",
        window_size=window_size,
        quantization=quantization,
        cache_backend=cache,
        deterministic_mode=True,
        device="cpu",
        dtype="float32",
        runtime_metadata={"deterministic_runtime_policy": "cpu_fp32"},
        code_version="embedding_novelty_replay_demo_v1",
    )
    for text in events:
        cache.set(scorer._cache_key(text), _fake_embedding(text))
    return scorer


def _run_packets(*, novelty_scorer: NoveltyScorer, events: Iterable[str]) -> list[dict[str, object]]:
    pipeline = SaliencePipeline(
        novelty_scorer=novelty_scorer,
        value_scorer=KeywordImperativeValue(),
    )
    packets: list[dict[str, object]] = []
    for step, text in enumerate(events):
        sal = pipeline.evaluate(text)
        packets.append(
            {
                "step": step,
                "event": text,
                "H": round(sal.novelty, 6),
                "V": round(sal.value, 6),
                "psi": round(sal.psi, 6),
                "PROVENANCE_HASH": compute_provenance_hash(sal.provenance),
            }
        )

    pipeline.reset()
    replay_packets: list[dict[str, object]] = []
    for step, text in enumerate(events):
        sal = pipeline.evaluate(text)
        replay_packets.append(
            {
                "step": step,
                "event": text,
                "H": round(sal.novelty, 6),
                "V": round(sal.value, 6),
                "psi": round(sal.psi, 6),
                "PROVENANCE_HASH": compute_provenance_hash(sal.provenance),
            }
        )

    assert packets == replay_packets, "Replay mismatch: deterministic output changed after reset()"
    return packets


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    config_a = {
        "window_size": 2,
        "quantization": "int8",
        "cache_dir": base_dir / ".cache" / "embeddings_ws2_int8",
    }
    scorer_a = _build_cache(
        cache_dir=config_a["cache_dir"],
        events=EVENTS,
        window_size=config_a["window_size"],
        quantization=config_a["quantization"],
    )
    packets_a = _run_packets(novelty_scorer=scorer_a, events=EVENTS)

    print("=== Deterministic run + replay (window_size=2, quantization=int8) ===")
    print(json.dumps(packets_a, indent=2))

    config_b = {
        "window_size": 3,
        "quantization": "int8",
        "cache_dir": base_dir / ".cache" / "embeddings_ws3_int8",
    }
    scorer_b = _build_cache(
        cache_dir=config_b["cache_dir"],
        events=EVENTS,
        window_size=config_b["window_size"],
        quantization=config_b["quantization"],
    )
    packets_b = _run_packets(novelty_scorer=scorer_b, events=EVENTS)

    print("\n=== Config change (window_size=3) ===")
    print(json.dumps(packets_b, indent=2))

    hashes_a = [packet["PROVENANCE_HASH"] for packet in packets_a]
    hashes_b = [packet["PROVENANCE_HASH"] for packet in packets_b]
    changed = [index for index, (left, right) in enumerate(zip(hashes_a, hashes_b)) if left != right]

    assert changed, "Expected at least one PROVENANCE_HASH change after config update"
    print("\nChanged PROVENANCE_HASH indices after config update:", changed)


if __name__ == "__main__":
    main()
