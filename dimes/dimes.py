from plotly.graph_objects import Figure, Scatter
from plotly.subplots import make_subplots
from pathlib import Path

class TimeSeriesData:
    def __init__(self, data_values):
        self.default_visibility = True
        self.dimension = ""
        self.name = ""
        self.data_values = data_values
        self.subplot_index = 0
        self.color = 0

class TimeSeriesPlot:

    def __init__(self, time_values):
        self.figure = Figure()
        self.title = ""
        self.time_values = time_values
        # self.subplots = []#: list(TimeSeriesData) = []

    def write_html_plot(self, path: Path):
        self.figure.write_html(path)



