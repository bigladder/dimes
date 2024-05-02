"""For making plots of multi-dimensional gridded data."""

from typing import List, Union

from .common import DimensionalData, LineProperties


class GridAxis(DimensionalData):
    pass


class GridPointData(DimensionalData):
    pass


class RegularGridData:
    def __init__(
        self, grid_axes: List[GridAxis], grid_point_data_sets: List[GridPointData]
    ) -> None:
        self.grid_axes = grid_axes
        self.grid_point_data_sets = grid_point_data_sets

    def plot(
        self, grid_point_data_name, primary_grid_axis_name, constraints, output_path
    ):  # TODO: Add additional grid axes
        pass
