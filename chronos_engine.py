import time
import math
import textwrap

class ClockRateModulator:
    """
    Clock-rate reparameterization for the internal time accumulator (τ).

    Principles:
    1. Clock-rate is modulated by salience load (surprise × value).
    2. Higher salience load slows the internal accumulator; lower load keeps it near the baseline rate.
    3. A floor on the clock-rate prevents τ from stalling.
    """
    
    def __init__(self, base_dilation_factor=1.0, min_clock_rate=0.05):
        self.start_wall_time = time.time()
        self.subjective_age = 0.0
        self.base_dilation = base_dilation_factor
        self.min_clock_rate = min_clock_rate
        self.last_tick = self.start_wall_time
        
        # Telemetry history for debugging/visualizing
        self.chronolog = []

    def clock_rate_from_psi(self, psi):
        """
        Maps salience load (Ψ) to a clock-rate with a minimum floor.
        """
        scaled_psi = max(0.0, psi) * self.base_dilation
        return max(self.min_clock_rate, 1 / (1 + scaled_psi))

    def calculate_information_density(self, input_data):
        """
        Calculates the 'Mass' of the current moment.
        In a real LLM context, this would be Token Count + Semantic Complexity.
        For this demo, we use raw length and entropy approximation.
        """
        if not input_data:
            return 0.0
            
        # 1. Raw Mass (Length)
        mass = len(input_data)
        
        # 2. Entropy (Complexity) - simplistic Shannon approximation
        prob = [float(input_data.count(c)) / len(input_data) for c in dict.fromkeys(list(input_data))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        
        # The Density Metric: High Entropy + High Mass = High Density
        density = mass * entropy
        return density

    def tick(self, psi, input_context=None):
        """
        Advances time. 
        ψ is the salience load; we reparameterize the clock-rate from it.
        """
        current_wall_time = time.time()
        wall_delta = current_wall_time - self.last_tick
        
        # Clock-rate reparameterization
        # If Ψ is 0, internal time matches wall clock (factor 1.0).
        # As Ψ increases, internal time slows with a minimum floor.
        clock_rate = self.clock_rate_from_psi(psi)
        
        # Calculate tau Delta
        subjective_delta = wall_delta * clock_rate
        self.subjective_age += subjective_delta

        density = None
        if input_context is not None:
            density = self.calculate_information_density(input_context)
        
        # Log the state
        telemetry = {
            "wall_delta": round(wall_delta, 4),
            "tau": round(self.subjective_age, 4),
            "psi": round(psi, 4),
            "clock_rate": round(clock_rate, 4),
            "d_tau": round(subjective_delta, 4)
        }
        if density is not None:
            telemetry["diagnostic_density"] = round(density, 2)
        self.chronolog.append(telemetry)
        
        self.last_tick = current_wall_time
        
        return subjective_delta

# --- SIMULATION ---

if __name__ == "__main__":
    agent_clock = ClockRateModulator()
    
    print(f"{'EVENT':<20} | {'WALL TIME':<10} | {'INTERNAL τ':<10} | {'CLOCK RATE'}")
    print("-" * 60)

    simulated_events = [
        "",                                      # The Void (No data)
        "Hello.",                                # Simple greeting (Low Mass)
        "The quick brown fox jumps over the dog",# Standard sentence (Medium Mass)
        # High Mass / High Entropy (The "Filament")
        textwrap.dedent("""
            Time is a field gradient formed by memory + change. 
            Entropy’s arrow is not time itself, but an emergent 
            direction from memory accumulation.
        """) * 5 
    ]

    for event in simulated_events:
        # Simulate processing time (Wall Clock moves forward)
        time.sleep(1.0) 
        
        psi = min(4.0, len(event) / 20) if event else 0.0

        # The Agent "Experiences" the event
        d_tau = agent_clock.tick(psi, input_context=event)
        
        label = (event[:15] + '...') if len(event) > 15 else (event if event else "[EMPTY INPUT]")
        
        print(f"{label:<20} | {1.0:<10} | {round(agent_clock.subjective_age, 4):<10} | {round(agent_clock.clock_rate_from_psi(psi), 2)}x")

    print("-" * 60)
    print("OBSERVATION:")
    print("In the empty input, 1 wall second ≈ 1 internal second (baseline rate).")
    print("During the high-load event, internal time advances more slowly (reduced clock rate).")
  
