from pathlib import Path
from typing import Union, List, Tuple
from dataclasses import dataclass
import warnings


from plotly.graph_objects import Figure, Scatter  # type: ignore

import koozie


@dataclass
class LineProperties:
    color: Union[str, None] = None
    line_type: Union[str, None] = None
    marker_symbol: Union[str, None] = None
    marker_size: Union[int, None] = None
    marker_line_color: Union[str, None] = None
    marker_fill_color: Union[str, None] = None
    is_visible: bool = True

    def get_line_mode(self):
        if all(
            variables is None
            for variables in (
                self.marker_size,
                self.marker_symbol,
                self.marker_line_color,
                self.marker_fill_color,
            )
        ):
            return "lines"
        else:
            return "lines+markers"


class DimensionalData:
    def __init__(
        self,
        data_values: list,
        name: Union[str, None] = None,
        native_units: str = "",
        display_units: Union[str, None] = None,
    ):
        self.data_values = data_values
        self.native_units = native_units
        self.dimensionality = koozie.get_dimensionality(self.native_units)
        self.name = (
            name
            if name is not None
            else str(self.dimensionality).title().replace("[", "").replace("]", "")
        )
        self.set_display_units(display_units)

    def set_display_units(self, units: Union[str, None] = None) -> None:
        """Set the display units for this axis"""
        if units is None:
            self.display_units = self.native_units
        else:
            self.display_units = units
            display_units_dimensionality = koozie.get_dimensionality(self.display_units)
            if self.dimensionality != display_units_dimensionality:
                raise Exception(
                    f"display_units, {self.display_units}, dimensionality ({display_units_dimensionality}) does not match native_units, {self.native_units}, dimensionality ({self.dimensionality})"
                )


class DisplayData(DimensionalData):
    """Data used for display."""

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


class DimensionalAxis:
    """Dimensional 'Y' axis. May contain multiple `DisplayData` objects."""

    def __init__(self, display_data: DisplayData, name: Union[str, None]) -> None:
        self.name = name
        self.units = display_data.display_units
        self.dimensionality = display_data.dimensionality
        self.display_data_set: List[DisplayData] = [display_data]

    def get_axis_label(self) -> str:
        """Make the string that appears as the axis label"""
        return f"{self.name} [{self.units}]"


class DimensionalSubplot:
    """Dimensional subplot. May contain multiple `DimensionalAxis` objects."""

    def __init__(self) -> None:
        self.axes: List[DimensionalAxis] = []

    def add_display_data(
        self, display_data: DisplayData, axis_name: Union[str, None] = None
    ) -> None:
        """Add `TimeSeriesData` to an axis"""
        if axis_name is not None:
            # Add time series to existing axis of the same name if it exists
            for axis in self.axes:
                if axis.name == axis_name:
                    self.add_display_data_to_existing_axis(display_data, axis)
                    return
        else:
            # Add time series to existing axis of the dimensionality if it exists
            for axis in self.axes:
                if axis.dimensionality == display_data.dimensionality:
                    self.add_display_data_to_existing_axis(display_data, axis)
                    return
            axis_name = display_data.name

        # Otherwise, make a new axis
        self.axes.append(DimensionalAxis(display_data, axis_name))

    def add_display_data_to_existing_axis(
        self, axis_data: DisplayData, axis: DimensionalAxis
    ) -> None:
        """Add `DisplayData` to an existing `DimensionalAxis`"""
        # Update axis data display units to match the axis
        axis_data.set_display_units(axis.units)
        axis.display_data_set.append(axis_data)


