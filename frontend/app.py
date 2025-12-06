import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# --- CLOUD SETUP: Add backend to path so we can import directly ---
# This ensures we can find your simulation.py and analysis.py files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.simulation import MarketplaceSimulator
from backend.analysis import analyze_experiment

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dynamic Pricing Engine", 
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Dynamic Marketplace Pricing: Switchback Experiment Simulation")
st.markdown("""
**Objective:** Test if increasing prices by **X%** (Surge) maintains net revenue despite lower conversion.  
**Methodology:** Switchback Testing (30-min time windows) to isolate network effects.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Simulation Parameters")

# 1. Duration Slider
days = st.sidebar.slider("Experiment Duration (Days)", min_value=7, max_value=60, value=14)

# 2. Uplift Slider (The "Sensitivity Analysis" Tool)
uplift_input = st.sidebar.slider(
    "Target Price Uplift (Treatment)", 
    min_value=1.00, 
    max_value=1.50, 
    value=1.10, 
    step=0.01,
    help="1.10 means Treatment prices are 10% higher on average."
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Scenario:** Testing a {(uplift_input-1)*100:.0f}% price hike over {days} days.")

# --- MAIN EXECUTION ---
if st.sidebar.button("🚀 Run Experiment"):
    with st.spinner("Simulating marketplace dynamics..."):
        try:
            # 1. Initialize Simulator
            simulator = MarketplaceSimulator()
            
            # 2. Run Simulation (Passing our slider inputs)
            # NOTE: Ensure your simulation.py accepts 'days' and 'uplift_factor'
            df = simulator.simulate_marketplace(uplift_factor=uplift_input, days=days) 
            
            # 3. Run Analysis
            summary, window_metrics = analyze_experiment(df)
            
            # --- KPI DASHBOARD ---
            st.subheader("Experiment Results")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            kpi1.metric("Total Rides", f"{summary['total_rides']:,}")
            kpi2.metric("Control OCR", f"{summary['control_ocr']:.1%}", help="Order Completion Rate (Baseline)")
            kpi3.metric("Treatment OCR", f"{summary['treatment_ocr']:.1%}", help="Order Completion Rate (with Surge)")
            
            lift = summary['lift'] * 100
            kpi4.metric(
                "Conversion Lift", 
                f"{lift:.2f}%", 
                delta=f"{lift:.2f}%",
                delta_color="normal" if lift > 0 else "inverse" # Red is bad for conversion drop
            )

            # --- SIGNIFICANCE & REVENUE ---
            st.divider()
            col_sig, col_rev = st.columns([1, 1])
            
            with col_sig:
                st.markdown("### 📊 Statistical Significance")
                st.write(f"**P-Value:** `{summary['p_value']:.5f}`")
                
                if summary['is_significant']:
                    st.success("RESULT: Statistically Significant (We can reject Null Hypothesis)")
                else:
                    st.warning("RESULT: Not Significant (Need more data or stronger signal)")
            
            with col_rev:
                st.markdown("### 💰 Revenue Impact")
                # Calculate simple Revenue per Request (RPR)
                control_rpr = summary['control_gmv'] / summary['control_requests'] if 'control_gmv' in summary else 0
                treatment_rpr = summary['treatment_gmv'] / summary['treatment_requests'] if 'treatment_gmv' in summary else 0
                
                rev_lift = ((treatment_rpr - control_rpr) / control_rpr) * 100
                st.metric("Revenue per Request (Est.)", f"${treatment_rpr:.2f}", delta=f"{rev_lift:.1f}%")

            # --- CHARTS ---
            st.divider()
            
            # Chart 1: Price Distribution (To prove the Surge works)
            st.subheader("1. Price Distribution Check")
            fig_hist = px.histogram(
                df, x="price_quoted", color="variant", barmode="overlay",
                title="Did Treatment actually pay more?",
                color_discrete_map={'Control': '#3498db', 'Treatment': '#e74c3c'}
            )
            st.plotly_chart(fig_hist, width='stretch')
            
            # --- ADD THIS BACK ---
            # Chart 2: Boxplot
            st.subheader("2. Stability Check (Box Plot)")
            fig_box = px.box(
                window_metrics, x="variant", y="ocr", 
                title="Distribution of Order Completion Rate (Spread)",
                color="variant",
                points="all", # Shows individual dots alongside the box
                color_discrete_map={'Control': '#3498db', 'Treatment': '#e74c3c'}
            )
            st.plotly_chart(fig_box, width='stretch')
            # ---------------------

            # Chart 3: Time Series
            st.subheader("2. OCR Trends over Time")
            metrics_sorted = window_metrics.sort_values('window_start')
            fig_time = px.scatter(
                metrics_sorted, x="window_start", y="ocr", color="variant",
                title="30-Min Window Performance (Switchback View)",
                opacity=0.5,
                color_discrete_map={'Control': '#3498db', 'Treatment': '#e74c3c'}
            )
            st.plotly_chart(fig_time, width='stretch')

        except Exception as e:
            st.error(f"Simulation Failed: {e}")
            st.info("Tip: Check if 'simulate_marketplace' in simulation.py accepts 'days' argument.")

else:
    st.info("👈 Adjust settings in the sidebar and click 'Run Experiment'")