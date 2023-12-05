# pylint:disable=C0114

import pytest
from dimes import TimeSeriesPlot, TimeSeriesData


def test_basic_plot():
    """Test basic plot"""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(TimeSeriesData([x**2 for x in plot.time_values]))
    plot.add_time_series(TimeSeriesData([x**3 for x in plot.time_values]))

    plot.write_html_plot("output.html")


def test_empty_plot():
    """Expect an exception if no TimeSeriesData added to a plot."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])

    with pytest.raises(Exception):
        plot.write_html_plot("output.html")


def test_plot_twice():
    """Ensure TimeSeriesData objects are not added twice to plots."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(TimeSeriesData([x**2 for x in plot.time_values]))
    plot.add_time_series(TimeSeriesData([x**3 for x in plot.time_values]))

    plot.write_html_plot("output.html")
    plot.write_html_plot("output2.html")
