from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline
from temporal_gradient.salience.provenance import compute_provenance_hash

from tests.replay_assertions import assert_numeric_diagnostics_policy, assert_strict_invariants


EVENT_SEQUENCE = [
    "must investigate anomaly now",
    "routine status check",
    "must investigate anomaly now",
    "critical alert requires immediate action",
]

EXPECTED_SALIENCE = [0.30000000000000004, 0.1, 0.0, 0.5]
EXPECTED_PROVENANCE_HASHES = [
    "20fe1fcf6a60eba42ffbc928d0a9d29932c780d02519bcc564a3289afbed0619",
    "ddc2c6d1d7caa5f9b86b57237aae8b4980e6405113471a479c548d257775a0dc",
    "20fe1fcf6a60eba42ffbc928d0a9d29932c780d02519bcc564a3289afbed0619",
    "c99741c0badfa8b3da70f006317193e13ec483786bbd72ac1c0b49e0de2f6970",
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
                "diagnostics": result.diagnostics,
            }
        )

    return packets


def test_salience_packets_are_deterministic_with_fresh_state():
    run1_packets = _run_event_sequence()
    run2_packets = _run_event_sequence()

    assert_strict_invariants(
        run1_packets,
        expected_event_order=EVENT_SEQUENCE,
        expected_salience=EXPECTED_SALIENCE,
        expected_provenance_hashes=EXPECTED_PROVENANCE_HASHES,
    )
    assert_strict_invariants(
        run2_packets,
        expected_event_order=EVENT_SEQUENCE,
        expected_salience=EXPECTED_SALIENCE,
        expected_provenance_hashes=EXPECTED_PROVENANCE_HASHES,
    )
    assert_numeric_diagnostics_policy([run1_packets, run2_packets])


def test_salience_packet_hashes_are_deterministic_per_event():
    run1_hashes = [packet["PROVENANCE_HASH"] for packet in _run_event_sequence()]
    run2_hashes = [packet["PROVENANCE_HASH"] for packet in _run_event_sequence()]

    assert run1_hashes == EXPECTED_PROVENANCE_HASHES
    assert run2_hashes == EXPECTED_PROVENANCE_HASHES
