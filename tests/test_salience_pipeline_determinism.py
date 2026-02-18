from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline
from temporal_gradient.salience.provenance import compute_provenance_hash

from tests.replay_assertions import assert_numeric_diagnostics_policy, assert_strict_invariants


EVENT_SEQUENCE = ["critical update", "normal", "critical update"]
EXPECTED_SALIENCE = [0.30000000000000004, 0.1, 0.0]
EXPECTED_PROVENANCE_HASHES = [
    "e469247de73fe402968e3f35feaf607f1aa08714a45be9a52d5797adc17a9c63",
    "64dba39e92daba622ec6b80c3849b6c0c70e7691d943e8757d95bed181b06803",
    "e469247de73fe402968e3f35feaf607f1aa08714a45be9a52d5797adc17a9c63",
]


def _pipeline():
    return SaliencePipeline(RollingJaccardNovelty(window_size=3), KeywordImperativeValue())


def _record_run(pipeline: SaliencePipeline, events: list[str]) -> list[dict[str, object]]:
    packets: list[dict[str, object]] = []
    for event in events:
        result = pipeline.evaluate(event)
        packets.append(
            {
                "event_text": event,
                "SALIENCE": result.psi,
                "PROVENANCE_HASH": compute_provenance_hash(result.provenance),
                "diagnostics": result.diagnostics,
            }
        )
    return packets


def test_pipeline_is_deterministic_for_identical_input_sequence():
    p1 = _pipeline()
    p2 = _pipeline()
    out1 = _record_run(p1, EVENT_SEQUENCE)
    out2 = _record_run(p2, EVENT_SEQUENCE)

    assert_strict_invariants(
        out1,
        expected_event_order=EVENT_SEQUENCE,
        expected_salience=EXPECTED_SALIENCE,
        expected_provenance_hashes=EXPECTED_PROVENANCE_HASHES,
    )
    assert_strict_invariants(
        out2,
        expected_event_order=EVENT_SEQUENCE,
        expected_salience=EXPECTED_SALIENCE,
        expected_provenance_hashes=EXPECTED_PROVENANCE_HASHES,
    )
    assert_numeric_diagnostics_policy([out1, out2])


def test_pipeline_replay_with_reset_matches_first_run():
    pipeline = _pipeline()

    first_run = _record_run(pipeline, EVENT_SEQUENCE)
    pipeline.reset()
    replay_run = _record_run(pipeline, EVENT_SEQUENCE)

    assert_strict_invariants(
        replay_run,
        expected_event_order=EVENT_SEQUENCE,
        expected_salience=EXPECTED_SALIENCE,
        expected_provenance_hashes=EXPECTED_PROVENANCE_HASHES,
    )
    assert_numeric_diagnostics_policy([first_run, replay_run])


def test_pipeline_reset_preserves_scorer_configuration():
    keywords = ("critical", "must", "stop")
    novelty = RollingJaccardNovelty(window_size=4)
    value = KeywordImperativeValue(keywords=keywords, base_value=0.15, hit_value=0.25)
    pipeline = SaliencePipeline(novelty, value)

    for event in ("critical update", "normal", "must stop now"):
        pipeline.evaluate(event)

    pipeline.reset()

    assert novelty.window_size == 4
    assert value.keywords == keywords
    assert value.base_value == 0.15
    assert value.hit_value == 0.25


def test_pipeline_handles_empty_input_with_zero_or_defined_bounds():
    result = _pipeline().evaluate("")
    assert 0.0 <= result.novelty <= 1.0
    assert 0.0 <= result.value <= 1.0
    assert 0.0 <= result.psi <= 1.0


def test_pipeline_handles_punctuation_only_input():
    result = _pipeline().evaluate("!!!???...")
    assert 0.0 <= result.novelty <= 1.0
    assert 0.0 <= result.value <= 1.0
    assert 0.0 <= result.psi <= 1.0


def test_pipeline_outputs_are_bounded_between_zero_and_one():
    p = _pipeline()
    for text in ["critical", "", ".....", "normal text"]:
        result = p.evaluate(text)
        assert 0.0 <= result.novelty <= 1.0
        assert 0.0 <= result.value <= 1.0
        assert 0.0 <= result.psi <= 1.0
