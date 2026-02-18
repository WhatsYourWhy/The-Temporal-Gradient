import hashlib
import json

from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline


EVENT_SEQUENCE = [
    "must investigate anomaly now",
    "routine status check",
    "must investigate anomaly now",
    "critical alert requires immediate action",
]


def _fresh_pipeline() -> SaliencePipeline:
    return SaliencePipeline(
        novelty_scorer=RollingJaccardNovelty(window_size=3),
        value_scorer=KeywordImperativeValue(
            keywords=["must", "critical", "immediate"],
            base_value=0.1,
            hit_value=0.2,
            max_value=1.0,
        ),
    )


def _provenance_hash(provenance: dict[str, str]) -> str:
    sorted_items = sorted(provenance.items())
    payload = json.dumps(sorted_items, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _run_event_sequence() -> list[dict[str, object]]:
    pipeline = _fresh_pipeline()
    packets: list[dict[str, object]] = []

    for index, event_text in enumerate(EVENT_SEQUENCE):
        result = pipeline.evaluate(event_text)
        packets.append(
            {
                "event_index": index,
                "event_text": event_text,
                "SALIENCE": result.psi,
                "PROVENANCE_HASH": _provenance_hash(result.provenance),
            }
        )

    return packets


def test_salience_packets_are_deterministic_with_fresh_state():
    run1_packets = _run_event_sequence()
    run2_packets = _run_event_sequence()

    assert run1_packets == run2_packets


def test_salience_packet_hashes_are_deterministic_per_event():
    run1_hashes = [packet["PROVENANCE_HASH"] for packet in _run_event_sequence()]
    run2_hashes = [packet["PROVENANCE_HASH"] for packet in _run_event_sequence()]

    assert run1_hashes == run2_hashes
