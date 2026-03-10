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


def decay_strength(strength: float, elapsed_tau: float, half_life: float | None = None, decay_lambda: float | None = None) -> float:
    if elapsed_tau < 0.0:
        elapsed_tau = 0.0

    if decay_lambda is not None:
        decayed_value = strength * math.exp(-decay_lambda * elapsed_tau)
    elif half_life is not None:
        decayed_value = strength * (0.5 ** (elapsed_tau / half_life))
    else:
        raise ValueError("either half_life or decay_lambda must be provided")
    return max(0.0, decayed_value)


class EntropicMemory:
    def __init__(self, content, initial_weight=1.0, tags=None, s_max: float = S_MAX):
        self.id = str(uuid.uuid4())[:8]
        self.content = content
        self.tags = tags or []
        self.strength = initial_weight
        self.s_max = s_max
        self.created_at_tau = 0.0
        self.last_accessed_tau = 0.0
        self.access_count = 1

    def reconsolidate(self, current_tau, cooldown=0.0):
        elapsed = current_tau - self.last_accessed_tau
        self.last_accessed_tau = current_tau
        self.access_count += 1

        if elapsed >= cooldown:
            boost = max(0.02, 0.1 / self.access_count)
            self.strength = min(self.s_max, self.strength + boost)

        return self.strength


class DecayEngine:
    def __init__(self, half_life=50.0, prune_threshold=0.2, decay_lambda: float | None = None, s_max: float = S_MAX):
        self.half_life = half_life
        self.decay_lambda = decay_lambda
        self.prune_threshold = prune_threshold
        self.s_max = s_max
        self.store = DecayMemoryStore(
            calculate_strength=self.calculate_current_strength,
            prune_threshold=prune_threshold,
            s_max=s_max,
        )

    @property
    def vault(self):
        return list(self.store.records)

    def add_memory(self, memory_obj, current_tau):
        memory_obj.created_at_tau = current_tau
        memory_obj.last_accessed_tau = current_tau
        if hasattr(memory_obj, "s_max"):
            memory_obj.s_max = self.s_max
        self.store.add(memory_obj)

    def get_memory(self, memory_id):
        return self.store.get(memory_id)

    def touch_memory(self, memory_id, current_tau, cooldown=0.0):
        return self.store.touch(memory_id, current_tau, cooldown=cooldown)

    def calculate_current_strength(self, memory, current_tau):
        elapsed = current_tau - memory.last_accessed_tau
        if elapsed < 0:
            elapsed = 0

        # Canonical first-order model from README: dS/dτ = -λS, so decay depends
        # on elapsed internal time τ only (not τ scaled by current strength).
        return decay_strength(
            memory.strength,
            elapsed,
            half_life=self.half_life,
            decay_lambda=self.decay_lambda,
        )

    def entropy_sweep(self, current_tau):
        survivors, forgotten = self.store.sweep(current_tau)
        return survivors, forgotten
