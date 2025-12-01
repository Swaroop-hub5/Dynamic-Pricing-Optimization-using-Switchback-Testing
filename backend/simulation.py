import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta

class MarketplaceSimulator:
    def __init__(self):
        self.start_date = datetime.now() - timedelta(days=14)
        self.window_size_minutes = 30 # Switchback window size
    
    def generate_switchback_schedule(self, days=14):
        """
        Creates a schedule alternating between Control and Treatment
        in 30-minute windows (common in ride-hailing).
        """
        timestamps = pd.date_range(start=self.start_date, periods=days*24*2, freq=f'{self.window_size_minutes}min')
        schedule = pd.DataFrame({'window_start': timestamps})
        
        # Simple randomization: Randomly assign variants to windows
        schedule['variant'] = np.random.choice(['Control', 'Treatment'], size=len(schedule))
        return schedule

    def simulate_marketplace(self, uplift_factor=1.05):
        """
        Simulates requests, driver availability, and conversion.
        """
        schedule = self.generate_switchback_schedule()
        data = []

        # Simulation Parameters
        base_demand_per_window = 50  # Avg requests per 30 mins
        
        for _, row in schedule.iterrows():
            window_start = row['window_start']
            variant = row['variant']
            
            # Simulate variable demand (random noise + peak hour effect)
            is_peak = 17 <= window_start.hour <= 19
            actual_demand = int(np.random.normal(base_demand_per_window * (1.5 if is_peak else 1.0), 10))
            actual_demand = max(0, actual_demand)

            for _ in range(actual_demand):
                request_id = str(uuid.uuid4())[:8]
                
                # Pricing Logic Simulation
                base_price = np.random.uniform(5, 20)
                
                if variant == 'Treatment':
                    price = base_price * np.random.uniform(1.0, 1.2) # Surge
                    driver_acceptance_prob = 0.85 
                    user_conversion_prob = 0.70 
                else:
                    price = base_price
                    driver_acceptance_prob = 0.75
                    user_conversion_prob = 0.75 
                
                # Simulate Outcome
                # FIX: Explicitly convert numpy bools to python bools
                driver_found = bool(np.random.random() < driver_acceptance_prob)
                user_accepted = bool(np.random.random() < user_conversion_prob)
                
                # Ride is "Completed" only if both agree
                is_completed = bool(driver_found and user_accepted)
                
                data.append({
                    'timestamp': window_start + timedelta(minutes=np.random.randint(0, 30)),
                    'window_start': window_start,
                    'variant': variant,
                    'request_id': request_id,
                    'price_quoted': round(float(price), 2), # FIX: Convert to float
                    'driver_found': driver_found,
                    'user_accepted': user_accepted,
                    'is_completed': is_completed,
                    'order_value': round(float(price), 2) if is_completed else 0.0
                })
                
        return pd.DataFrame(data)