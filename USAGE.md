# How to Read the Logs
The `temporal-gradient-architecture` does not output standard debug text. It outputs **Subjective Experience Metrics**.

When you run `experiments/simulation_run.py`, you will see a table like this. Here is how to interpret the physics.

## 1. The Time Dilation Table
This measures how the Agent experiences time relative to the complexity of the input.

```text
WALL T   | SUBJ T   | INPUT                               | VAL  | DILATION
=====================================================================================
1.0      | 0.15     | "CRITICAL: SECURITY BREACH..."      | 1.5  | 0.15x
2.0      | 1.15     | "Checking local weather..."         | 0.4  | 1.00x

Key Metrics:
 * WALL T (Wall Time): The actual time passed in the real world (seconds).
 * SUBJ T (Subjective Time): The age of the Agent.
   * Notice: In the first row, 1 second passed for us, but the Agent only aged 0.15 seconds.
   * Why? The input was "CRITICAL" (High Entropy/Mass). The Wiltshire Clock slowed down subjective time to allow for deep processing. The Agent is in a "Bullet Time" state.
 * VAL (Valuation): The "Codex" score.
   * 1.5 = High Priority (Trauma/Core Memory).
   * 0.4 = Low Priority (Noise).
 * DILATION: The multiplier.
   * 1.00x = Real-time (The Void).
   * < 1.00x = Deep Focus (Time Slows).
2. The Entropy Sweep (Memory Audit)
At the end of the simulation, the system runs the Entropic Decay function to see what survived.
>>> MEMORY AUDIT (Post-Simulation)
[ALIVE] Strength: 1.42 | Content: "My name is Sentinel."
[DEAD ] Content: "Rain. Water. Liquid."

The Logic:
 * ALIVE: This memory had a high initial Valuation (1.5) or was "Reconsolidated" (accessed frequently). It remains in the Agent's context window.
 * DEAD: This memory was low valuation (0.3) and was eaten by the entropy function. The Agent has effectively "forgotten" this noise to save energy.
3. Configuration
You can tweak the physics of the universe in simulation_run.py:
# The "Gravity" of the universe. 
# Higher = Time slows down more aggressively during complex tasks.
clock = WiltshireClock(base_dilation_factor=1.5)

# The "Rot Rate" of memory.
# Lower = Memories die faster.
decay = DecayEngine(half_life=10.0) 




