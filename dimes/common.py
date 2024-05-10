from pathlib import Path
from typing import Union, Tuple, List, SupportsFloat
from collections.abc import Iterable
from dataclasses import dataclass
import warnings
from datetime import datetime
import math
import bisect

from plotly.graph_objects import Figure, Scatter  # type: ignore

import koozie

WHITE = "white"
BLACK = "black"
GREY = "rgba(128,128,128,0.3)"


@dataclass
class LineProperties:
    color: Union[str, None] = None
    line_type: Union[str, None] = None
    line_width: Union[SupportsFloat, None] = None
    marker_symbol: Union[str, None] = None
    marker_size: Union[SupportsFloat, None] = None
    marker_line_color: Union[str, None] = None
    marker_line_width: Union[SupportsFloat, None] = None
    marker_fill_color: Union[str, None] = None

    def get_line_mode(self):

        if self.line_width is None:
            has_lines = True
        elif self.line_width == 0:
            has_lines = False
        else:
            has_lines = True

        if self.marker_size is None:
            has_markers = True
        elif self.marker_size == 0:
            has_markers = False
        else:
            has_markers = True

        if has_lines and has_markers:
            return "lines+markers"
        if has_markers:
            return "markers"
        if has_lines:
            return "lines"
        return "lines+markers"


@dataclass
class MarkersOnly(LineProperties):
    line_width: Union[SupportsFloat, None] = 0


@dataclass
class LinesOnly(LineProperties):
    marker_size: Union[SupportsFloat, None] = 0


class DimensionalData:
    def __init__(
        self,
        data_values: Iterable[SupportsFloat],
        name: Union[str, None] = None,
        native_units: str = "",
        display_units: Union[str, None] = None,
    ):
        self.data_values = data_values
        self.native_units = native_units
        self.dimensionality = koozie.get_dimensionality(self.native_units)
        self.name = name if name is not None else str(self.dimensionality).title().replace("[", "").replace("]", "")
        self.set_display_units(display_units)

    def set_display_units(self, units: Union[str, None] = None) -> None:
        """Set the display units for this axis"""
        if units is None:
            self.display_units = self.native_units
        else:
            self.display_units = units
            display_units_dimensionality = koozie.get_dimensionality(self.display_units)
            if self.dimensionality != display_units_dimensionality:
                raise RuntimeError(
                    f"display_units, {self.display_units}, dimensionality ({display_units_dimensionality}) does not match native_units, {self.native_units}, dimensionality ({self.dimensionality})"
                )


class TimeSeriesAxis:
    def __init__(
        self,
        data_values: Iterable[datetime],
        name: str = "Time",
    ):
        self.data_values = data_values
        self.name = name


class DisplayData(DimensionalData):
    """Data used for display."""

    def __init__(
        self,
        data_values: Iterable[SupportsFloat],
        name: Union[str, None] = None,
        native_units: str = "",
        display_units: Union[str, None] = None,
        line_properties: LineProperties = LineProperties(),
        is_visible: bool = True,
        legend_group: Union[str, None] = None,
        x_axis: Union[DimensionalData, TimeSeriesAxis, List[SupportsFloat], List[datetime], None] = None,
        y_axis_min: Union[SupportsFloat, None] = 0.0,
    ):
        super().__init__(data_values, name, native_units, display_units)
        self.x_axis: Union[DimensionalData, TimeSeriesAxis, None]
        if isinstance(x_axis, list):
            if isinstance(x_axis[0], datetime):
                self.x_axis = TimeSeriesAxis(x_axis)  # type: ignore[arg-type]
            else:
                self.x_axis = DimensionalData(x_axis)  # type: ignore[arg-type]
        else:
            self.x_axis = x_axis
        self.y_axis_min = y_axis_min
        self.line_properties = line_properties
        self.is_visible = is_visible
        self.legend_group = legend_group


class DimensionalAxis:
    """Dimensional 'Y' axis. May contain multiple `DisplayData` objects."""

    def __init__(self, display_data: DisplayData, name: Union[str, None]) -> None:
        self.name = name
        self.units = display_data.display_units
        self.dimensionality = display_data.dimensionality
        self.display_data_set: List[DisplayData] = [display_data]
        self.range_min: SupportsFloat = float("inf")
        self.range_max: SupportsFloat = -float("inf")

    def get_axis_label(self) -> str:
        """Make the string that appears as the axis label"""
        return f"{self.name} [{self.units}]"

    @staticmethod
    def get_axis_range(value_min, value_max):
        max_ticks = 6
        tick_scale_options = [1, 2, 5, 10]

        value_range = value_max - value_min
        min_tick_size = value_range / max_ticks
        magnitude = 10 ** math.floor(math.log(min_tick_size, 10))
        residual = min_tick_size / magnitude
        tick_size = (
            tick_scale_options[bisect.bisect_right(tick_scale_options, residual)] if residual < 10 else 10
        ) * magnitude
        range_min = math.floor(value_min / tick_size) * tick_size
        range_max = math.ceil(value_max / tick_size) * tick_size
        return [range_min, range_max]


