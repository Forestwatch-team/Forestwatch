"""Plotly charts. Each function returns a figure and never fails on empty data."""
import plotly.express as px
import plotly.graph_objects as go


def empty_figure(message="No data to show"):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=18),
                       xref="paper", yref="paper", x=0.5, y=0.5)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(height=350)
    return fig


def _is_empty(df, cols):
    return df is None or df.empty or any(c not in df.columns for c in cols)


def fire_timeseries(daily):
    if _is_empty(daily, ["alert_date", "detections"]):
        return empty_figure("No fire detections for this selection")
    fig = px.line(daily, x="alert_date", y="detections",
                  labels={"alert_date": "Date (UTC)", "detections": "Detections per day"})
    fig.update_layout(height=380)
    return fig


def fire_map(points):
    if _is_empty(points, ["latitude", "longitude"]):
        return empty_figure("No fire points for this selection")
    kwargs = dict(lat="latitude", lon="longitude", color="confidence", zoom=3, height=550)
    try:
        fig = px.scatter_map(points, map_style="open-street-map", **kwargs)
    except AttributeError:  # older Plotly
        fig = px.scatter_mapbox(points, mapbox_style="open-street-map", **kwargs)
    return fig


def loss_bar(loss):
    if _is_empty(loss, ["year", "area_ha"]):
        return empty_figure("No forest loss data for this selection")
    fig = px.bar(loss, x="year", y="area_ha",
                 labels={"year": "Year", "area_ha": "Tree cover loss (hectares)"})
    fig.update_layout(height=380)
    return fig