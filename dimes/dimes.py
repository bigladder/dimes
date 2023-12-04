from plotly.graph_objects import Figure, Scatter
from plotly.subplots import make_subplots
from pathlib import Path
from typing import List

class TimeSeriesData:
    def __init__(self, data_values: list, name: str = "", color: str | None = None, is_visible: bool = True):
        self.is_visible = is_visible
        self.name = name
        self.data_values = data_values
        self.color = color

class TimeSeriesPlot:

    def __init__(self, time_values):
        self.figure = Figure()
        self.title = ""
        self.time_values = time_values
        # self.subplots = []#: list(TimeSeriesData) = []

    def write_html_plot(self, path: Path):
        self.figure.write_html(path)



