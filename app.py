import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="ForestWatch Dashboard", layout="wide")

# Sidebar indicating mode as per manual instructions
st.sidebar.title("🌲 Navigation")
st.sidebar.markdown("**STATUS:** SYNTHETIC stub data active")

# Sidebar Filters
st.sidebar.subheader("Global Filters")
year_filter = st.sidebar.slider("Select Analysis Year", 2020, 2026, 2024)
region_filter = st.sidebar.selectbox("Select Country/Region", ["All", "Australia", "Brazil", "Indonesia", "Global"])

# Tab names explicitly requested by manual
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", 
    "Fire activity", 
    "Forest loss", 
    "Data quality", 
    "Methodology and limits"
])

# ----------------- TAB 1: OVERVIEW -----------------
with tab1:
    st.header("Project Status & Executive Summary")
    st.write(f"Displaying consolidated analytics for **{region_filter}** in the year **{year_filter}**.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Fire Alerts Logged", f"{11894 if region_filter=='All' else 2450}")
    col2.metric("Total Forest Loss Area (Ha)", f"{45210 if region_filter=='All' else 8900}")
    col3.metric("System Health", "98.4%")
    
    st.subheader("Recent Consolidated Alert Stream")
    sample_df = pd.DataFrame({
        "Timestamp": pd.date_range(end=pd.Timestamp.now(), periods=5, freq='h'),
        "Region": ["Australia", "Brazil", "Australia", "Indonesia", "Brazil"],
        "Metric Type": ["Fire Alert", "Forest Canopy Loss", "Fire Alert", "Fire Alert", "Forest Canopy Loss"],
        "Severity/Area": ["High (90%)", "12.4 Ha", "Medium (50%)", "High (92%)", "45.1 Ha"]
    })
    st.dataframe(sample_df, use_container_width=True)
    st.caption("Figure 1.1: Live-streamed data ingestion events across monitored operational sectors.")

# ----------------- TAB 2: FIRE ACTIVITY -----------------
with tab2:
    st.header("FIRMS Active Fire Telemetry & Spatial Trends")
    st.write("Visualizing thermal anomalies detected via satellite instrumentation channels.")
    
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['VIIRS SNPP', 'MODIS Terra', 'MODIS Aqua']
    )
    st.line_chart(chart_data)
    st.caption("Figure 2.1: Temporal distribution of localized high-confidence thermal alerts by instrument type.")

# ----------------- TAB 3: FOREST LOSS -----------------
with tab3:
    st.header("GFW Tree Cover & Canopy Disturbance Metrics")
    st.write("Annual forest loss statistics mapped against target coordinates.")
    
    bar_data = pd.DataFrame({
        'Year': [2019, 2020, 2021, 2022, 2023, 2024],
        'Loss Area (Ha)': [12000, 15000, 18000, 14000, 16500, 11000]
    }).set_index('Year')
    st.bar_chart(bar_data)
    st.caption("Figure 3.1: Comparative breakdown of aggregated annual canopy reduction metrics.")

# ----------------- TAB 4: DATA QUALITY -----------------
with tab4:
    st.header("Pipeline Validation Logs & Audit Tracking")
    st.write("System health monitoring checking records processed against failed data frames.")
    
    quality_df = pd.DataFrame({
        "Source File Name": ["firms_VIIRS_SNPP_NRT_2026.csv", "gfw_gadm__tcl__iso_AUS.json", "fire_alerts_sample.csv"],
        "Records Processed": [14500, 8920, 1250],
        "Records Failed": [0, 0, 15],
        "Pipeline Status": ["SUCCESS", "SUCCESS", "PARTIAL"]
    })
    st.table(quality_df)
    st.caption("Figure 4.1: Database validation metrics checking ingest reliability and deduplication integrity.")

# ----------------- TAB 5: METHODOLOGY AND LIMITS -----------------
with tab5:
    st.header("Data Models, Architecture Contracts & Constraints")
    st.subheader("Operational Constraints")
    st.markdown("""
    * **Satellite Sync Delays:** FIRMS data has an ingestion delay window depending on orbital paths.
    * **Resolution Thresholds:** Spatial filters parse anomalies inside strict bounds (-90 to 90 lat / -180 to 180 lon).
    * **Confidence Mapping:** Character confidence mapping stringently labels inputs into structured numeric equivalents.
    """)
    st.subheader("Data Structures Contract")
    st.info("System interfaces map exactly with schemas specified in `docs/interfaces.md` contracts.")
    st.caption("Figure 5.1: Functional layout definitions and metadata integration limits.")