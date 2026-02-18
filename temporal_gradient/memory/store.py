from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Sequence, Tuple


class MemoryStore(ABC):
    @abstractmethod
    def add(self, record):
        pass

    @abstractmethod
    def get(self, record_id: str):
        pass

    @abstractmethod
    def sweep(self, current_tau: float):
        pass

    @abstractmethod
    def touch(self, record_id: str, current_tau: float, cooldown: float = 0.0):
        pass


class DecayMemoryStore(MemoryStore):
    def __init__(self, calculate_strength: Callable[[object, float], float], prune_threshold: float, s_max: float = 1.5):
        self._calculate_strength = calculate_strength
        self.prune_threshold = prune_threshold
        self.s_max = s_max
        self._records_by_id: Dict[str, object] = {}
        self._last_tau_by_id: Dict[str, float] = {}
        self._active_order: List[str] = []

    @property
    def records(self) -> Sequence[object]:
        return [self._records_by_id[record_id] for record_id in self._active_order]

    @property
    def active_ids(self) -> Tuple[str, ...]:
        return tuple(self._active_order)

    def _validate_record(self, record, *, allow_tau_regression: bool = False) -> None:
        strength = getattr(record, "strength", None)
        if strength is not None and not (0.0 <= strength <= self.s_max):
            raise ValueError(f"strength must be within [0.0, {self.s_max}]")

        new_tau = getattr(record, "last_accessed_tau", None)
        prev_tau = self._last_tau_by_id.get(record.id)
        if not allow_tau_regression and prev_tau is not None and new_tau is not None and new_tau < prev_tau:
            raise ValueError("last_tau cannot regress for existing record")

    def _should_prune(self, current_strength: float) -> bool:
        return current_strength <= self.prune_threshold

    def upsert(self, record, *, allow_tau_regression: bool = False):
        self._validate_record(record, allow_tau_regression=allow_tau_regression)
        self._records_by_id[record.id] = record
        if getattr(record, "last_accessed_tau", None) is not None:
            self._last_tau_by_id[record.id] = record.last_accessed_tau
        if record.id not in self._active_order:
            self._active_order.append(record.id)

    def add(self, record):
        self.upsert(record, allow_tau_regression=True)

    def get(self, record_id: str):
        return self._records_by_id.get(record_id)

    def sweep(self, current_tau: float) -> Tuple[List[Tuple[object, float]], List[object]]:
        survivors: List[Tuple[object, float]] = []
        forgotten: List[object] = []
        retained_ids: List[str] = []

        for record_id in self._active_order:
            record = self._records_by_id[record_id]
            current_val = self._calculate_strength(record, current_tau)
            if self._should_prune(current_val):
                forgotten.append(record)
            else:
                survivors.append((record, current_val))
                retained_ids.append(record_id)

        for record in forgotten:
            self._records_by_id.pop(record.id, None)
            self._last_tau_by_id.pop(record.id, None)

        self._active_order = retained_ids
        return survivors, forgotten

    def touch(self, record_id: str, current_tau: float, cooldown: float = 0.0):
        record = self.get(record_id)
        if record is None:
            return None
        updated_strength = record.reconsolidate(current_tau=current_tau, cooldown=cooldown)
        self._last_tau_by_id[record_id] = record.last_accessed_tau
        return updated_strength
