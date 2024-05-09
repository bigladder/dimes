"""Module for plotting time series data."""

from .common import DimensionalPlot, DisplayData
from typing import Union


class TimeSeriesData(DisplayData):
    """"""

    pass


class TimeSeriesPlot(DimensionalPlot):
    """Time series plot."""

    def __init__(self, time_values: list, title: Union[str, None] = None):
        super().__init__(time_values, title)
        self.add_time_series = self.add_display_data
        self.time_values = self.x_axis.data_values
