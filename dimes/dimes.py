from plotly.graph_objects import Figure, Scatter
from pathlib import Path

class TimeSeriesData:
    def __init__(self, values):
        self.default_visibility = True
        self.dimension = ""
        self.name = ""
        self.values = values
        self.subplot_index = 0
        self.color = 0

class TimeSeriesPlot:

    def __init__(self, time_values):
        self.figure = Figure()
        self.title = ""
        self.time_values = time_values
        self.subplots = []#: list(TimeSeriesData) = []

    def add_time_series(self, time_series: TimeSeriesData):
        self.figure.add_trace(
            Scatter(
                x=self.time_values,
                y=time_series.values,
                name=time_series.name,
                mode="lines",
                visible='legendonly' if not time_series.default_visibility else True
            ))

    def write_html_plot(self, path: Path):
        self.figure.write_html(path)



