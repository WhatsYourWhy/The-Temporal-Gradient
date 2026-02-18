from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline


def _pipeline():
    return SaliencePipeline(RollingJaccardNovelty(window_size=3), KeywordImperativeValue())


def test_pipeline_is_deterministic_for_identical_input_sequence():
    events = ["critical update", "normal", "critical update"]
    p1 = _pipeline()
    p2 = _pipeline()
    out1 = [p1.evaluate(e).psi for e in events]
    out2 = [p2.evaluate(e).psi for e in events]
    assert out1 == out2


def test_pipeline_replay_with_reset_matches_first_run():
    events = ["critical update", "normal", "critical update"]
    pipeline = _pipeline()

    first_run = [pipeline.evaluate(e).psi for e in events]
    pipeline.reset()
    replay_run = [pipeline.evaluate(e).psi for e in events]

    assert replay_run == first_run


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
