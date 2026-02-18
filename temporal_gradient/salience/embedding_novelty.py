from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping, Optional, Protocol, Sequence, Tuple, runtime_checkable


@runtime_checkable
class EmbeddingCacheBackend(Protocol):
    def get(self, key: str) -> Optional[Sequence[float]]:
        ...

    def set(self, key: str, value: Sequence[float]) -> None:
        ...


class DictEmbeddingCache:
    """In-memory embedding cache backend."""

    def __init__(self, storage: MutableMapping[str, Sequence[float]] | None = None) -> None:
        self.storage = {} if storage is None else storage

    def get(self, key: str) -> Optional[Sequence[float]]:
        return self.storage.get(key)

    def set(self, key: str, value: Sequence[float]) -> None:
        self.storage[key] = tuple(float(item) for item in value)


class JsonDirectoryEmbeddingCache:
    """Filesystem cache that stores one embedding JSON file per cache key."""

    def __init__(self, cache_path: str | Path) -> None:
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)

    def _path_for_key(self, key: str) -> Path:
        return self.cache_path / f"{key}.json"

    def get(self, key: str) -> Optional[Sequence[float]]:
        path = self._path_for_key(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return tuple(float(item) for item in payload)

    def set(self, key: str, value: Sequence[float]) -> None:
        path = self._path_for_key(key)
        payload = [float(item) for item in value]
        path.write_text(json.dumps(payload), encoding="utf-8")


@dataclass(frozen=True)
class NoveltyScorerConfig:
    model_id: str
    model_hash: str
    window_size: int
    quantization: str
    deterministic_mode: bool = False
    cache_path: str | Path | None = None
    cache_backend: EmbeddingCacheBackend | None = None
    device: str = "cpu"
    dtype: str = "float32"
    runtime_metadata: Mapping[str, str] | None = None
    allow_nondeterministic_runtime: bool = False
    code_version: str | None = None


class NoveltyScorer:
    """Embedding novelty scorer using rolling max-cosine similarity."""

    def __init__(
        self,
        *,
        model_id: str,
        model_hash: str,
        window_size: int,
        quantization: str,
        cache_backend: EmbeddingCacheBackend | None = None,
        cache_path: str | Path | None = None,
        deterministic_mode: bool = False,
        device: str = "cpu",
        dtype: str = "float32",
        runtime_metadata: Mapping[str, str] | None = None,
        allow_nondeterministic_runtime: bool = False,
        code_version: str | None = None,
    ) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be > 0")

        self.model_id = model_id
        self.model_hash = model_hash
        self.window_size = window_size
        self.quantization = quantization
        self.deterministic_mode = deterministic_mode
        self.device = device
        self.dtype = dtype
        self.runtime_metadata = dict(runtime_metadata or {})
        self.allow_nondeterministic_runtime = allow_nondeterministic_runtime
        self.code_version = code_version
        self.novelty_method = "embedding_max_cosine_window"

        self._enforce_deterministic_invariants()

        if cache_backend is not None:
            self.cache_backend = cache_backend
        elif cache_path is not None:
            self.cache_backend = JsonDirectoryEmbeddingCache(cache_path)
        else:
            self.cache_backend = DictEmbeddingCache()

        self._history: List[Tuple[float, ...]] = []

    def _enforce_deterministic_invariants(self) -> None:
        if not self.deterministic_mode:
            return

        if self.quantization.strip().lower() == "none":
            raise ValueError(
                "Deterministic invariant failed [quantization]: deterministic_mode=True requires "
                "quantization to be enabled (anything except 'none'). "
                "Fix by configuring a deterministic quantization mode such as 'int8'."
            )

        if self.allow_nondeterministic_runtime:
            return

        policy = self.runtime_metadata.get("deterministic_runtime_policy", "").strip().lower()
        metadata_device = self.runtime_metadata.get("execution_device", "").strip().lower()
        metadata_dtype = self.runtime_metadata.get("compute_dtype", "").strip().lower()

        has_explicit_policy = policy == "cpu_fp32"
        has_cpu_fp32_metadata = metadata_device == "cpu" and metadata_dtype in {"float32", "fp32"}
        has_cpu_fp32_runtime = self.device.strip().lower() == "cpu" and self.dtype.strip().lower() in {
            "float32",
            "fp32",
        }

        if not (has_explicit_policy or has_cpu_fp32_metadata or has_cpu_fp32_runtime):
            raise ValueError(
                "Deterministic invariant failed [runtime_metadata]: deterministic_mode=True requires "
                "deterministic-safe runtime metadata (CPU + fp32) or explicit override. "
                "Fix by setting runtime_metadata={'deterministic_runtime_policy': 'cpu_fp32'} "
                "(or execution_device='cpu' and compute_dtype='float32'), or set "
                "allow_nondeterministic_runtime=True to override intentionally."
            )

    def reset(self) -> None:
        self._history.clear()

    def _cache_key(self, text: str) -> str:
        payload = {
            "text": text,
            "model_id": self.model_id,
            "model_hash": self.model_hash,
            "novelty_method": self.novelty_method,
            "window_size": self.window_size,
            "quantization": self.quantization,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return sha256(encoded).hexdigest()

    def _cosine_similarity(self, left: Sequence[float], right: Sequence[float]) -> float:
        if len(left) != len(right):
            raise ValueError("embedding dimension mismatch")
        dot = 0.0
        left_norm = 0.0
        right_norm = 0.0
        for left_item, right_item in zip(left, right):
            dot += left_item * right_item
            left_norm += left_item * left_item
            right_norm += right_item * right_item
        if left_norm == 0.0 or right_norm == 0.0:
            return 0.0
        return dot / ((left_norm ** 0.5) * (right_norm ** 0.5))

    def _provenance(self, *, cache: str, deterministic: str, reason: str | None = None) -> Dict[str, str]:
        provenance = {
            "novelty_method": self.novelty_method,
            "model_id": self.model_id,
            "model_hash": self.model_hash,
            "device": self.device,
            "dtype": self.dtype,
            "window_size": str(self.window_size),
            "quantization": self.quantization,
            "cache": cache,
            "deterministic": deterministic,
        }
        if self.code_version is not None:
            provenance["code_version"] = self.code_version
        if reason is not None:
            provenance["reason"] = reason
        return provenance

    def score(self, text: str) -> Tuple[float, Dict[str, float], Dict[str, str]]:
        key = self._cache_key(text)
        cached_embedding = self.cache_backend.get(key)

        if cached_embedding is None:
            if self.deterministic_mode:
                raise ValueError(
                    "Deterministic invariant failed [cache_hit_only]: deterministic_mode=True requires "
                    "precomputed embeddings in cache for every input. "
                    f"Missing cache entry for text={text!r}. "
                    "Fix by precomputing and storing embeddings before deterministic replay."
                )
            raise NotImplementedError(
                "Operational mode cache miss: live embedding compute path is not implemented yet."
            )

        embedding = tuple(float(value) for value in cached_embedding)
        max_similarity = 0.0
        for past_embedding in self._history:
            similarity = self._cosine_similarity(embedding, past_embedding)
            if similarity > max_similarity:
                max_similarity = similarity

        novelty = max(0.0, min(1.0, 1.0 - max_similarity))
        self._history.append(embedding)
        if len(self._history) > self.window_size:
            self._history = self._history[-self.window_size :]

        diagnostics = {
            "H_max_cosine_similarity": max_similarity,
            "H_history": float(len(self._history)),
        }

        if self.deterministic_mode:
            provenance = self._provenance(cache="hit", deterministic="true")
        else:
            provenance = self._provenance(
                cache="hit",
                deterministic="false",
                reason="operational_mode_cache_hit",
            )

        return novelty, diagnostics, provenance
