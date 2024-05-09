# pylint:disable=C0114

from pathlib import Path
import pytest
from dimes import TimeSeriesPlot, TimeSeriesData, LineProperties, LinesOnly

TESTING_DIRECTORY = Path("test_outputs")
TESTING_DIRECTORY.mkdir(exist_ok=True)


def test_basic_plot():
    """Test basic plot"""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5], "Title Basic Plot")
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
    # Time series & axis names explicit, subplot default to 1
    plot.add_time_series(
        TimeSeriesData(
            [x**2 for x in plot.time_values], name="Power", native_units="hp", display_units="W"
        ),
        axis_name="Power or Capacity",
    )
    # Time series name explicit, axis automatically determined by dimensionality, subplot default to 1
    plot.add_time_series(
        TimeSeriesData(
            [x * 10 for x in plot.time_values],
            name="Capacity",
            native_units="kBtu/h",
            is_visible=False
        )
    )
    # Time series and axis will get name from dimensionality, subplot default to 1, new axis for new dimension on existing subplot
    plot.add_time_series(
        TimeSeriesData([x for x in plot.time_values], native_units="ft", display_units="cm")
    )
    # Time series & axis names and subplot number are all explicit
    plot.add_time_series(
        TimeSeriesData([x**3 for x in plot.time_values], name="Number of Apples"),
        subplot_number=2,
        axis_name="Quantity",
    )
    # Time series and subplot number explicit, axis name automatically determined from time series name
    plot.add_time_series(
        TimeSeriesData(
            [x**4 for x in plot.time_values],
            name="Force",
            native_units="lbf",
        ),
        subplot_number=3,
    )

    plot.write_html_plot(Path(TESTING_DIRECTORY, "multi_plot.html"))


def test_basic_marker():
    """Test basic marker plot"""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(
        TimeSeriesData(
            [x**2 for x in plot.time_values],
            line_properties=LineProperties(
                color="blue",
                marker_symbol="circle",
                marker_size=5,
                marker_line_color="black",
                marker_fill_color="white",
            ),
        )
    )
    plot.write_html_plot(Path(TESTING_DIRECTORY, "basic_marker.html"))


def test_missing_marker_symbol():
    """Test missing marker symbol, default symbol should be 'circle'."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(
        TimeSeriesData(
            [x**2 for x in plot.time_values],
            line_properties=LineProperties(
                color="blue",
                marker_size=5,
                marker_line_color="black",
                marker_fill_color="white",
            ),
        )
    )
    plot.write_html_plot(Path(TESTING_DIRECTORY, "missing_marker_symbol.html"))


def test_legend_group():
    """Test legend group and legend group title."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    city_data = {"City_A":{2000:[x**2 for x in plot.time_values],2010:[x**3 for x in plot.time_values]},
            "City_B":{2000:[x**2.5 for x in plot.time_values],2010:[x**3.5 for x in plot.time_values]}}
    for city, year_data in city_data.items():
        for year, data in year_data.items():
            plot.add_time_series(
                TimeSeriesData(
                    data,
                    name = city,
                    legend_group = str(year),
                ),

            )
    plot.write_html_plot(Path(TESTING_DIRECTORY, "legend_group.html"))


def test_is_visible():
    """Test visibility of lines in plot and legend."""
    plot = TimeSeriesPlot([1, 2, 3, 4, 5])
    plot.add_time_series(
        TimeSeriesData(
            [x**2 for x in plot.time_values],
            line_properties=LineProperties(
                color="blue",
                marker_size=5,
                marker_line_color="black",
                marker_fill_color="white",
                marker_line_width=1.5
            ),
            is_visible = True,
            name = "Visible"
        )
    )
    plot.add_time_series(
        TimeSeriesData(
            [x**3 for x in plot.time_values],
            line_properties=LinesOnly(
                color="green",
                marker_size=5,
                marker_line_color="black",
                marker_fill_color="white",
            ),
            is_visible = False,
            name = "Legend Only"
        )
    )
    plot.write_html_plot(Path(TESTING_DIRECTORY, "is_visible.html"))