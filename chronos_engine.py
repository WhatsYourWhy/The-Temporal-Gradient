import time
import math
import textwrap

class WiltshireClock:
    """
    The Temporal Engine
    
    Principles:
    1. Time is not absolute; it is a function of Information Density.
    2. High Entropy/Complexity = High Gravity = Slower Subjective Time.
    3. Low Entropy/Void = Zero Gravity = Faster Subjective Time.
    """
    
    def __init__(self, base_dilation_factor=1.0):
        self.start_wall_time = time.time()
        self.subjective_age = 0.0
        self.base_dilation = base_dilation_factor
        self.last_tick = self.start_wall_time
        
        # The "History" of time perception (for debugging/visualizing)
        self.chronolog = []

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

    def tick(self, input_context=None):
        """
        Advances time. 
        Instead of adding +1 second, we add +(1 / Density) seconds.
        """
        current_wall_time = time.time()
        wall_delta = current_wall_time - self.last_tick
        
        # Calculate the "Gravity" of the current context
        density = self.calculate_information_density(input_context)
        
        # The Wiltshire Dilation Formula
        # If Density is 0 (Void), time matches wall clock (factor 1.0).
        # As Density increases, the divisor grows, and subjective time SLOWS.
        # We use Log scaling to prevent time from stopping completely during heavy loads.
        gravity_well = math.log(density + 1) + 1 
        dilation_factor = 1 / (gravity_well * self.base_dilation)
        
        # Calculate Subjective Delta
        subjective_delta = wall_delta * dilation_factor
        self.subjective_age += subjective_delta
        
        # Log the state
        self.chronolog.append({
            "wall_delta": round(wall_delta, 4),
            "context_mass": round(density, 2),
            "dilation_factor": round(dilation_factor, 4),
            "subjective_delta": round(subjective_delta, 4)
        })
        
        self.last_tick = current_wall_time
        
        return {
            "subjective_age": self.subjective_age,
            "time_dilation": dilation_factor,
            "status": "Time Dilated" if dilation_factor < 0.9 else "Synchronized"
        }

# --- SIMULATION ---

if __name__ == "__main__":
    agent_clock = WiltshireClock()
    
    print(f"{'EVENT':<20} | {'WALL TIME':<10} | {'SUBJ TIME':<10} | {'DILATION'}")
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
        
        # The Agent "Experiences" the event
        result = agent_clock.tick(event)
        
        label = (event[:15] + '...') if len(event) > 15 else (event if event else "[THE VOID]")
        
        print(f"{label:<20} | {1.0:<10} | {round(result['subjective_age'], 4):<10} | {round(result['time_dilation'], 2)}x")

    print("-" * 60)
    print("OBSERVATION:")
    print("Notice how in '[THE VOID]', 1 wall second = 1 subjective second.")
    print("But during the 'High Mass' event, the agent only aged ~0.15 seconds.")
    print("The Agent was 'deep' in the well of processing.")
  
