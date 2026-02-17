from __future__ import annotations

from typing import Dict, List, Sequence, Tuple


class MemoryStore:
    """Storage interface for active memories managed by the decay engine."""

    def add(self, record):
        raise NotImplementedError

    def get(self, record_id: str):
        raise NotImplementedError

    def sweep(self, current_tau: float):
        raise NotImplementedError

    def touch(self, record_id: str, current_tau: float, cooldown: float = 0.0):
        raise NotImplementedError


class DecayMemoryStore(MemoryStore):
    """In-memory store backed by a retained-record index for pruning sweeps."""

    def __init__(self, calculate_strength, prune_threshold: float):
        self._calculate_strength = calculate_strength
        self.prune_threshold = prune_threshold
        self._records_by_id: Dict[str, object] = {}
        self._active_order: List[str] = []

    @property
    def records(self) -> Sequence[object]:
        return [self._records_by_id[record_id] for record_id in self._active_order]

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
