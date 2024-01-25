"""Module for plotting time series data."""
from pathlib import Path
from typing import List, Tuple, Union
import warnings

from plotly.graph_objects import Figure, Scatter  # type: ignore
import koozie

from .common import LineProperties, DimensionalData


class TimeSeriesData(DimensionalData):
    """Time series data."""

    def __init__(
        self,
        data_values: list,
        name: Union[str, None] = None,
        native_units: str = "",
        display_units: Union[str, None] = None,
        line_properties: LineProperties = LineProperties(),
        is_visible: bool = True,
    ):
        super().__init__(data_values, name, native_units, display_units)
        self.line_properties = line_properties
        self.is_visible = is_visible


class TimeSeriesAxis:
    """Time series 'Y' axis. May contain multiple `TimeSeriesData` objects."""

    def __init__(self, time_series: TimeSeriesData, name: Union[str, None]) -> None:
        self.name = name
        self.units = time_series.display_units
        self.dimensionality = time_series.dimensionality
        self.time_series: List[TimeSeriesData] = [time_series]

    def get_axis_label(self) -> str:
        """Make the string that appears as the axis label"""
        return f"{self.name} [{self.units}]"


class TimeSeriesSubplot:
    """Time series subplot. May contain multiple `TimeSeriesAxis` objects."""

    def __init__(self) -> None:
        self.axes: List[TimeSeriesAxis] = []

    def add_time_series(
        self, time_series: TimeSeriesData, axis_name: Union[str, None] = None
    ) -> None:
        """Add `TimeSeriesData` to an axis"""
        if axis_name is not None:
            # Add time series to existing axis of the same name if it exists
            for axis in self.axes:
                if axis.name == axis_name:
                    self.add_time_series_to_existing_axis(time_series, axis)
                    return
        else:
            # Add time series to existing axis of the dimensionality if it exists
            for axis in self.axes:
                if axis.dimensionality == time_series.dimensionality:
                    self.add_time_series_to_existing_axis(time_series, axis)
                    return
            axis_name = time_series.name

        # Otherwise, make a new axis
        self.axes.append(TimeSeriesAxis(time_series, axis_name))

    def add_time_series_to_existing_axis(
        self, time_series: TimeSeriesData, axis: TimeSeriesAxis
    ) -> None:
        """Add `TimeSeriesData` to an existing `TimeSeriesAxis`"""
        # Update time series display units to match the axis
        time_series.set_display_units(axis.units)
        axis.time_series.append(time_series)


class TimeSeriesPlot:
    """Time series plot."""

    def __init__(self, time_values: list):
        self.figure = Figure()
        self.time_values = time_values
        self.subplots: List[Union[TimeSeriesSubplot, None]] = [None]
        self.is_finalized = False

    def add_time_series(
        self,
        time_series: TimeSeriesData,
        subplot_number: Union[int, None] = None,
        axis_name: Union[str, None] = None,
    ) -> None:
        """Add a TimeSeriesData object to the plot."""
        if subplot_number is None:
            # Default case
            subplot_number = len(self.subplots)
        else:
            if subplot_number > len(self.subplots):
                # Make enough empty subplots
                self.subplots += [None] * (subplot_number - len(self.subplots))
        subplot_index = subplot_number - 1
        if self.subplots[subplot_index] is None:
            self.subplots[subplot_index] = TimeSeriesSubplot()
        self.subplots[subplot_index].add_time_series(time_series, axis_name)  # type: ignore[union-attr]

    def finalize_plot(self):
        """Once all TimeSeriesData objects have been added, generate plot and subplots."""
        if not self.is_finalized:
            at_least_one_subplot = False
            number_of_subplots = len(self.subplots)
            subplot_domains = get_subplot_domains(number_of_subplots)
            absolute_axis_index = 0  # Used to track axes data in the plot
            for subplot_index, subplot in enumerate(self.subplots):
                subplot_number = subplot_index + 1
                x_axis_id = subplot_number
                subplot_base_y_axis_id = absolute_axis_index + 1
                if subplot is not None:
                    y_axis_side = "left"
                    for axis_number, axis in enumerate(subplot.axes):
                        y_axis_id = absolute_axis_index + 1
                        for time_series in axis.time_series:
                            at_least_one_subplot = True
                            self.figure.add_trace(
                                Scatter(
                                    x=self.time_values,
                                    y=koozie.convert(
                                        time_series.data_values,
                                        time_series.native_units,
                                        axis.units,
                                    ),
                                    name=time_series.name,
                                    yaxis=f"y{y_axis_id}",
                                    xaxis=f"x{x_axis_id}",
                                    mode=time_series.line_properties.get_line_mode(),
                                    visible="legendonly"
                                    if not time_series.line_properties.is_visible
                                    else True,
                                    line={
                                        "color": time_series.line_properties.color,
                                        "dash": time_series.line_properties.line_type,
                                    },
                                    marker={
                                        "size": time_series.line_properties.marker_size,
                                        "color": time_series.line_properties.marker_fill_color,
                                        "symbol": time_series.line_properties.marker_symbol,
                                        "line": {
                                            "color": time_series.line_properties.marker_line_color,
                                            "width": 2,
                                        },
                                    },
                                ),
                            )
                        is_base_y_axis = subplot_base_y_axis_id == y_axis_id
                        self.figure.layout[f"yaxis{y_axis_id}"] = {
                            "title": axis.get_axis_label(),
                            "domain": subplot_domains[subplot_index]
                            if subplot_base_y_axis_id == y_axis_id
                            else None,
                            "side": y_axis_side,
                            "anchor": f"x{x_axis_id}",
                            "overlaying": f"y{subplot_base_y_axis_id}"
                            if not is_base_y_axis
                            else None,
                            "tickmode": "sync" if not is_base_y_axis else None,
                            "autoshift": True if axis_number > 1 else None,
                        }
                        absolute_axis_index += 1
                        y_axis_side = "right" if y_axis_side == "left" else "left"
                    is_last_subplot = subplot_number == number_of_subplots
                    self.figure.layout[f"xaxis{x_axis_id}"] = {
                        "anchor": f"y{subplot_base_y_axis_id}",
                        "domain": [0.0, 1.0],
                        "matches": f"x{number_of_subplots}"
                        if subplot_number < number_of_subplots
                        else None,
                        "showticklabels": None if is_last_subplot else False,
                    }
                else:
                    warnings.warn(f"Subplot {subplot_number} is unused.")
            if not at_least_one_subplot:
                raise Exception("No time series data provided.")

            self.is_finalized = True

    def write_html_plot(self, path: Path) -> None:
        "Write plots to html file at specified path."
        self.finalize_plot()
        self.figure.write_html(path)


def get_subplot_domains(number_of_subplots: int, gap: float = 0.05) -> List[Tuple[float, float]]:
    """Calculate and return the 'Y' domain ranges for a given number of subplots with the specified gap size."""
    subplot_height = (1.0 - gap * (number_of_subplots - 1)) / number_of_subplots
    subplot_domains = []
    for subplot_number in range(number_of_subplots):
        subplot_bottom = subplot_number * (subplot_height + gap)
        subplot_top = subplot_bottom + subplot_height
        subplot_domains.append((subplot_bottom, subplot_top))

    subplot_domains.reverse()
    return subplot_domains