class DimensionalPlot:
    """Plot of dimensional data."""

    def __init__(self, x_axis_values: list):
        self.figure = Figure()
        self.x_axis_values = x_axis_values
        self.subplots: List[Union[DimensionalSubplot, None]] = [None]
        self.is_finalized = False
        self.LINE_WIDTH = 1.5
        self.WHITE = "white"
        self.BLACK = "black"
        self.GREY = "rgba(128,128,128,0.3)"
        self.RANGE_BUFFER = 0.1


    def add_display_data(
        self,
        display_data: DisplayData,
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
            self.subplots[subplot_index] = DimensionalSubplot()
        self.subplots[subplot_index].add_display_data(display_data, axis_name)  # type: ignore[union-attr]
    
    def append_y_values_range(self, y_values):
        self.y_range["min"].append(min(y_values))
        self.y_range["max"].append(max(y_values))
    
    def get_axis_range(self, values):
        min_value = min(values["min"])
        max_value = max(values["max"])
        range_values = max_value - min_value
        return [min_value - range_values*self.RANGE_BUFFER, max_value + range_values*self.RANGE_BUFFER]


    def finalize_plot(self):
        """Once all TimeSeriesData objects have been added, generate plot and subplots."""
        if not self.is_finalized:
            at_least_one_subplot = False
            number_of_subplots = len(self.subplots)
            subplot_domains = get_subplot_domains(number_of_subplots)
            absolute_axis_index = 0  # Used to track axes data in the plot
            self.figure.layout["plot_bgcolor"] = self.WHITE
            self.figure.layout["font_color"] = self.BLACK
            self.figure.layout["title_x"] = 0.5
            for subplot_index, subplot in enumerate(self.subplots):
                subplot_number = subplot_index + 1
                x_axis_id = subplot_number
                subplot_base_y_axis_id = absolute_axis_index + 1
                if subplot is not None:
                    y_axis_side = "left"
                    for axis_number, axis in enumerate(subplot.axes):
                        y_axis_id = absolute_axis_index + 1
                        self.y_range: dict = {"min":[],"max":[]}
                        for display_data in axis.display_data_set:
                            at_least_one_subplot = True
                            y_values = koozie.convert(
                                        display_data.data_values,
                                        display_data.native_units,
                                        axis.units,
                                    )
                            self.append_y_values_range(y_values)
                            self.figure.add_trace(
                                Scatter(
                                    x=self.x_axis_values,
                                    y=y_values,
                                    name=display_data.name,
                                    yaxis=f"y{y_axis_id}",
                                    xaxis=f"x{x_axis_id}",
                                    mode=display_data.line_properties.get_line_mode(),
                                    visible=(
                                        "legendonly"
                                        if not display_data.line_properties.is_visible
                                        else True
                                    ),
                                    line={
                                        "color": display_data.line_properties.color,
                                        "dash": display_data.line_properties.line_type,
                                    },
                                    marker={
                                        "size": display_data.line_properties.marker_size,
                                        "color": display_data.line_properties.marker_fill_color,
                                        "symbol": display_data.line_properties.marker_symbol,
                                        "line": {
                                            "color": display_data.line_properties.marker_line_color,
                                            "width": 2,
                                        },
                                    },
                                ),
                            )
                        is_base_y_axis = subplot_base_y_axis_id == y_axis_id
                        self.figure.layout[f"yaxis{y_axis_id}"] = {
                            "title": axis.get_axis_label(),
                            "domain": (
                                subplot_domains[subplot_index]
                                if subplot_base_y_axis_id == y_axis_id
                                else None
                            ),
                            "side": y_axis_side,
                            "anchor": f"x{x_axis_id}",
                            "overlaying": (
                                f"y{subplot_base_y_axis_id}" if not is_base_y_axis else None
                            ),
                            "tickmode": "sync" if not is_base_y_axis else None,
                            "autoshift": True if axis_number > 1 else None,
                            "mirror": True,
                            "linecolor":self.BLACK,
                            "linewidth":self.LINE_WIDTH,
                            "showgrid":True,
                            "gridcolor":self.GREY,
                            "gridwidth":self.LINE_WIDTH,
                            "zeroline":True,
                            "zerolinecolor":self.GREY,
                            "zerolinewidth":self.LINE_WIDTH,
                            "range":self.get_axis_range(self.y_range)

                        }
                        absolute_axis_index += 1
                        y_axis_side = "right" if y_axis_side == "left" else "left"
                    is_last_subplot = subplot_number == number_of_subplots
                    self.figure.layout[f"xaxis{x_axis_id}"] = {
                        "anchor": f"y{subplot_base_y_axis_id}",
                        "domain": [0.0, 1.0],
                        "matches": (
                            f"x{number_of_subplots}"
                            if subplot_number < number_of_subplots
                            else None
                        ),
                        "showticklabels": None if is_last_subplot else False,
                        "ticks":"outside",
                        "tickson":"boundaries",
                        "tickcolor":self.BLACK,
                        "tickwidth":self.LINE_WIDTH,
                        "mirror": True,
                        "linecolor":self.BLACK,
                        "linewidth":self.LINE_WIDTH,
                        "zeroline":True,
                        "zerolinecolor":self.GREY,
                        "zerolinewidth":self.LINE_WIDTH,
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
