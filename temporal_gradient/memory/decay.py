import math
import uuid

from .store import DecayMemoryStore

S_MAX = 1.5


def _clamp(value, min_value=0.0, max_value=1.0):
    return max(min_value, min(max_value, value))


def should_encode(psi, threshold=0.3):
    return psi >= threshold


def initial_strength_from_psi(psi, S_max=1.2):
    normalized = _clamp(psi, 0.0, 1.0)
    return normalized * S_max


def decay_strength(strength: float, elapsed_tau: float, half_life: float) -> float:
    if elapsed_tau < 0.0:
        elapsed_tau = 0.0
    decayed_value = strength * (0.5 ** (elapsed_tau / half_life))
    return max(0.0, decayed_value)


class EntropicMemory:
    def __init__(self, content, initial_weight=1.0, tags=None):
        self.id = str(uuid.uuid4())[:8]
        self.content = content
        self.tags = tags or []
        self.strength = initial_weight
        self.created_at_tau = 0.0
        self.last_accessed_tau = 0.0
        self.access_count = 1

    def reconsolidate(self, current_tau, cooldown=0.0):
        elapsed = current_tau - self.last_accessed_tau
        self.last_accessed_tau = current_tau
        self.access_count += 1

        if elapsed >= cooldown:
            boost = max(0.02, 0.1 / self.access_count)
            self.strength = min(S_MAX, self.strength + boost)

        return self.strength


class DecayEngine:
    def __init__(self, half_life=50.0, prune_threshold=0.2):
        self.half_life = half_life
        self.prune_threshold = prune_threshold
        self.store = DecayMemoryStore(
            calculate_strength=self.calculate_current_strength,
            prune_threshold=prune_threshold,
            s_max=S_MAX,
        )

    @property
    def vault(self):
        return list(self.store.records)

    def add_memory(self, memory_obj, current_tau):
        memory_obj.created_at_tau = current_tau
        memory_obj.last_accessed_tau = current_tau
        self.store.add(memory_obj)

    def get_memory(self, memory_id):
        return self.store.get(memory_id)

    def touch_memory(self, memory_id, current_tau, cooldown=0.0):
        return self.store.touch(memory_id, current_tau, cooldown=cooldown)

    def calculate_current_strength(self, memory, current_tau):
        elapsed = current_tau - memory.last_accessed_tau
        if elapsed < 0:
            elapsed = 0

        effective_strength = max(memory.strength, 1e-12)
        adjusted_elapsed = elapsed / effective_strength
        return decay_strength(memory.strength, adjusted_elapsed, self.half_life)

    def entropy_sweep(self, current_tau):
        survivors, forgotten = self.store.sweep(current_tau)
        return survivors, forgotten
