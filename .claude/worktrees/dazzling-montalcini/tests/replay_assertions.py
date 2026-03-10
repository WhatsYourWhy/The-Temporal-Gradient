from __future__ import annotations

from math import isclose
from typing import Iterable, Mapping, Sequence


def _validate_unstable_metric_allowlist(allowed_unstable_metrics: Mapping[str, str]) -> None:
    for key, rationale in allowed_unstable_metrics.items():
        assert isinstance(key, str) and key.strip(), "unstable metric key must be a non-empty string"
        assert isinstance(rationale, str) and rationale.strip(), (
            f"unstable metric '{key}' requires a non-empty rationale"
        )


def assert_strict_invariants(
    packets: Sequence[Mapping[str, object]],
    *,
    expected_event_order: Sequence[str],
    expected_salience: Sequence[float],
    expected_provenance_hashes: Sequence[str],
) -> None:
    """Assert hard replay invariants that must match exactly."""

    assert [packet["event_text"] for packet in packets] == list(expected_event_order)
    assert [packet["SALIENCE"] for packet in packets] == list(expected_salience)
    assert [packet["PROVENANCE_HASH"] for packet in packets] == list(expected_provenance_hashes)


def assert_numeric_diagnostics_policy(
    runs: Sequence[Sequence[Mapping[str, object]]],
    *,
    tolerance_keys: Iterable[str] = (),
    abs_tol: float = 1e-9,
    rel_tol: float = 1e-9,
    allowed_unstable_metrics: Mapping[str, str] | None = None,
) -> None:
    """Validate numeric diagnostics policy across replay runs.

    Policy:
    - deterministic diagnostics must match exactly,
    - explicit tolerance keys may use numeric tolerance,
    - unstable diagnostics are allowed only for explicitly allowlisted metrics
      that include a per-test rationale.
    """

    assert runs, "at least one run is required"
    baseline = runs[0]
    tolerance_key_set = set(tolerance_keys)
    unstable_metric_allowlist = dict(allowed_unstable_metrics or {})
    _validate_unstable_metric_allowlist(unstable_metric_allowlist)

    for candidate in runs[1:]:
        assert len(candidate) == len(baseline)
        for baseline_packet, candidate_packet in zip(baseline, candidate):
            baseline_diag = baseline_packet["diagnostics"]
            candidate_diag = candidate_packet["diagnostics"]
            assert isinstance(baseline_diag, Mapping)
            assert isinstance(candidate_diag, Mapping)

            baseline_keys = set(baseline_diag.keys())
            candidate_keys = set(candidate_diag.keys())
            assert baseline_keys == candidate_keys

            for key in baseline_keys:
                baseline_val = baseline_diag[key]
                candidate_val = candidate_diag[key]
                assert isinstance(baseline_val, float)
                assert isinstance(candidate_val, float)
                if key in unstable_metric_allowlist:
                    continue
                if key in tolerance_key_set:
                    assert isclose(candidate_val, baseline_val, rel_tol=rel_tol, abs_tol=abs_tol)
                else:
                    assert candidate_val == baseline_val, (
                        f"diagnostics metric '{key}' drifted across replays; "
                        "add it to allowed_unstable_metrics with a rationale if instability is expected"
                    )
