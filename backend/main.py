from fastapi import FastAPI
from .simulation import MarketplaceSimulator
from .analysis import analyze_experiment
import pandas as pd
import json

app = FastAPI()
simulator = MarketplaceSimulator()

@app.get("/")
def read_root():
    return {"status": "Bolt Experimentation API Active"}

@app.post("/run-simulation")
def run_simulation(days: int = 14):
    """Generates synthetic data and runs analysis"""
    
    # 1. Run Simulation
    df = simulator.simulate_marketplace()
    
    # 2. Analyze
    summary, window_metrics = analyze_experiment(df)
    
    # 3. Serialize for Frontend
    # Convert dates to strings for JSON serialization
    window_metrics['window_start'] = window_metrics['window_start'].dt.strftime('%Y-%m-%d %H:%M')
    
    return {
        "summary": summary,
        "window_metrics": window_metrics.to_dict(orient='records'),
        "raw_data_sample": df.head(5).to_dict(orient='records') # Just a peek
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)