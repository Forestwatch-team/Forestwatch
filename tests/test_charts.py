import pandas as pd

from src.visualization import charts


def test_empty_figure_shows_message():
    fig = charts.empty_figure("No data")
    assert fig.layout.annotations[0].text == "No data"


def test_charts_survive_empty_data():
    empty = pd.DataFrame()
    assert charts.fire_timeseries(empty) is not None
    assert charts.fire_map(empty) is not None
    assert charts.loss_bar(empty) is not None