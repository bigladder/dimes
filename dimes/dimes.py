"""Module for plotting time series data."""
from pathlib import Path
from typing import List
from plotly.graph_objects import Figure, Scatter  # type: ignore

# from plotly.subplots import make_subplots


class TimeSeriesData:
    """Time series data."""

    def __init__(
        self, data_values: list, name: str = "", color: str | None = None, is_visible: bool = True
    ):
        self.is_visible = is_visible
        self.name = name
        self.data_values = data_values
        self.color = color


class TimeSeriesPlot:
    """Time series plot."""

    def __init__(self, time_values: list):
        self.fig = Figure()
        # self.fig = make_subplots(rows=2,shared_xaxes=True)
        self.time_values = time_values
        # self.subplots = []#: list(TimeSeriesData) = []
        self.series: List[TimeSeriesData] = []
        self.is_finalized = False

    def add_time_series(self, time_series: TimeSeriesData, subplot_number: int = 0):
        """Add a TimeSeriesData object to the plot."""
        self.series.append(time_series)

    def finalize_plot(self):
        """Once all TimeSeriesData objects have been added, generate plot and subplots."""
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
                        visible="legendonly" if not time_series.is_visible else True,
                        line=dict(color=time_series.color),
                    ),
                    row=time_series.subplot_index,
                    # row=1,
                    col=1,
                )

            self.is_finalized = True

    def write_html_plot(self, path: Path):
        "Write plots to html file at specified path."
        self.finalize_plot()
        self.fig.write_html(path)
