import temporal_gradient as tg
import temporal_gradient.contracts as c


def test_top_level_exports_are_present():
    for attr in ("clock", "memory", "salience", "telemetry", "load_config"):
        assert hasattr(tg, attr)


def test_package_version_is_0_2_0():
    assert tg.__version__ == "0.2.0"


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
