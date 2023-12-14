"""Module for plotting time series data."""
from pathlib import Path
from typing import List, Union
import warnings

from plotly.graph_objects import Figure, Scatter  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
import koozie


class TimeSeriesData:
    """Time series data."""

    def __init__(
        self,
        data_values: list,
        name: str | None = None,
        native_units: str = "",
        display_units: str | None = None,
        color: str | None = None,
        line_type: str | None = None,
        is_visible: bool = True,
    ):
        self.data_values = data_values
        self.native_units = native_units
        self.dimensionality = koozie.get_dimensionality(self.native_units)
        if name is None:
            self.name = str(self.dimensionality)
        else:
            self.name = name
        if display_units is None:
            self.display_units = self.native_units
        else:
            self.display_units = display_units
            display_units_dimensionality = koozie.get_dimensionality(self.display_units)
            if self.dimensionality != display_units_dimensionality:
                raise Exception(
                    f"display_units, {self.display_units}, dimensionality ({display_units_dimensionality}) does not match native_units, {self.native_units}, dimensionality ({self.dimensionality})"
                )
        self.color = color
        self.line_type = line_type
        self.is_visible = is_visible


class TimeSeriesAxis:
    """Time series 'Y' axis. May contain multiple `TimeSeriesData` objects."""

    def __init__(self, time_series: TimeSeriesData) -> None:
        self.title = None
        self.units = time_series.display_units
        self.dimensionality = time_series.dimensionality
        self.time_series: List[TimeSeriesData] = [time_series]

    def get_axis_label(self) -> str:
        """Make the string that appears as the axis label"""
        return f"{self.title} [{self.units}]"


class TimeSeriesSubplot:
    """Time series subplot. May contain multiple `TimeSeriesAxis` objects."""

    def __init__(self) -> None:
        self.axes: List[TimeSeriesAxis] = []

    def add_time_series(self, time_series) -> None:
        """Add `TimeSeriesData` to an axis"""
        # Add time series to existing axis of the same dimensionality (if it exists)
        for axis in self.axes:
            if axis.dimensionality == time_series.dimensionality:
                time_series.display_units = axis.units
                axis.time_series.append(time_series)
                return
        # Otherwise, make a new axis
        self.axes.append(TimeSeriesAxis(time_series))


class TimeSeriesPlot:
    """Time series plot."""

    def __init__(self, time_values: list):
        self.fig = Figure()
        self.time_values = time_values
        self.subplots: List[Union[TimeSeriesSubplot, None]] = [None]
        self.is_finalized = False

    def add_time_series(self, time_series: TimeSeriesData, subplot_number: int | None = None):
        """Add a TimeSeriesData object to the plot."""
        if subplot_number is None:
            # Default case
            subplot_number = len(self.subplots)
        else:
            if subplot_number > len(self.subplots):
                # Make enough empty subplots
                self.subplots += [None] * (subplot_number - len(self.subplots))
        if self.subplots[subplot_number - 1] is None:
            self.subplots[subplot_number - 1] = TimeSeriesSubplot()
        self.subplots[subplot_number - 1].add_time_series(time_series)  # type: ignore[union-attr]

    def finalize_plot(self):
        """Once all TimeSeriesData objects have been added, generate plot and subplots."""
        if not self.is_finalized:
            at_least_one_subplot = False
            number_of_subplots = len(self.subplots)
            if len(self.subplots) > 1:
                self.fig = make_subplots(
                    rows=number_of_subplots, shared_xaxes=True, vertical_spacing=0.05
                )
            for subplot_index, subplot in enumerate(self.subplots):
                subplot_number = subplot_index + 1
                if subplot is not None:
                    for axis in subplot.axes:
                        for time_series in axis.time_series:
                            at_least_one_subplot = True
                            self.fig.add_trace(
                                Scatter(
                                    x=self.time_values,
                                    y=time_series.data_values,
                                    name=time_series.name,
                                    mode="lines",
                                    visible="legendonly" if not time_series.is_visible else True,
                                    line=dict(
                                        color=time_series.color,
                                        dash=time_series.line_type,
                                    ),
                                ),
                                row=None if number_of_subplots == 1 else subplot_number,
                                col=None if number_of_subplots == 1 else 1,
                            )
                else:
                    warnings.warn(f"Subplot {subplot_number} is unused.")

            if not at_least_one_subplot:
                raise Exception("No time series data provided.")

            self.is_finalized = True

    def write_html_plot(self, path: Path):
        "Write plots to html file at specified path."
        self.finalize_plot()
        self.fig.write_html(path)
