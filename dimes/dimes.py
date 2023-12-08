"""Module for plotting time series data."""
from pathlib import Path
from typing import List
from plotly.graph_objects import Figure, Scatter  # type: ignore
from plotly.subplots import make_subplots  # type: ignore


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

    class TimeSeriesSubplotPair:
        """Basic class to couple time series and subplot number"""

        def __init__(self, time_series: TimeSeriesData, subplot_number: int):
            self.time_series = time_series
            self.subplot_number = subplot_number

    def __init__(self, time_values: list):
        self.fig = Figure()
        # self.fig = make_subplots(rows=2,shared_xaxes=True)
        self.time_values = time_values
        self.number_of_subplots = 1
        self.time_series_subplot_pairs: List[TimeSeriesPlot.TimeSeriesSubplotPair] = []
        self.is_finalized = False

    def add_time_series(self, time_series: TimeSeriesData, subplot_number: int | None = None):
        """Add a TimeSeriesData object to the plot."""
        if subplot_number is None:
            subplot_number = self.number_of_subplots
        else:
            self.number_of_subplots = max(subplot_number, self.number_of_subplots)
        self.time_series_subplot_pairs.append(
            TimeSeriesPlot.TimeSeriesSubplotPair(time_series, subplot_number)
        )

    def finalize_plot(self):
        """Once all TimeSeriesData objects have been added, generate plot and subplots."""
        if not self.is_finalized:
            if not self.time_series_subplot_pairs:
                raise Exception("No time series data provided.")
            if self.number_of_subplots > 1:
                self.fig = make_subplots(
                    rows=self.number_of_subplots, shared_xaxes=True, vertical_spacing=0.05
                )
            for time_series_subplot_pair in self.time_series_subplot_pairs:
                self.fig.add_trace(
                    Scatter(
                        x=self.time_values,
                        y=time_series_subplot_pair.time_series.data_values,
                        name=time_series_subplot_pair.time_series.name,
                        mode="lines",
                        visible="legendonly"
                        if not time_series_subplot_pair.time_series.is_visible
                        else True,
                        line=dict(color=time_series_subplot_pair.time_series.color),
                    ),
                    row=None
                    if self.number_of_subplots == 1
                    else time_series_subplot_pair.subplot_number,
                    col=None if self.number_of_subplots == 1 else 1,
                )

            self.is_finalized = True

    def write_html_plot(self, path: Path):
        "Write plots to html file at specified path."
        self.finalize_plot()
        self.fig.write_html(path)
