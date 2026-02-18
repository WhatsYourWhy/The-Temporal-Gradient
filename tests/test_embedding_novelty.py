import pytest

from temporal_gradient.salience.embedding_novelty import DictEmbeddingCache, NoveltyScorer


def _make_scorer(*, cache_backend: DictEmbeddingCache, deterministic_mode: bool) -> NoveltyScorer:
    return NoveltyScorer(
        model_id="mini-embed",
        model_hash="sha256:abc123",
        window_size=2,
        quantization="int8",
        cache_backend=cache_backend,
        deterministic_mode=deterministic_mode,
        device="cpu",
        dtype="float32",
        runtime_metadata={"deterministic_runtime_policy": "cpu_fp32"},
        code_version="test-v1",
    )


def _populate_cache(scorer: NoveltyScorer, vectors_by_text: dict[str, tuple[float, ...]]) -> None:
    for text, vector in vectors_by_text.items():
        scorer.cache_backend.set(scorer._cache_key(text), vector)


def test_cache_hit_deterministic_replay_equality() -> None:
    vectors_by_text = {
        "alpha": (1.0, 0.0, 0.0),
        "beta": (0.0, 1.0, 0.0),
        "gamma": (1.0, 0.0, 0.0),
    }
    sequence = ["alpha", "beta", "gamma"]

    cache = DictEmbeddingCache()
    scorer1 = _make_scorer(cache_backend=cache, deterministic_mode=True)
    _populate_cache(scorer1, vectors_by_text)

    run1 = [scorer1.score(text) for text in sequence]

    scorer2 = _make_scorer(cache_backend=cache, deterministic_mode=True)
    run2 = [scorer2.score(text) for text in sequence]

    assert run1 == run2


def test_cache_miss_fails_in_deterministic_mode() -> None:
    scorer = _make_scorer(cache_backend=DictEmbeddingCache(), deterministic_mode=True)

    with pytest.raises(ValueError, match=r"cache_hit_only"):
        scorer.score("missing")


def test_deterministic_mode_fails_when_quantization_is_disabled() -> None:
    with pytest.raises(ValueError, match=r"\[quantization\]"):
        NoveltyScorer(
            model_id="mini-embed",
            model_hash="sha256:abc123",
            window_size=2,
            quantization="none",
            cache_backend=DictEmbeddingCache(),
            deterministic_mode=True,
            device="cpu",
            dtype="float32",
            runtime_metadata={"deterministic_runtime_policy": "cpu_fp32"},
        )


def test_deterministic_mode_fails_with_incompatible_runtime_metadata() -> None:
    with pytest.raises(ValueError, match=r"\[runtime_metadata\]"):
        NoveltyScorer(
            model_id="mini-embed",
            model_hash="sha256:abc123",
            window_size=2,
            quantization="int8",
            cache_backend=DictEmbeddingCache(),
            deterministic_mode=True,
            device="cuda",
            dtype="float16",
            runtime_metadata={
                "deterministic_runtime_policy": "gpu_fp16",
                "execution_device": "cuda",
                "compute_dtype": "float16",
            },
        )


def test_provenance_contains_required_keys() -> None:
    cache = DictEmbeddingCache()
    scorer = _make_scorer(cache_backend=cache, deterministic_mode=True)
    text = "alpha"
    cache.set(scorer._cache_key(text), (1.0, 0.0, 0.0))

    _, _, provenance = scorer.score(text)

    assert provenance["novelty_method"] == "embedding_max_cosine_window"
    assert provenance["model_id"] == "mini-embed"
    assert provenance["model_hash"] == "sha256:abc123"
    assert provenance["device"] == "cpu"
    assert provenance["dtype"] == "float32"
    assert provenance["window_size"] == "2"
    assert provenance["quantization"] == "int8"
    assert provenance["cache"] == "hit"
    assert provenance["deterministic"] == "true"
    assert provenance["code_version"] == "test-v1"


def test_operational_provenance_contains_required_keys() -> None:
    cache = DictEmbeddingCache()
    scorer = _make_scorer(cache_backend=cache, deterministic_mode=False)
    text = "alpha"
    cache.set(scorer._cache_key(text), (1.0, 0.0, 0.0))

    _, _, provenance = scorer.score(text)

    assert provenance["deterministic"] == "false"
    assert provenance["reason"] == "live_embedding_compute"
    assert provenance["model_runtime"] == "cpu_fp32"
    assert provenance["model_id"] == "mini-embed"
    assert provenance["model_hash"] == "sha256:abc123"
    assert provenance["tokenizer_id"] == "mini-embed"
    assert provenance["tokenizer_hash"] == "sha256:abc123"
    assert provenance["tokenizer_version"] == "test-v1"
    assert provenance["code_version"] == "test-v1"


@pytest.mark.parametrize(
    "missing_key",
    [
        "deterministic",
        "reason",
        "model_runtime",
        "model_id",
        "model_hash",
        "tokenizer_id",
        "tokenizer_hash",
        "tokenizer_version",
        "code_version",
    ],
)
def test_operational_provenance_validation_fails_when_required_key_missing(missing_key: str) -> None:
    cache = DictEmbeddingCache()
    scorer = _make_scorer(cache_backend=cache, deterministic_mode=False)
    text = "alpha"
    cache.set(scorer._cache_key(text), (1.0, 0.0, 0.0))

    original_provenance = scorer._provenance

    def _broken_provenance(*, cache: str, deterministic: str, reason: str | None = None) -> dict[str, str]:
        provenance = original_provenance(cache=cache, deterministic=deterministic, reason=reason)
        provenance.pop(missing_key)
        return provenance

    scorer._provenance = _broken_provenance  # type: ignore[method-assign]

    with pytest.raises(ValueError, match=r"required_keys"):
        scorer.score(text)


def test_operational_provenance_validation_fails_for_wrong_reason() -> None:
    cache = DictEmbeddingCache()
    scorer = _make_scorer(cache_backend=cache, deterministic_mode=False)
    text = "alpha"
    cache.set(scorer._cache_key(text), (1.0, 0.0, 0.0))

    original_provenance = scorer._provenance

    def _broken_provenance(*, cache: str, deterministic: str, reason: str | None = None) -> dict[str, str]:
        provenance = original_provenance(cache=cache, deterministic=deterministic, reason=reason)
        provenance["reason"] = "wrong_reason"
        return provenance

    scorer._provenance = _broken_provenance  # type: ignore[method-assign]

    with pytest.raises(ValueError, match=r"\[reason\]"):
        scorer.score(text)
