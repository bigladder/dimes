"""Module for plotting time series data."""
from pathlib import Path
from typing import List, Union
import warnings
from dataclasses import dataclass

from plotly.graph_objects import Figure, Scatter  # type: ignore
from plotly.subplots import make_subplots  # type: ignore


class TimeSeriesData:
    """Time series data."""

    def __init__(
        self,
        data_values: list,
        name: str = "",
        color: Union[str, None] = None,
        is_visible: bool = True,
        line_type: Union[str, None] = None,
    ):
        self.is_visible = is_visible
        self.name = name
        self.data_values = data_values
        self.color = color
        self.line_type = line_type


class TimeSeriesPlot:
    """Time series plot."""

    @dataclass
    class TimeSeriesSubplotPair:
        """Basic class to couple time series and subplot number"""

        time_series: TimeSeriesData
        subplot_number: int

    def __init__(self, time_values: list):
        self.fig = Figure()
        # self.fig = make_subplots(rows=2,shared_xaxes=True)
        self.time_values = time_values
        self.number_of_subplots = 1
        self.time_series_subplot_pairs: List[TimeSeriesPlot.TimeSeriesSubplotPair] = []
        self.is_finalized = False

    def add_time_series(
        self, time_series: TimeSeriesData, subplot_number: Union[int, None] = None
    ) -> None:
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
            subplots_used = [False] * self.number_of_subplots
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
                        line={
                            "color": time_series_subplot_pair.time_series.color,
                            "dash": time_series_subplot_pair.time_series.line_type,
                        },
                    ),
                    row=None
                    if self.number_of_subplots == 1
                    else time_series_subplot_pair.subplot_number,
                    col=None if self.number_of_subplots == 1 else 1,
                )
                subplots_used[time_series_subplot_pair.subplot_number - 1] = True

            for i, subplot_used in enumerate(subplots_used):
                if not subplot_used:
                    warnings.warn(f"Subplot {i + 1} is unused.")

            self.is_finalized = True

    def write_html_plot(self, path: Path) -> None:
        "Write plots to html file at specified path."
        self.finalize_plot()
        self.fig.write_html(path)
