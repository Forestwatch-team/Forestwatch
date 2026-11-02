"""ForestWatch dashboard. Run: python -m streamlit run app.py"""
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.database import queries
from src.database.db import DatabaseUnavailable
from src.visualization import charts

st.set_page_config(page_title="ForestWatch", layout="wide", page_icon="🌲")


@st.cache_data(ttl=600, show_spinner="Connecting to the database...")
def load_meta():
    return queries.load_meta_bundle()


@st.cache_data(ttl=600, show_spinner="Loading daily counts...")
def load_daily(start, end, classes):
    return queries.fire_daily_counts(start, end, classes)


@st.cache_data(ttl=600, show_spinner="Loading map points...")
def load_points(start, end, classes):
    return queries.fire_points(start, end, classes)


@st.cache_data(ttl=3600, show_spinner=False)
def load_loss(country):
    return queries.loss_by_year(country)


st.title("🌲 ForestWatch: Forest Loss and Fire Activity")
st.caption("Satellite-derived public data (NASA FIRMS and Global Forest Watch). "
           "For learning and awareness, not an official report.")

try:
    meta = load_meta()
except (DatabaseUnavailable, RuntimeError) as exc:
    st.error("The database is not reachable. Check DATABASE_URL and your internet connection.")
    st.caption(f"Details: {exc}")
    st.stop()
except Exception as exc:
    st.error("Could not read data. Are the tables created and loaded?")
    st.caption(f"Details: {exc}")
    st.stop()

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
rng = meta["range"]
has_fire = (not rng.empty) and pd.notna(rng.loc[0, "min_day"])
if has_fire:
    min_day = pd.to_datetime(rng.loc[0, "min_day"]).date()
    max_day = pd.to_datetime(rng.loc[0, "max_day"]).date()
else:
    min_day = max_day = date.today()

default_start = max(min_day, max_day - timedelta(days=90))
dates = st.sidebar.date_input("Date range (UTC)", value=(default_start, max_day),
                              min_value=min_day, max_value=max_day)
start, end = dates if isinstance(dates, tuple) and len(dates) == 2 else (default_start, max_day)

class_options = list(meta["classes"]["confidence"]) if not meta["classes"].empty else []
chosen_classes = st.sidebar.multiselect(
    "Confidence", class_options, default=class_options,
    format_func=lambda c: {"l": "low", "n": "nominal", "h": "high"}.get(c, c))
st.sidebar.caption("Rows with missing confidence are always included.")

tab_over, tab_fire, tab_loss, tab_quality, tab_method = st.tabs(
    ["Overview", "Fire activity", "Forest loss", "Data quality", "Methodology and limits"])

# ---------------- Overview ----------------
with tab_over:
    counts = (meta["counts"].set_index("table_name")["row_count"]
              if not meta["counts"].empty else pd.Series(dtype=int))
    c1, c2, c3 = st.columns(3)
    c1.metric("Stored fire detections", f"{int(counts.get('fire_alerts', 0)):,}")
    c2.metric("Forest loss records", f"{int(counts.get('forest_loss', 0)):,}")
    c3.metric("Validation runs", f"{int(counts.get('validation_logs', 0)):,}")
    
    st.caption("Fire detections with the same location, date and time are counted once.")
    
    if meta["quality"].empty:
        st.info("No validation runs recorded yet.")
    else:
        st.subheader("Latest validation run")
        st.dataframe(meta["quality"].head(1), hide_index=True)

# ---------------- Fire activity ----------------
with tab_fire:
    if not has_fire:
        st.info("No fire data stored yet.")
    elif class_options and not chosen_classes:
        st.warning("Select at least one confidence level.")
    else:
        daily = load_daily(start, end, chosen_classes)
        total = int(daily["detections"].sum()) if not daily.empty else 0
        st.metric("Detections in selected range", f"{total:,}")
        st.plotly_chart(charts.fire_timeseries(daily))
        points = load_points(start, end, chosen_classes)
        st.plotly_chart(charts.fire_map(points))
        st.caption("Each dot is one satellite detection (a hot pixel), not a confirmed fire "
                   "and not a burned area. The map shows at most 20,000 of the most recent "
                   "detections. Times are UTC.")

# ---------------- Forest loss ----------------
with tab_loss:
    countries = meta["countries"]
    if countries.empty:
        st.info("No forest loss data stored yet.")
    else:
        names = list(countries["country"])
        idx = names.index("Australia") if "Australia" in names else 0
        country = st.selectbox("Country", names, index=idx)
        loss = load_loss(country)
        st.plotly_chart(charts.loss_bar(loss))
        st.caption("Tree cover loss is not the same as deforestation: it includes harvest and "
                   "fire-related loss. Methods changed in 2011, so compare earlier and later "
                   "years with caution.")

# ---------------- Data quality ----------------
with tab_quality:
    q = meta["quality"]
    if q.empty:
        st.info("No validation runs recorded yet.")
    else:
        st.dataframe(q, hide_index=True)
        st.caption("Failed records are counted in the validation log; they are not silently ignored.")

# ---------------- Methodology ----------------
with tab_method:
    st.markdown("""
**Sources.** NASA FIRMS active fire detections and Global Forest Watch tree cover loss
(University of Maryland / Hansen et al.). Please credit both providers.

**What the data is.** Fire detections are satellite thermal anomalies. One fire can produce many
detections, and a detection does not prove a wildfire. Tree cover loss is annual canopy loss.

**What it is not.** It is not burned area, fire risk, a prediction, or proof that fire caused forest loss.

**Limits.** Clouds, smoke and overpass timing cause missed detections. Times are UTC.
The fire table has no country column, so fire filters use date and confidence only.
""")