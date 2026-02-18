from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline
from temporal_gradient.salience.provenance import compute_provenance_hash


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
                "PROVENANCE_HASH": compute_provenance_hash(result.provenance),
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
