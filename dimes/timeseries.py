"""Module for plotting time series data."""

from .common import DimensionalPlot, DisplayData


class TimeSeriesData(DisplayData):
    """"""

    pass


class TimeSeriesPlot(DimensionalPlot):
    """Time series plot."""

    def __init__(self, time_values: list):
        super().__init__(time_values)
        self.add_time_series = self.add_display_data
        self.time_values = self.x_axis_values
