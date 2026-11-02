"""Chart helpers for the Forestwatch dashboard (EDA by Person C).

Usage in Streamlit:
    from charts import clean_fires, plot_forest_loss
    st.plotly_chart(plot_forest_loss(loss), use_container_width=True)
"""
import pandas as pd
import plotly.express as px

CONFIDENCE_MAP = {"l": "low", "n": "nominal", "h": "high"}
CONFIDENCE_ORDER = ["low", "nominal", "high"]


def clean_fires(fires: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate detections, fix dtypes and label confidence."""
    df = fires.drop_duplicates(
        subset=["latitude", "longitude", "acq_date", "acq_time"]
    ).copy()
    df["acq_date"] = pd.to_datetime(df["acq_date"])
    df["acq_time"] = df["acq_time"].astype(str).str.zfill(4)
    df["hour"] = df["acq_time"].str[:2].astype(int)
    df["confidence"] = df["confidence"].map(CONFIDENCE_MAP).fillna(df["confidence"])
    return df


def plot_forest_loss(loss: pd.DataFrame):
    """Line chart of annual tree cover loss (hectares)."""
    df = loss.sort_values("year")
    fig = px.line(
        df, x="year", y="area_ha", markers=True,
        title="Annual Tree Cover Loss in Australia",
        labels={"year": "Year", "area_ha": "Area lost (ha)"},
    )
    fig.update_traces(line_color="firebrick")
    return fig


def plot_daily_fires(fires_clean: pd.DataFrame):
    """Bar chart of fire detections per day."""
    daily = (
        fires_clean.groupby(fires_clean["acq_date"].dt.date)
        .size().reset_index(name="detections")
    )
    daily["acq_date"] = daily["acq_date"].astype(str)
    return px.bar(
        daily, x="acq_date", y="detections",
        title="Fire detections per day",
        labels={"acq_date": "Date", "detections": "Detections"},
        color_discrete_sequence=["darkorange"],
    )


def plot_confidence(fires_clean: pd.DataFrame):
    """Bar chart of detection confidence levels."""
    counts = (
        fires_clean["confidence"].value_counts()
        .reindex(CONFIDENCE_ORDER).reset_index()
    )
    counts.columns = ["confidence", "count"]
    return px.bar(
        counts, x="confidence", y="count",
        title="Detection confidence levels",
        color_discrete_sequence=["firebrick"],
    )


def plot_frp_distribution(fires_clean: pd.DataFrame):
    """Histogram of Fire Radiative Power (log count axis)."""
    fig = px.histogram(
        fires_clean, x="frp", nbins=60,
        title="Fire Radiative Power distribution",
        labels={"frp": "FRP (MW)"},
        color_discrete_sequence=["darkred"],
    )
    fig.update_yaxes(type="log", title="Count (log)")
    return fig


def plot_fire_map(fires_clean: pd.DataFrame):
    """Map of fire detections coloured by FRP."""
    cap = fires_clean["frp"].quantile(0.99)
    fig = px.scatter_geo(
        fires_clean, lat="latitude", lon="longitude",
        color="frp", range_color=(0, cap),
        color_continuous_scale="YlOrRd",
        title="Fire detections (colour = FRP, MW)",
        hover_data=["acq_date", "confidence", "frp"],
    )
    fig.update_geos(fitbounds="locations", showcountries=True)
    return fig