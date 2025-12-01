import pandas as pd
import numpy as np
from scipy import stats

def analyze_experiment(df):
    """
    Performs statistical analysis on Switchback data.
    """
    # 1. Aggregate metrics by Window (The Unit of Randomization)
    window_metrics = df.groupby(['window_start', 'variant']).agg({
        'request_id': 'count',
        'is_completed': 'sum',
        'order_value': 'sum'
    }).reset_index()
    
    # Calculate Ratios per window
    window_metrics['ocr'] = window_metrics['is_completed'] / window_metrics['request_id']
    window_metrics['avg_gmv'] = window_metrics['order_value'] / window_metrics['request_id']
    
    # 2. Separate Groups
    control_windows = window_metrics[window_metrics['variant'] == 'Control']
    treatment_windows = window_metrics[window_metrics['variant'] == 'Treatment']
    
    # 3. Statistical Test (Welch's t-test on Window Means)
    t_stat, p_value = stats.ttest_ind(
        treatment_windows['ocr'], 
        control_windows['ocr'], 
        equal_var=False
    )
    
    # 4. Summary Results - FIX: Explicit type conversions for JSON serialization
    results = {
        "control_ocr": float(control_windows['ocr'].mean()),
        "treatment_ocr": float(treatment_windows['ocr'].mean()),
        "lift": float((treatment_windows['ocr'].mean() - control_windows['ocr'].mean()) / control_windows['ocr'].mean()),
        "p_value": float(p_value),
        "is_significant": bool(p_value < 0.05), # FIX: Convert numpy bool to python bool
        "total_rides": int(df['is_completed'].sum()), # FIX: Convert numpy int to python int
        "total_revenue": float(df['order_value'].sum()),
        "sample_size_windows": int(len(window_metrics))
    }
    
    return results, window_metrics