"""Plotly charts. Each function returns a figure and never fails on empty data."""
import plotly.express as px
import plotly.graph_objects as go

GREEN = "#22c55e"
ORANGE = "#f97316"
RED = "#ef4444"
MUTED = "#94a3b8"
GRID = "rgba(148,163,184,0.15)"

CONF_LABELS = {"l": "low", "n": "nominal", "h": "high"}
CONF_COLORS = {"low": "#facc15", "nominal": "#fb923c", "high": "#ef4444", "unknown": MUTED}


def _style(fig, height=380):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        margin=dict(l=10, r=10, t=20, b=10),
        hoverlabel=dict(bgcolor="#0f172a", font_color="#f8fafc"),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


def empty_figure(message="No data to show"):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=16, color=MUTED),
                       xref="paper", yref="paper", x=0.5, y=0.5)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _style(fig, 320)


def _is_empty(df, cols):
    return df is None or df.empty or any(c not in df.columns for c in cols)


def fire_timeseries(daily):
    if _is_empty(daily, ["alert_date", "detections"]):
        return empty_figure("No fire detections for this selection")
    fig = go.Figure(go.Scatter(
        x=daily["alert_date"], y=daily["detections"],
        mode="lines+markers",
        line=dict(color=ORANGE, width=3),
        marker=dict(size=7),
        fill="tozeroy", fillcolor="rgba(249,115,22,0.15)",
        hovertemplate="%{x|%d %b %Y}<br>%{y:,} detections<extra></extra>",
    ))
    fig.update_xaxes(title="Date (UTC)", tickformat="%d %b")
    if len(daily) <= 14:
        fig.update_xaxes(dtick=86400000)
    fig.update_yaxes(title="Detections per day", rangemode="tozero")
    return _style(fig, 380)


def fire_map(points):
    if _is_empty(points, ["latitude", "longitude", "confidence"]):
        return empty_figure("No fire points for this selection")
    labels = points["confidence"].map(CONF_LABELS).fillna(points["confidence"]).fillna("unknown")
    pts = points.assign(confidence=labels)
    kwargs = dict(
        lat="latitude", lon="longitude", color="confidence",
        color_discrete_map=CONF_COLORS,
        category_orders={"confidence": ["low", "nominal", "high"]},
        center=dict(lat=-25.5, lon=134.0), zoom=3, height=560, opacity=0.8,
    )
    try:
        fig = px.scatter_map(pts, map_style="carto-darkmatter", **kwargs)
    except AttributeError:  # older Plotly
        fig = px.scatter_mapbox(pts, mapbox_style="carto-darkmatter", **kwargs)
    fig.update_traces(marker=dict(size=5))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(title="Confidence", bgcolor="rgba(15,23,42,0.7)"),
    )
    return fig


def loss_bar(loss):
    if _is_empty(loss, ["year", "area_ha"]):
        return empty_figure("No forest loss data for this selection")
    top = loss["area_ha"].idxmax()
    colors = [RED if i == top else GREEN for i in loss.index]
    fig = go.Figure(go.Bar(
        x=loss["year"], y=loss["area_ha"], marker_color=colors,
        hovertemplate="%{x}: %{y:,.0f} hectares<extra></extra>",
    ))
    fig.update_xaxes(title="Year")
    fig.update_yaxes(title="Tree cover loss (hectares)")
    return _style(fig, 380)