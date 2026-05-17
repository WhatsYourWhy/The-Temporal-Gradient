from importlib.metadata import version as _installed_version

import temporal_gradient as tg
import temporal_gradient.contracts as c


def test_top_level_exports_are_present():
    for attr in ("clock", "memory", "salience", "telemetry", "load_config"):
        assert hasattr(tg, attr)


def test_package_version_matches_pyproject():
    # Guards against pyproject.toml and __init__.py drifting apart on a release.
    assert tg.__version__ == _installed_version("temporal-gradient")


def test_contracts_all_contains_protocols():
    required = {
        "ClockTickRequest",
        "ClockTickResult",
        "MemoryDecaySnapshot",
        "MemoryEncodingDecision",
        "SalienceEvaluationRequest",
        "SalienceEvaluationResult",
        "TelemetryPacketContract",
    }
    assert required.issubset(set(c.__all__))


def test_policies_exports_include_canonical_cooldown_policy():
    assert hasattr(tg.policies, "ComputeCooldownPolicy")
    assert not hasattr(tg.policies, "ComputeBudgetPolicy")