class DimensionalSubplot:
    """Dimensional subplot. May contain multiple `DimensionalAxis` objects."""

    def __init__(self) -> None:
        self.axes: List[DimensionalAxis] = []

    def add_display_data(self, display_data: DisplayData, axis_name: Union[str, None] = None) -> None:
        """Add `DisplayData` to an axis"""
        if axis_name is not None:
            # Add display data to existing axis of the same name if it exists
            for axis in self.axes:
                if axis.name == axis_name:
                    self.add_display_data_to_existing_axis(display_data, axis)
                    return
        else:
            # Add display data to existing axis of the dimensionality if it exists
            for axis in self.axes:
                if axis.dimensionality == display_data.dimensionality:
                    self.add_display_data_to_existing_axis(display_data, axis)
                    return
            axis_name = display_data.name

        # Otherwise, make a new axis
        self.axes.append(DimensionalAxis(display_data, axis_name))

    def add_display_data_to_existing_axis(self, axis_data: DisplayData, axis: DimensionalAxis) -> None:
        """Add `DisplayData` to an existing `DimensionalAxis`"""
        # Update axis data display units to match the axis
        axis_data.set_display_units(axis.units)
        axis.display_data_set.append(axis_data)


class DimensionalPlot:
    """Plot of dimensional data."""

    def __init__(
        self,
        x_axis: Union[DimensionalData, TimeSeriesAxis, List[SupportsFloat], List[datetime]],
        title: Union[str, None] = None,
    ):
        self.figure = Figure()
        self.x_axis: Union[DimensionalData, TimeSeriesAxis]
        if isinstance(x_axis, list):
            if isinstance(x_axis[0], datetime):
                self.x_axis = TimeSeriesAxis(x_axis)  # type: ignore[arg-type]
            else:
                self.x_axis = DimensionalData(x_axis)  # type: ignore[arg-type]
        else:
            self.x_axis = x_axis
        self.subplots: List[Union[DimensionalSubplot, None]] = [None]
        self.is_finalized = False
        self.figure.layout["title"] = title

    def add_display_data(
        self,
        display_data: DisplayData,
        subplot_number: Union[int, None] = None,
        axis_name: Union[str, None] = None,
    ) -> None:
        """Add a DisplayData object to the plot."""
        if subplot_number is None:
            # Default case
            subplot_number = len(self.subplots)
        else:
            if subplot_number > len(self.subplots):
                # Make enough empty subplots
                self.subplots += [None] * (subplot_number - len(self.subplots))
        subplot_index = subplot_number - 1
        if self.subplots[subplot_index] is None:
            self.subplots[subplot_index] = DimensionalSubplot()
        self.subplots[subplot_index].add_display_data(display_data, axis_name)  # type: ignore[union-attr]

    def finalize_plot(self):
        """Once all DisplayData objects have been added, generate plot and subplots."""
        if not self.is_finalized:
            grid_line_width = 1.5
            at_least_one_subplot = False
            number_of_subplots = len(self.subplots)
            subplot_domains = get_subplot_domains(number_of_subplots)
            absolute_axis_index = 0  # Used to track axes data in the plot
            self.figure.layout["plot_bgcolor"] = WHITE
            self.figure.layout["font_color"] = BLACK
            self.figure.layout["title_x"] = 0.5
            xy_common_axis_format = {
                "mirror": True,
                "linecolor": BLACK,
                "linewidth": grid_line_width,
                "zeroline": False,
            }
            x_axis_label = f"{self.x_axis.name}"
            if isinstance(self.x_axis, DimensionalData):
                x_axis_label += f" [{self.x_axis.display_units}]"
            for subplot_index, subplot in enumerate(self.subplots):
                subplot_number = subplot_index + 1
                x_axis_id = subplot_number
                subplot_base_y_axis_id = absolute_axis_index + 1
                if subplot is not None:
                    y_axis_side = "left"
                    for axis_number, axis in enumerate(subplot.axes):
                        y_axis_id = absolute_axis_index + 1
                        for display_data in axis.display_data_set:
                            at_least_one_subplot = True
                            y_values = koozie.convert(
                                display_data.data_values,
                                display_data.native_units,
                                axis.units,
                            )
                            axis.range_min = min(min(y_values), axis.range_min)
                            if display_data.y_axis_min is not None:
                                data_y_axis_min = koozie.convert(
                                    display_data.y_axis_min, display_data.native_units, axis.units
                                )
                                axis.range_min = min(data_y_axis_min, axis.range_min)
                            axis.range_max = max(max(y_values), axis.range_max)
                            if display_data.x_axis is None:
                                if isinstance(display_data.x_axis, DimensionalData):
                                    x_axis_values = koozie.convert(
                                        self.x_axis.data_values, self.x_axis.native_units, self.x_axis.display_units
                                    )
                                else:
                                    x_axis_values = self.x_axis.data_values
                            else:
                                if isinstance(display_data.x_axis, DimensionalData) and isinstance(
                                    self.x_axis, DimensionalData
                                ):
                                    x_axis_values = koozie.convert(
                                        display_data.x_axis.data_values,
                                        display_data.x_axis.native_units,
                                        self.x_axis.display_units,
                                    )
                                elif isinstance(display_data.x_axis, TimeSeriesAxis) and isinstance(
                                    self.x_axis, TimeSeriesAxis
                                ):
                                    x_axis_values = display_data.x_axis.data_values
                                else:
                                    raise RuntimeError(
                                        f"DispalyData x-axis, {display_data.x_axis.name}, and Plot x-axis, {self.x_axis.name}, must both be DimensionalData or TimeSeriesAxes."
                                    )
                            self.figure.add_trace(
                                Scatter(
                                    x=x_axis_values,
                                    y=y_values,
                                    name=display_data.name,
                                    yaxis=f"y{y_axis_id}",
                                    xaxis=f"x{x_axis_id}",
                                    mode=display_data.line_properties.get_line_mode(),
                                    visible=("legendonly" if not display_data.is_visible else True),
                                    line={
                                        "color": display_data.line_properties.color,
                                        "dash": display_data.line_properties.line_type,
                                        "width": display_data.line_properties.line_width,
                                    },
                                    marker={
                                        "size": display_data.line_properties.marker_size,
                                        "color": display_data.line_properties.marker_fill_color,
                                        "symbol": display_data.line_properties.marker_symbol,
                                        "line": {
                                            "color": display_data.line_properties.marker_line_color,
                                            "width": display_data.line_properties.marker_line_width,
                                        },
                                    },
                                    legendgroup=display_data.legend_group,
                                    legendgrouptitle={"text": display_data.legend_group},
                                ),
                            )
                        is_base_y_axis = subplot_base_y_axis_id == y_axis_id
                        self.figure.layout[f"yaxis{y_axis_id}"] = {
                            "title": axis.get_axis_label(),
                            "domain": (subplot_domains[subplot_index] if subplot_base_y_axis_id == y_axis_id else None),
                            "side": y_axis_side,
                            "anchor": f"x{x_axis_id}",
                            "overlaying": (f"y{subplot_base_y_axis_id}" if not is_base_y_axis else None),
                            "tickmode": "sync" if not is_base_y_axis else None,
                            "autoshift": True if axis_number > 1 else None,
                            "showgrid": True,
                            "gridcolor": GREY,
                            "gridwidth": grid_line_width,
                            "range": axis.get_axis_range(axis.range_min, axis.range_max),
                        }
                        self.figure.layout[f"yaxis{y_axis_id}"].update(xy_common_axis_format)
                        absolute_axis_index += 1
                        y_axis_side = "right" if y_axis_side == "left" else "left"
                    is_last_subplot = subplot_number == number_of_subplots
                    self.figure.layout[f"xaxis{x_axis_id}"] = {
                        "title": x_axis_label if is_last_subplot else None,
                        "anchor": f"y{subplot_base_y_axis_id}",
                        "domain": [0.0, 1.0],
                        "matches": (f"x{number_of_subplots}" if subplot_number < number_of_subplots else None),
                        "showticklabels": None if is_last_subplot else False,
                        "ticks": None if not is_last_subplot else "outside",
                        "tickson": None if not is_last_subplot else "boundaries",
                        "tickcolor": None if not is_last_subplot else BLACK,
                        "tickwidth": None if not is_last_subplot else grid_line_width,
                    }
                    self.figure.layout[f"xaxis{x_axis_id}"].update(xy_common_axis_format)
                else:
                    warnings.warn(f"Subplot {subplot_number} is unused.")
            if not at_least_one_subplot:
                raise RuntimeError("No display data provided.")

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
