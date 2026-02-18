from temporal_gradient.salience.pipeline import CodexNoveltyAdapter, CodexValueAdapter


class _FakeCodex:
    def __init__(self, version: object = "v-test") -> None:
        self.version = version

    def score_H(self, text: str):
        return 0.25, {"H_model": 0.25}

    def score_V(self, text: str):
        return 0.75, {"V_model": 0.75}


class _FakeCodexNoVersion:
    def score_H(self, text: str):
        return 0.1, {"H_model": 0.1}

    def score_V(self, text: str):
        return 0.2, {"V_model": 0.2}


def test_codex_novelty_adapter_returns_deterministic_provenance_strings():
    score, diagnostics, provenance = CodexNoveltyAdapter(_FakeCodex(version=123)).score("input")

    assert score == 0.25
    assert diagnostics == {"H_model": 0.25}
    assert provenance == {
        "method": "codex_novelty",
        "codex_version": "123",
        "adapter_class": "CodexNoveltyAdapter",
    }
    assert all(isinstance(value, str) for value in provenance.values())


def test_codex_value_adapter_returns_unknown_version_when_missing():
    score, diagnostics, provenance = CodexValueAdapter(_FakeCodexNoVersion()).score("input")

    assert score == 0.2
    assert diagnostics == {"V_model": 0.2}
    assert provenance == {
        "method": "codex_value",
        "codex_version": "unknown",
        "adapter_class": "CodexValueAdapter",
    }
    assert all(isinstance(value, str) for value in provenance.values())
