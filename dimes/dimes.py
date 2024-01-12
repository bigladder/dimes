"""Module for plotting time series data."""
from pathlib import Path
from typing import List, Tuple, Union
import warnings

from plotly.graph_objects import Figure, Scatter  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
import koozie


class TimeSeriesData:
    """Time series data."""

    def __init__(
        self,
        data_values: list,
        name: Union[str, None] = None,
        native_units: str = "",
        display_units: Union[str, None] = None,
        dimension: Union[str, None] = None,
        color: Union[str, None] = None,
        line_type: Union[str, None] = None,
        is_visible: bool = True,
    ):
        self.data_values = data_values
        self.native_units = native_units
        self.dimensionality = koozie.get_dimensionality(self.native_units)
        self.name = name if name is not None else str(self.dimensionality)
        self.dimension = (
            dimension
            if dimension is not None
            else name
            if name is not None
            else str(self.dimensionality)
        )
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

    # TODO: Make use of multiple Y axes on a single subplot: https://plotly.com/python/multiple-axes/

    def __init__(self, time_series: TimeSeriesData) -> None:
        self.title = str(time_series.dimension)
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

    def add_time_series(self, time_series: TimeSeriesData) -> None:
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
        self.figure = Figure()
        self.time_values = time_values
        self.subplots: List[Union[TimeSeriesSubplot, None]] = [None]
        self.is_finalized = False

    def add_time_series(
        self, time_series: TimeSeriesData, subplot_number: Union[int, None] = None
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
        self.subplots[subplot_index].add_time_series(time_series)  # type: ignore[union-attr]

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
                                    mode="lines",
                                    visible="legendonly" if not time_series.is_visible else True,
                                    line={
                                        "color": time_series.color,
                                        "dash": time_series.line_type,
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
    subplot_height = (1.0 - gap) / number_of_subplots
    subplot_domains = []
    for subplot_number in range(number_of_subplots):
        subplot_bottom = subplot_number * (subplot_height + gap)
        subplot_top = subplot_bottom + subplot_height
        subplot_domains.append((subplot_bottom, subplot_top))

    subplot_domains.reverse()
    return subplot_domains
