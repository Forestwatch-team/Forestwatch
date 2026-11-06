"""ForestWatch dashboard. Run: python -m streamlit run app.py"""
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.database import queries
from src.database.db import DatabaseUnavailable
from src.visualization import charts

st.set_page_config(page_title="ForestWatch", layout="wide", page_icon="🌲")

CSS = """
<style>
.block-container {padding-top: 3.5rem; max-width: 1250px;}
header[data-testid="stHeader"] {background: transparent;}
#MainMenu, footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
.hero {background: linear-gradient(135deg, #064e3b 0%, #0f766e 55%, #115e59 100%);
       border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: .6rem;
       border: 1px solid rgba(255,255,255,0.08);}
.hero h1 {color: #ffffff; font-size: 2.2rem; margin: 0 0 .2rem 0; padding: 0;}
.hero p {color: #d1fae5; margin: 0; font-size: 1.02rem;}
.pill {display: inline-block; padding: .2rem .75rem; margin: .8rem .4rem 0 0;
       border-radius: 999px; background: rgba(255,255,255,.14);
       color: #ecfdf5; font-size: .78rem;}
[data-testid="stMetric"] {background: #111a2e; border: 1px solid #1f2a44;
       border-radius: 14px; padding: .9rem 1.1rem;}
[data-testid="stMetricLabel"] {color: #94a3b8;}
[data-testid="stMetricValue"] {color: #f8fafc; font-size: 1.8rem;}
[data-testid="stMetricValue"] > div {overflow: visible !important;
       text-overflow: clip !important; white-space: normal !important;}
button[data-baseweb="tab"] {font-size: 1rem; padding: .6rem 1rem;}
section[data-testid="stSidebar"] {border-right: 1px solid #1f2a44;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
      <h1>🌲 ForestWatch</h1>
      <p>Forest loss and fire activity in Australia, from public satellite data</p>
      <span class="pill">NASA FIRMS</span>
      <span class="pill">Global Forest Watch</span>
      <span class="pill">Australia</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Satellite-derived public data. For learning and awareness, not an official report.")

CONF_NAMES = {"l": "low", "n": "nominal", "h": "high"}
STATUS_ICON = {"SUCCESS": "✅", "PARTIAL": "⚠️", "FAILED": "❌"}


def coverage_text(d1, d2):
    if d1.year == d2.year and d1.month == d2.month:
        return f"{d1.day}–{d2.day} {d2:%b %Y}"
    if d1.year == d2.year:
        return f"{d1:%d %b} – {d2:%d %b %Y}"
    return f"{d1:%d %b %Y} – {d2:%d %b %Y}"


def hectares(x):
    if x >= 1_000_000:
        return f"{x / 1_000_000:.2f} M ha"
    return f"{x / 1_000:,.0f} k ha"


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
st.sidebar.markdown("### 🌲 ForestWatch")
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
    format_func=lambda c: CONF_NAMES.get(c, c))
st.sidebar.caption("Date range and confidence apply to the Fire activity tab. "
                   "Rows with missing confidence are always included.")

tab_over, tab_fire, tab_loss, tab_quality, tab_method = st.tabs(
    ["Overview", "Fire activity", "Forest loss", "Data quality", "Methodology and limits"])

# ---------------- Overview ----------------
with tab_over:
    counts = (meta["counts"].set_index("table_name")["row_count"]
              if not meta["counts"].empty else pd.Series(dtype=int))
    c1, c2, c3, c4 = st.columns([1, 1.5, 1, 1])
    c1.metric("Stored fire detections", f"{int(counts.get('fire_alerts', 0)):,}")
    c2.metric("Fire data covers", coverage_text(min_day, max_day) if has_fire else "No data")
    c3.metric("Forest loss records", f"{int(counts.get('forest_loss', 0)):,}")
    c4.metric("Validation runs", f"{int(counts.get('validation_logs', 0)):,}")
    st.caption("Fire detections with the same location, date and time are counted once.")
    with st.container(border=True):
        st.subheader("Latest validation run")
        if meta["quality"].empty:
            st.info("No validation runs recorded yet.")
        else:
            st.dataframe(meta["quality"].head(1), hide_index=True, width="stretch")

# ---------------- Fire activity ----------------
with tab_fire:
    if not has_fire:
        st.info("No fire data stored yet.")
    elif class_options and not chosen_classes:
        st.warning("Select at least one confidence level.")
    else:
        daily = load_daily(start, end, chosen_classes)
        total = int(daily["detections"].sum()) if not daily.empty else 0
        m1, m2, m3 = st.columns(3)
        m1.metric("Detections in selected range", f"{total:,}",
                  f"{start:%d %b} – {end:%d %b}", delta_color="off", delta_arrow="off")
        if not daily.empty:
            peak = daily.loc[daily["detections"].idxmax()]
            m2.metric("Busiest day", f"{peak['alert_date']:%d %b}",
                      f"{int(peak['detections']):,} detections",
                      delta_color="off", delta_arrow="off")
            m3.metric("Daily average", f"{int(round(daily['detections'].mean())):,}",
                      "detections per day", delta_color="off", delta_arrow="off")
        with st.container(border=True):
            st.markdown("**Detections per day**")
            st.plotly_chart(charts.fire_timeseries(daily))
        with st.container(border=True):
            st.markdown("**Where detections occurred**")
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
        if not loss.empty:
            top = loss.loc[loss["area_ha"].idxmax()]
            last = loss.loc[loss["year"].idxmax()]
            l1, l2, l3 = st.columns(3)
            l1.metric("Highest loss year", f"{int(top['year'])}", hectares(top["area_ha"]),
                      delta_color="off", delta_arrow="off")
            l2.metric("Latest year in data", f"{int(last['year'])}", hectares(last["area_ha"]),
                      delta_color="off", delta_arrow="off")
            l3.metric("Total loss, all years in data", hectares(loss["area_ha"].sum()),
                      f"{int(loss['year'].min())}–{int(loss['year'].max())}",
                      delta_color="off", delta_arrow="off")
        with st.container(border=True):
            st.plotly_chart(charts.loss_bar(loss))
        st.caption("The highest year is shown in red. Tree cover loss is not the same as "
                   "deforestation: it includes harvest and fire-related loss. Methods changed "
                   "in 2011, so compare earlier and later years with caution.")

# ---------------- Data quality ----------------
with tab_quality:
    q = meta["quality"]
    if q.empty:
        st.info("No validation runs recorded yet.")
    else:
        d1, d2, d3 = st.columns(3)
        d1.metric("Validation runs", f"{len(q):,}")
        d2.metric("Records processed", f"{int(q['records_processed'].sum()):,}")
        d3.metric("Records failed", f"{int(q['records_failed'].sum()):,}")
        show = q.copy()
        show["status"] = show["status"].map(
            lambda s: f"{STATUS_ICON.get(str(s).upper(), '')} {s}".strip())
        with st.container(border=True):
            st.dataframe(show, hide_index=True, width="stretch")
        st.caption("Failed records are counted in the validation log; they are not silently ignored.")

# ---------------- Methodology ----------------
with tab_method:
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown("**Sources**")
            st.write("NASA FIRMS active fire detections and Global Forest Watch tree cover loss "
                     "(University of Maryland / Hansen et al.). Please credit both providers.")
        with st.container(border=True):
            st.markdown("**What the data is**")
            st.write("Fire detections are satellite thermal anomalies. One fire can produce many "
                     "detections, and a detection does not prove a wildfire. Tree cover loss is "
                     "annual canopy loss.")
    with right:
        with st.container(border=True):
            st.markdown("**What it is not**")
            st.write("It is not burned area, fire risk, a prediction, or proof that fire caused "
                     "forest loss.")
        with st.container(border=True):
            st.markdown("**Limits**")
            st.write("Clouds, smoke and overpass timing cause missed detections. Times are UTC. "
                     "The fire table has no country column, so fire filters use date and "
                     "confidence only.")