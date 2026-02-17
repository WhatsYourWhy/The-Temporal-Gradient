from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Sequence, Tuple


class MemoryStore(ABC):
    """Storage interface for active memories managed by the decay engine."""

    @abstractmethod
    def add(self, record):
        """Insert a record into active storage."""

    @abstractmethod
    def get(self, record_id: str):
        """Fetch a record by id from active storage."""

    @abstractmethod
    def sweep(self, current_tau: float):
        """Apply pruning and return diagnostics for survivors and forgotten memories."""

    @abstractmethod
    def touch(self, record_id: str, current_tau: float, cooldown: float = 0.0):
        """Reconsolidate a record through the store API."""


class DecayMemoryStore(MemoryStore):
    """In-memory store backed by a retained-record index for pruning sweeps."""

    def __init__(self, calculate_strength: Callable[[object, float], float], prune_threshold: float):
        self._calculate_strength = calculate_strength
        self.prune_threshold = prune_threshold
        self._records_by_id: Dict[str, object] = {}
        self._active_order: List[str] = []

    @property
    def records(self) -> Sequence[object]:
        return [self._records_by_id[record_id] for record_id in self._active_order]

    @property
    def active_ids(self) -> Tuple[str, ...]:
        """Current retained memory ids in deterministic insertion order."""
        return tuple(self._active_order)

    def add(self, record):
        self._records_by_id[record.id] = record
        if record.id not in self._active_order:
            self._active_order.append(record.id)

    def get(self, record_id: str):
        return self._records_by_id.get(record_id)

    def sweep(self, current_tau: float) -> Tuple[List[Tuple[object, float]], List[object]]:
        survivors: List[Tuple[object, float]] = []
        forgotten: List[object] = []
        retained_ids: List[str] = []

        for record_id in self._active_order:
            record = self._records_by_id[record_id]
            current_val = self._calculate_strength(record, current_tau)
            if current_val > self.prune_threshold:
                survivors.append((record, current_val))
                retained_ids.append(record_id)
            else:
                forgotten.append(record)

        for record in forgotten:
            self._records_by_id.pop(record.id, None)

        self._active_order = retained_ids
        return survivors, forgotten

    def touch(self, record_id: str, current_tau: float, cooldown: float = 0.0):
        record = self.get(record_id)
        if record is None:
            return None
        return record.reconsolidate(current_tau=current_tau, cooldown=cooldown)
