import pandas as pd
import numpy as np
from scipy import stats

def analyze_experiment(df):
    """
    Performs statistical analysis on Switchback data.
    """
    # 1. Safety Check: If dataframe is empty (e.g., simulation failed), return zeros
    if df.empty:
        return {
            "control_ocr": 0.0, "treatment_ocr": 0.0, "lift": 0.0,
            "p_value": 1.0, "is_significant": False,
            "total_rides": 0, "total_revenue": 0.0,
            "control_gmv": 0.0, "treatment_gmv": 0.0, # Safety defaults
            "control_requests": 0, "treatment_requests": 0
        }, pd.DataFrame()

    # 2. Aggregate metrics by Window (The Unit of Randomization)
    window_metrics = df.groupby(['window_start', 'variant']).agg({
        'request_id': 'count',
        'is_completed': 'sum',
        'order_value': 'sum'
    }).reset_index()
    
    # Calculate Ratios per window
    window_metrics['ocr'] = window_metrics['is_completed'] / window_metrics['request_id']
    window_metrics['avg_gmv'] = window_metrics['order_value'] / window_metrics['request_id']
    
    # 3. Separate Groups
    control_windows = window_metrics[window_metrics['variant'] == 'Control']
    treatment_windows = window_metrics[window_metrics['variant'] == 'Treatment']
    
    # 4. Statistical Test (Welch's t-test on Window Means)
    # Handle cases where one group might be empty
    if len(control_windows) > 1 and len(treatment_windows) > 1:
        t_stat, p_value = stats.ttest_ind(
            treatment_windows['ocr'], 
            control_windows['ocr'], 
            equal_var=False
        )
    else:
        p_value = 1.0 # Not enough data

    # 5. Lift Calculation (Safe Division)
    ctrl_mean = control_windows['ocr'].mean()
    if ctrl_mean > 0:
        lift = (treatment_windows['ocr'].mean() - ctrl_mean) / ctrl_mean
    else:
        lift = 0.0

    # 6. Summary Results
    # We add 'control_gmv' and 'treatment_gmv' here so the Frontend doesn't crash
    results = {
        "control_ocr": float(ctrl_mean),
        "treatment_ocr": float(treatment_windows['ocr'].mean()),
        "lift": float(lift),
        "p_value": float(p_value),
        "is_significant": bool(p_value < 0.05),
        "total_rides": int(df['is_completed'].sum()),
        "total_revenue": float(df['order_value'].sum()),
        "sample_size_windows": int(len(window_metrics)),
        
        # --- NEW METRICS FOR FRONTEND ---
        "control_gmv": float(control_windows['order_value'].sum()),
        "treatment_gmv": float(treatment_windows['order_value'].sum()),
        "control_requests": int(control_windows['request_id'].sum()),
        "treatment_requests": int(treatment_windows['request_id'].sum())
    }
    
    return results, window_metrics