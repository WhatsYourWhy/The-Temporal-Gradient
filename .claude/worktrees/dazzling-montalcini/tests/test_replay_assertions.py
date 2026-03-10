import pytest

from tests.replay_assertions import assert_numeric_diagnostics_policy


def _packet_with_diagnostics(**diagnostics: float) -> dict[str, object]:
    return {"diagnostics": diagnostics}


def test_unknown_unstable_metric_drift_fails_without_allowlist():
    baseline = [_packet_with_diagnostics(H_model=0.25, stable_metric=1.0)]
    replay = [_packet_with_diagnostics(H_model=0.33, stable_metric=1.0)]

    with pytest.raises(AssertionError, match="H_model"):
        assert_numeric_diagnostics_policy([baseline, replay], allowed_unstable_metrics={})


def test_unknown_unstable_metric_drift_fails_when_not_whitelisted():
    baseline = [_packet_with_diagnostics(H_model=0.25, V_model=0.75)]
    replay = [_packet_with_diagnostics(H_model=0.25, V_model=0.6)]

    with pytest.raises(AssertionError, match="V_model"):
        assert_numeric_diagnostics_policy(
            [baseline, replay],
            allowed_unstable_metrics={"H_model": "LLM-side novelty estimate can vary by runtime"},
        )


def test_whitelisted_unstable_metric_with_rationale_is_allowed():
    baseline = [_packet_with_diagnostics(H_model=0.25, stable_metric=1.0)]
    replay = [_packet_with_diagnostics(H_model=0.33, stable_metric=1.0)]

    assert_numeric_diagnostics_policy(
        [baseline, replay],
        allowed_unstable_metrics={"H_model": "LLM-side novelty estimate can vary by runtime"},
    )


def test_allowlisted_unstable_metric_requires_rationale():
    baseline = [_packet_with_diagnostics(H_model=0.25)]
    replay = [_packet_with_diagnostics(H_model=0.33)]

    with pytest.raises(AssertionError, match="requires a non-empty rationale"):
        assert_numeric_diagnostics_policy([baseline, replay], allowed_unstable_metrics={"H_model": ""})
