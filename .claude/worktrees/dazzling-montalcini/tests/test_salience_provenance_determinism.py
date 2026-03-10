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
    "778c43f286a10c81e910e3fcc3e6798baea3b9acea34a66cac0850ee47b59549",
    "12ae7c9f0830c4e6b5960cca50d96c87db7e9d130ab317ed4e05ea02cf538746",
    "778c43f286a10c81e910e3fcc3e6798baea3b9acea34a66cac0850ee47b59549",
    "0dcf80351ba637be222be9ba84e93582a00fb807d3a07c126ca5ede347589bab",
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
    assert_numeric_diagnostics_policy([run1_packets, run2_packets], allowed_unstable_metrics={})


def test_salience_packet_hashes_are_deterministic_per_event():
    run1_hashes = [packet["PROVENANCE_HASH"] for packet in _run_event_sequence()]
    run2_hashes = [packet["PROVENANCE_HASH"] for packet in _run_event_sequence()]

    assert run1_hashes == EXPECTED_PROVENANCE_HASHES
    assert run2_hashes == EXPECTED_PROVENANCE_HASHES
