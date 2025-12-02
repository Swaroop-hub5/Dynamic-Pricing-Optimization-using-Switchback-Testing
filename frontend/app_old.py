import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Experimentation Platform", layout="wide")

st.title("Mock Experiment: Dynamic Pricing Switchback")
st.markdown("""
**Project:** Optimizing Order Completion Rate (OCR) via Dynamic Pricing.  
**Method:** Switchback Testing (30-min windows) to mitigate network interference.
""")

# Sidebar Controls
st.sidebar.header("Experiment Settings")
days = st.sidebar.slider("Duration (Days)", 7, 30, 14)
st.sidebar.info("Click 'Run Experiment' to generate synthetic data and analyze.")

if st.sidebar.button("Run Experiment"):
    with st.spinner("Simulating Marketplace..."):
        try:
            response = requests.post(f"{API_URL}/run-simulation?days={days}")
            data = response.json()
            
            summary = data['summary']
            metrics_df = pd.DataFrame(data['window_metrics'])
            
            # --- KPI ROW ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Rides", f"{summary['total_rides']:,}")
            col2.metric("Control OCR", f"{summary['control_ocr']:.2%}")
            col3.metric("Treatment OCR", f"{summary['treatment_ocr']:.2%}")
            
            lift = summary['lift'] * 100
            col4.metric("Lift", f"{lift:.2f}%", delta_color="normal" if lift > 0 else "inverse")

            # --- STATISTICAL SIGNIFICANCE ---
            st.divider()
            st.subheader("Statistical Inference")
            
            sig_col1, sig_col2 = st.columns(2)
            
            with sig_col1:
                st.markdown(f"**P-Value:** `{summary['p_value']:.4f}`")
                if summary['is_significant']:
                    st.success("Result is Statistically Significant (p < 0.05)")
                else:
                    st.error("Result is NOT Significant (p >= 0.05)")
                
                st.markdown("""
                *Note: P-value is calculated using Welch's t-test on time-window aggregated means, 
                not user-level data, to account for time-series correlation.*
                """)

            # --- VISUALIZATION ---
            with sig_col2:
                # Box Plot of OCR by Variant
                fig = px.box(metrics_df, x="variant", y="ocr", 
                             title="Distribution of Order Completion Rate (Window-Level)",
                             color="variant", 
                             color_discrete_map={'Control': '#FF4B4B', 'Treatment': '#34C759'})
                st.plotly_chart(fig, use_container_width=True)

            # --- TIME SERIES ---
            st.subheader("Hourly Performance (Switchback View)")
            
            # Sort for line chart
            metrics_df['window_start'] = pd.to_datetime(metrics_df['window_start'])
            metrics_df = metrics_df.sort_values('window_start')
            
            # Scatter plot with color mapped to variant
            fig2 = px.scatter(metrics_df, x="window_start", y="ocr", color="variant",
                              title="OCR over Time (Each dot is a 30-min window)",
                              labels={"window_start": "Time", "ocr": "Order Completion Rate"},
                              opacity=0.6)
            st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error(f"Error connecting to backend: {e}. Make sure FastAPI is running.")

else:
    st.info("Waiting for input...")