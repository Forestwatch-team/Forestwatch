import streamlit as st

st.set_page_config(page_title="ForestWatch Dashboard", layout="wide")
st.title("🌲 ForestWatch Monitoring Dashboard")

# Creating 5 Tabs as per manual requirement
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", 
    "FIRMS Fire Alerts", 
    "GFW Forest Loss", 
    "Database Diagnostics", 
    "Settings"
])

with tab1:
    st.header("Project Overview")
    st.write("Welcome to the ForestWatch system dashboard.")

with tab2:
    st.header("FIRMS Fire Alerts Data")
    st.write("Real-time monitoring of active fire alerts.")

with tab3:
    st.header("GFW Forest Loss Analytics")
    st.write("Annual forest canopy cover loss metrics.")

with tab4:
    st.header("Database Diagnostics & Validation Logs")
    st.write("Status logs for pipeline execution audits.")

with tab5:
    st.header("System Settings")
    st.write("Configuration profiles for external APIs and database instances.")
