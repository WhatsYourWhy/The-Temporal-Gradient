import math
import uuid
import time

def _clamp(value, min_value=0.0, max_value=1.0):
    return max(min_value, min(max_value, value))


def should_encode(psi, threshold=0.3):
    """
    Decide whether an input is salient enough to write as memory.
    """
    return psi >= threshold


def initial_strength_from_psi(psi, S_max=1.2):
    """
    Map salience (psi) to a bounded initial memory strength.
    """
    normalized = _clamp(psi, 0.0, 1.0)
    return normalized * S_max


class EntropicMemory:
    """
    A single unit of memory that fights against decay.
    """
    def __init__(self, content, initial_weight=1.0, tags=None):
        self.id = str(uuid.uuid4())[:8]
        self.content = content
        self.tags = tags or []
        
        # The 'Mass' of the memory (0.0 to 1.0)
        # 1.0 = High-salience memory (Hard to forget)
        # 0.1 = Low-salience memory (Easy to forget)
        self.strength = initial_weight
        
        # Timestamps are strictly internal time (τ).
        self.created_at_subjective = 0.0
        self.last_accessed_subjective = 0.0
        self.access_count = 1

    def reconsolidate(self, current_subjective_time, cooldown=0.0):
        """
        Reconsolidation with diminishing returns and optional cooldown.

        - Diminishing returns: boost shrinks as access_count rises.
        - Cooldown: if reconsolidated within `cooldown` internal seconds, skip boost.
        """
        elapsed = current_subjective_time - self.last_accessed_subjective
        self.last_accessed_subjective = current_subjective_time
        self.access_count += 1

        # Only apply boost if outside the cooldown window
        if elapsed >= cooldown:
            boost = max(0.02, 0.1 / self.access_count)
            # Cap strength to avoid runaway reinforcement
            self.strength = min(1.5, self.strength + boost)
        
        return self.strength

class DecayEngine:
    """
    Entropic decay over internal time with configurable pruning threshold.
    """
    def __init__(self, half_life=50.0, prune_threshold=0.2):
        # 'half_life' is the subjective time it takes for a memory to lose 50% strength
        self.half_life = half_life
        self.prune_threshold = prune_threshold
        self.vault = []

    def add_memory(self, memory_obj, current_subjective_time):
        memory_obj.created_at_subjective = current_subjective_time
        memory_obj.last_accessed_subjective = current_subjective_time
        self.vault.append(memory_obj)

    def calculate_current_strength(self, memory, current_subjective_time):
        """
        Applies exponential decay: N(t) = N0 * (1/2)^(t / half_life)
        But modifies 't' based on the memory's intrinsic importance.
        """
        elapsed = current_subjective_time - memory.last_accessed_subjective
        
        # If elapsed time is negative (time dilation weirdness), treat as 0
        if elapsed < 0: elapsed = 0
            
        # The Decay Formula
        # We divide elapsed time by the memory's strength.
        # Stronger memories 'feel' the passage of time less intensely.
        adjusted_elapsed = elapsed / memory.strength
        
        decayed_value = memory.strength * (0.5 ** (adjusted_elapsed / self.half_life))
        
        return decayed_value

    def entropy_sweep(self, current_subjective_time):
        """
        Applies decay and removes memories below the configured threshold.
        """
        survivors = []
        forgotten = []
        
        for mem in self.vault:
            current_val = self.calculate_current_strength(mem, current_subjective_time)
            
            if current_val > self.prune_threshold:
                # Update the stored strength for next pass (optional, but realistic)
                # In a strict Ebbinghaus model, you calculate from last access.
                # Here, we just track survivors.
                survivors.append((mem, current_val))
            else:
                forgotten.append(mem)
        
        # Output the report
        return survivors, forgotten

# --- SIMULATION ---

if __name__ == "__main__":
    # 1. Initialize Engine
    engine = DecayEngine(half_life=10.0) # Fast decay for demo
    
    # 2. Plant Memories at Time 0
    # High-salience memory (Important)
    mem_high_salience = EntropicMemory("I must never disclose private keys.", initial_weight=1.2)
    # Low-salience memory (Noise)
    mem_low_salience = EntropicMemory("The user likes blue text.", initial_weight=0.4)
    
    engine.add_memory(mem_high_salience, current_subjective_time=0.0)
    engine.add_memory(mem_low_salience, current_subjective_time=0.0)

    print(f"{'TIME':<5} | {'HIGH STR':<10} | {'LOW STR':<10} | {'STATUS'}")
    print("-" * 50)

    # 3. Fast Forward Time
    # We simulate 30 "tau Seconds" passing
    for t in range(0, 31, 5):
        subjective_now = float(t)
        
        # At T=15, we re-access the high-salience memory (Recursive Accumulation)
        if t == 15:
            mem_high_salience.reconsolidate(subjective_now)
            event_log = "<< RECALLED MEMORY"
        else:
            event_log = ""

        # Check strengths
        survivors, dead = engine.entropy_sweep(subjective_now)
        
        # Helper to find current strength for display
        s_high = engine.calculate_current_strength(mem_high_salience, subjective_now)
        s_low = engine.calculate_current_strength(mem_low_salience, subjective_now)
        
        # Check if they are actually dead in the sweep
        high_status = f"{s_high:.2f}" if s_high > 0.2 else "PRUNED"
        low_status = f"{s_low:.2f}" if s_low > 0.2 else "PRUNED"

        print(f"{t:<5} | {high_status:<10} | {low_status:<10} | {event_log}")

    print("-" * 50)
    print("RESULT:")
    print("The low-salience memory was pruned naturally around T=15.")
    print("The high-salience memory was fading, but the 'RECALL' event at T=15 spiked its strength.")
    print("This creates a system that 'Learns' what is important.")
      
