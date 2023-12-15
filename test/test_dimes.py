# pylint:disable=C0114

from pathlib import Path
import pytest
from dimes import TimeSeriesPlot, TimeSeriesData

TESTING_DIRECTORY = Path("test_outputs")
TESTING_DIRECTORY.mkdir(exist_ok=True)


def test_basic_plot():
    """Test basic plot"""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(TimeSeriesData([x**2 for x in plot.time_values]))
    plot.add_time_series(TimeSeriesData([x**3 for x in plot.time_values]))

    plot.write_html_plot(Path(TESTING_DIRECTORY, "basic_plot.html"))


def test_basic_subplot():
    """Test basic subplot"""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(TimeSeriesData([x**2 for x in plot.time_values]))
    plot.add_time_series(TimeSeriesData([x**3 for x in plot.time_values]), subplot_number=2)

    plot.write_html_plot(Path(TESTING_DIRECTORY, "basic_subplot.html"))


def test_empty_plot():
    """Expect an exception if no TimeSeriesData added to a plot."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])

    with pytest.raises(Exception):
        plot.write_html_plot(Path(TESTING_DIRECTORY, "empty_plot.html"))


def test_plot_twice():
    """Ensure TimeSeriesData objects are not added twice to plots."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(TimeSeriesData([x**2 for x in plot.time_values]))
    plot.add_time_series(TimeSeriesData([x**3 for x in plot.time_values]))

    plot.write_html_plot(Path(TESTING_DIRECTORY, "plot_twice_1.html"))
    plot.write_html_plot(Path(TESTING_DIRECTORY, "plot_twice_2.html"))


def test_bad_units():
    """Expect an exception if no TimeSeriesData added to a plot."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    with pytest.raises(Exception) as exception:
        plot.add_time_series(
            TimeSeriesData(
                [x**2 for x in plot.time_values],
                "Temperature",
                native_units="degF",
                display_units="C",
            )
        )

    assert "[current] * [time]" in str(exception)


def test_multi_plot():
    """Test multiple time series on multiple axes in multiple subplots."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(
        TimeSeriesData(
            [x**2 for x in plot.time_values], name="Power", native_units="hp", display_units="W"
        )
    )
    plot.add_time_series(
        TimeSeriesData([x * 10 for x in plot.time_values], name="Capacity", native_units="kBtu/h")
    )
    # TODO: Enable multiple axes on the same subplot
    # plot.add_time_series(
    #     TimeSeriesData(
    #         [x for x in plot.time_values], name="Distance", native_units="ft", display_units="cm"
    #     )
    # )
    plot.add_time_series(TimeSeriesData([x**3 for x in plot.time_values]), subplot_number=2)

    plot.write_html_plot(Path(TESTING_DIRECTORY, "multi_plot.html"))
