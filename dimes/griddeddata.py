"""For making plots of multi-dimensional gridded data."""

from copy import deepcopy
from csv import writer
from dataclasses import dataclass
from enum import Enum
from itertools import cycle
from itertools import product as cartesian_product
from typing import SupportsFloat

from koozie import convert

from .dimensional_plot import (
    COLOR_SCALE_SEQUENCE,
    DimensionalData,
    DimensionalPlot,
    DisplayData,
    LineProperties,
    add_units,
    get_color_from_scale,
)


class GridAxis(DimensionalData):
    pass


class GridPointData(DisplayData):
    pass


class AxisPlotType(Enum):
    X_AXIS = 0
    CONSTRAINED_AXIS = 1
    LEGEND_AXIS = 2


@dataclass
class DataSelection:
    """
    Class for selecting data to display in a chart
    """

    # TODO: Add color?

    name: str
    units: str | None = None
    precision: int = 2


@dataclass
class AxisConstraint:
    """
    Class for constraining an axis in a chart
    """

    selection: DataSelection
    value: float = 0.0  # Allow default for axis with one value


class RegularGridData:
    def __init__(self, grid_axes: list[GridAxis], grid_point_data_sets: list[GridPointData]) -> None:
        self.grid_axes = grid_axes
        self.grid_point_data_sets = grid_point_data_sets

        # Check sizes
        self.grid_axis_step_size = [0] * len(self.grid_axes)
        number_of_grid_points = 1
        for i, axis in enumerate(reversed(self.grid_axes)):
            i_reverse = len(self.grid_axes) - 1 - i
            self.grid_axis_step_size[i_reverse] = number_of_grid_points
            number_of_grid_points *= len(list(axis.data_values))

        for grid_point_data_set in self.grid_point_data_sets:
            size = len(list(grid_point_data_set.data_values))
            if size != number_of_grid_points:
                raise RuntimeError(
                    f"grid_point_data_set, {grid_point_data_set.name}, size ({size}) "
                    f"does not match size of grid, ({number_of_grid_points})."
                )

        # TODO: Make interpolator

    def get_grid_point_index(self, grid_indices: list[int] | tuple[int, ...]) -> int:
        index = 0
        for axis_index, point_index in enumerate(grid_indices):
            index += point_index * self.grid_axis_step_size[axis_index]
        return index

    def get_grid_point_indices(
        self,
        axis_indices: list[list[int]],  # For each axis, list the axis indices where data is requested
    ) -> list[
        int
    ]:  # Returns a list of indices into grid point data sets at the corresponding combinations of grid index values
        value_indices: list[int] = []
        for combination in cartesian_product(*axis_indices):
            value_indices.append(self.get_grid_point_index(combination))
        return value_indices

    def write_to_csv(self, output_path):
        grid_axes_indices = []
        header_row = []
        for grid_axis in self.grid_axes:
            grid_axes_indices.append(list(range(len(list(grid_axis.data_values)))))
            header_row.append(f"{grid_axis.name}{add_units(grid_axis.display_units)}")

        for grid_point_data_set in self.grid_point_data_sets:
            header_row.append(f"{grid_point_data_set.name}{add_units(grid_point_data_set.display_units)}")

        with open(output_path, "w", encoding="UTF-8") as csv_object:
            writer_object = writer(csv_object)
            writer_object.writerow(header_row)  # Header

            for combination in cartesian_product(*grid_axes_indices):
                content_row = []
                for i, grid_axis in enumerate(self.grid_axes):
                    content_row.append(list(grid_axis.data_values)[combination[i]])
                combination_index = self.get_grid_point_index(combination)
                for grid_point_data_set in self.grid_point_data_sets:
                    content_row.append(list(grid_point_data_set.data_values)[combination_index])
                writer_object.writerow(content_row)

    def make_plot(  # noqa: PLR0912 PLR0915
        self,
        x_grid_axis: DataSelection,  # Grid axis to use as the x-axis in the plot
        display_data: (
            list[DataSelection] | DataSelection | None
        ) = None,  # What grid point data to plot. Use None to plot all grid point data.
        legend_grid_axis: DataSelection | None = None,  # Name of grid axis to use in the legend of the plot
        constrained_grid_axes: list[AxisConstraint] | None = None,  # Constraints on axis not plotted
    ) -> DimensionalPlot:
        constrained_grid_axis_names: list[str] = []

        if constrained_grid_axes is None:
            constrained_grid_axes = []
        constrained_grid_axis_names = [axis.selection.name for axis in constrained_grid_axes]
        assert constrained_grid_axes is not None
        grid_axis_names = [axis.name for axis in self.grid_axes]
        grid_point_data_set_names = [data_set.name for data_set in self.grid_point_data_sets]

        # Initial Error checking
        if x_grid_axis.name in constrained_grid_axis_names:
            raise RuntimeError(f"x_grid_axis, {x_grid_axis.name}, cannot also be in constrained_grid_axes.")

        if x_grid_axis.name not in grid_axis_names:
            raise RuntimeError(f"x_grid_axis, {x_grid_axis.name}, not found.")

        if legend_grid_axis is not None:
            if legend_grid_axis.name == x_grid_axis.name:
                raise RuntimeError(f"legend_grid_axis, {legend_grid_axis.name}, cannot also be x_grid_axis.")

            if legend_grid_axis.name not in grid_axis_names:
                raise RuntimeError(f"legend_grid_axis, {legend_grid_axis.name}, not found.")

        if display_data is None:
            display_data = []
            assert display_data is not None
            for data_set in self.grid_point_data_sets:
                display_data.append(DataSelection(data_set.name, data_set.display_units))
        else:
            if isinstance(display_data, DataSelection):
                display_data = [display_data]
            assert not isinstance(display_data, DataSelection)
            for display_variable in display_data:
                if display_variable.name not in grid_point_data_set_names:
                    raise RuntimeError(f"display_data, {display_variable.name}, not found in grid_point_data_sets.")

        grid_point_data_set_indices: list[int] = []

        for display_variable in display_data:
            grid_point_data_set_indices.append(grid_point_data_set_names.index(display_variable.name))

        # All other axes are constrained
        referenced_axis_names = constrained_grid_axis_names + [x_grid_axis.name]
        if legend_grid_axis is not None:
            referenced_axis_names += [legend_grid_axis.name]

        for grid_axis in self.grid_axes:
            if grid_axis.name not in referenced_axis_names:
                grid_axis_values = list(grid_axis.data_values)
                mid_index = (len(grid_axis_values) - 1) // 2
                grid_axis_value = float(grid_axis_values[mid_index])
                constrained_grid_axes.append(
                    AxisConstraint(DataSelection(grid_axis.name, grid_axis.display_units), grid_axis_value)
                )
        constrained_grid_axis_names = [axis.selection.name for axis in constrained_grid_axes]

        axis_indices: list[list[int]] = [[] for _ in range(len(self.grid_axes))]
        legend_axis_index: int | None = None
        x_axis: GridAxis | None = None

        constraints_text: list[str] = []
        for i, grid_axis in enumerate(self.grid_axes):
            grid_axis_values = list(grid_axis.data_values)
            if grid_axis.name == x_grid_axis.name:
                axis_indices[i] = list(range(len(grid_axis_values)))
                x_axis = deepcopy(grid_axis)
                if x_grid_axis.units is None:
                    x_grid_axis.units = grid_axis.display_units
                x_axis.set_display_units(x_grid_axis.units)
            if legend_grid_axis is not None:
                if grid_axis.name == legend_grid_axis.name:
                    if legend_grid_axis.units is None:
                        legend_grid_axis.units = grid_axis.display_units
                    legend_axis_index = i
                    axis_indices[i] = list(range(len(grid_axis_values)))
            if grid_axis.name in constrained_grid_axis_names:
                for constrained_grid_axis in constrained_grid_axes:
                    selection = constrained_grid_axis.selection
                    if selection.units is None:
                        selection.units = grid_axis.display_units
                    value = constrained_grid_axis.value
                    if grid_axis.name == selection.name:
                        matching_value = (
                            value
                            if selection.units == grid_axis.native_units
                            else convert(value, selection.units, grid_axis.native_units)
                        )
                        matched_index, matched_value = find_index_of_nearest_value(grid_axis_values, matching_value)
                        axis_indices[i] = [matched_index]
                        if selection.units != grid_axis.native_units:
                            matched_value = convert(matched_value, grid_axis.native_units, selection.units)
                        constraints_text.append(
                            f"{selection.name} = {matched_value:.{selection.precision}f}{add_units(selection.units)}"
                        )

        # Create plot
        assert x_axis is not None
        plot = DimensionalPlot(
            x_axis, additional_info="<br>".join(constraints_text) if len(constrained_grid_axis_names) > 0 else None
        )

        if legend_grid_axis is not None:
            # Loop over legend axis values and add display data for each
            assert legend_axis_index is not None
            assert legend_grid_axis.units is not None
            grid_axis = self.grid_axes[legend_axis_index]
            legend_axis_indices = axis_indices[legend_axis_index]
            grid_axis_values = list(grid_axis.data_values)
            grid_axis_min = float(grid_axis_values[legend_axis_indices[0]])
            grid_axis_max = float(grid_axis_values[legend_axis_indices[-1]])
            color_scale_cycler = cycle(COLOR_SCALE_SEQUENCE)
            for grid_data_index, display_variable in enumerate(display_data):
                grid_point_data_set = self.grid_point_data_sets[grid_point_data_set_indices[grid_data_index]]
                grid_point_values = list(grid_point_data_set.data_values)
                color_scale = next(color_scale_cycler)
                for index in legend_axis_indices:
                    plot_axis_indices = deepcopy(axis_indices)
                    plot_axis_indices[legend_axis_index] = [index]
                    grid_point_indices = self.get_grid_point_indices(axis_indices=plot_axis_indices)
                    data_values = [grid_point_values[i] for i in grid_point_indices]
                    grid_axis_value = float(grid_axis_values[index])
                    grid_axis_ratio = (grid_axis_max - grid_axis_value) / (grid_axis_max - grid_axis_min)
                    line_color = get_color_from_scale(color_scale, grid_axis_ratio)
                    legend_axis_value = convert(grid_axis_value, grid_axis.native_units, legend_grid_axis.units)
                    plot.add_display_data(
                        DisplayData(
                            data_values,
                            name=f"{legend_grid_axis.name} = "
                            f"{legend_axis_value:.{legend_grid_axis.precision}f}{add_units(legend_grid_axis.units)}",
                            native_units=grid_point_data_set.native_units,
                            display_units=display_variable.units,
                            line_properties=LineProperties(color=line_color),
                            legend_group=f"{display_variable.name}",
                            y_axis_name=(
                                grid_point_data_set.name
                                if grid_point_data_set.y_axis_name is None
                                else grid_point_data_set.y_axis_name
                            ),
                        )
                    )
        else:
            grid_point_indices = self.get_grid_point_indices(axis_indices=axis_indices)
            for grid_data_index, display_variable in enumerate(display_data):
                grid_point_data_set = self.grid_point_data_sets[grid_point_data_set_indices[grid_data_index]]
                grid_point_values = list(grid_point_data_set.data_values)
                data_values = [grid_point_values[i] for i in grid_point_indices]
                plot.add_display_data(
                    DisplayData(
                        data_values,
                        name=display_variable.name,
                        native_units=grid_point_data_set.native_units,
                        display_units=display_variable.units,
                        y_axis_name=grid_point_data_set.y_axis_name,
                    )
                )

        return plot


def find_index_of_nearest_value(axis: list[SupportsFloat], value: SupportsFloat) -> tuple[int, SupportsFloat]:
    index = min(range(len(axis)), key=lambda i: abs(float(axis[i]) - float(value)))
    return index, axis[index]
