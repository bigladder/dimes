"""For making plots of multi-dimensional gridded data."""

from typing import List, Dict, Tuple, SupportsFloat
from enum import Enum
from pathlib import Path

from koozie import convert

from .common import DimensionalData, DisplayData, DimensionalPlot


class GridAxis(DimensionalData):
    pass


class GridPointData(DisplayData):
    pass


class AxisPlotType(Enum):
    X_AXIS = 0
    CONSTRAINED_AXIS = 1


class RegularGridData:
    def __init__(
        self, grid_axes: List[GridAxis], grid_point_data_sets: List[GridPointData]
    ) -> None:
        self.grid_axes = grid_axes
        self.grid_point_data_sets = grid_point_data_sets

        # Check sizes
        self.grid_axis_step_size = [0] * len(self.grid_axes)
        number_of_grid_points = 1
        for i, axis in enumerate(self.grid_axes):
            self.grid_axis_step_size[i] = number_of_grid_points
            number_of_grid_points *= len(axis.data_values)

        for grid_point_data_set in self.grid_point_data_sets:
            size = len(grid_point_data_set.data_values)
            if size != number_of_grid_points:
                raise RuntimeError(
                    f"grid_point_data_set, {grid_point_data_set.name}, size ({size}) does not match size of grid, ({number_of_grid_points})."
                )
        self.plot: DimensionalPlot

    def initialize_plot(
        self,
        grid_point_data_name: str,
        x_grid_axis_name: str,
        constraints: Dict[str, Tuple[float, str]],
        output_path: Path,
    ) -> None:  # TODO: Add additional grid axes

        # Check axes. Must either be x_grid_axis, or constrained.
        if x_grid_axis_name in constraints:
            raise RuntimeError(
                f"x_grid_axis_name, {x_grid_axis_name}, cannot also be in constraints."
            )

        # find grid point data name
        for i, grid_point_data_set in enumerate(self.grid_point_data_sets):
            if grid_point_data_set.name == grid_point_data_name:
                data_set_index = i
                break

        axis_references = [0] * len(self.grid_axes)
        axis_indices = [None] * len(self.grid_axes)
        axis_plot_type = [None] * len(self.grid_axes)

        for i, grid_axis in enumerate(self.grid_axes):
            if grid_axis.name == x_grid_axis_name:
                axis_references[i] += 1
                x_axis_index = i
                axis_indices = list(range(len(grid_axis.data_values)))
                axis_plot_type[i] = AxisPlotType.X_AXIS
            if grid_axis.name in constraints:
                axis_references[i] += 1
                # Determine nearest grid axis point index
                value = constraints[grid_axis.name][0]
                units = constraints[grid_axis.name][1]
                matching_value = (
                    value
                    if units == grid_axis.native_units
                    else convert(value, units, grid_axis.native_units)
                )
                axis_indices[i] = find_index_of_nearest_value(grid_axis.data_values, matching_value)
                axis_plot_type[i] = AxisPlotType.CONSTRAINED_AXIS

        # Build up display data
        # DisplayData()

        self.plot = DimensionalPlot(self.grid_axes[x_axis_index].data_values)
        self.plot.add_display_data(self.grid_point_data_sets[data_set_index])
        self.plot.write_html_plot(output_path)

    def get_grid_point_index(self, grid_indices: List[int]) -> int:
        index = 0
        for axis_index, point_index in enumerate(grid_indices):
            index += point_index * self.grid_axis_step_size[axis_index]
        return index


def find_index_of_nearest_value(
    axis: List[SupportsFloat], value: SupportsFloat
) -> Tuple[int, SupportsFloat]:
    index = min(range(len(axis)), key=lambda i: abs(axis[i] - value))
    return index, axis[index]
