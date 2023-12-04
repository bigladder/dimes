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
    def finalize_plot(self):
        if not self.is_finalized:
            if not self.series:
                raise Exception("No time series data provided.")
            for time_series in self.series:
                self.fig.add_trace(
                    Scatter(
                        x=self.time_values,
                        y=time_series.data_values,
                        name=time_series.name,
                        mode="lines",
                        visible='legendonly' if not time_series.is_visible else True,
                        line=dict(
                            color=time_series.color
                        )),
                    row=time_series.subplot_index,
                    # row=1,
                    col=1
                    )
            
            self.is_finalized = True
        

    def write_html_plot(self, path: Path):
        self.finalize_plot()
