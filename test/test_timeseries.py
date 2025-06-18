# mypy: disable-error-code="operator, arg-type"

from pathlib import Path

import pytest

from dimes import DimensionalPlot, DisplayData, LineProperties, LinesOnly
from dimes.dimensional_plot import DimensionalAxis

TESTING_DIRECTORY = Path("test_outputs")
TESTING_DIRECTORY.mkdir(exist_ok=True)

TEST_AXIS: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]


def test_basic_plot():
    """Test basic plot"""
    plot = DimensionalPlot(TEST_AXIS, "Title Basic Plot")
    plot.add_display_data(DisplayData([x**2 for x in plot.x_axis.data_values]))
    plot.add_display_data(DisplayData([x**3 for x in plot.x_axis.data_values]))

    plot.write_html_plot(Path(TESTING_DIRECTORY, "basic_plot.html"))


def test_basic_subplot():
    """Test basic subplot"""
    plot = DimensionalPlot(TEST_AXIS)
    plot.add_display_data(DisplayData([x**2 for x in plot.x_axis.data_values]))
    plot.add_display_data(DisplayData([x**3 for x in plot.x_axis.data_values]), subplot_number=2)

    plot.write_html_plot(Path(TESTING_DIRECTORY, "basic_subplot.html"))


def test_empty_plot():
    """Expect an exception if no DisplayData added to a plot."""
    plot = DimensionalPlot(TEST_AXIS)

    with pytest.raises(Exception):
        plot.write_html_plot(Path(TESTING_DIRECTORY, "empty_plot.html"))


def test_plot_twice():
    """Ensure DisplayData objects are not added twice to plots."""
    plot = DimensionalPlot(TEST_AXIS)
    plot.add_display_data(DisplayData([x**2 for x in plot.x_axis.data_values]))
    plot.add_display_data(DisplayData([x**3 for x in plot.x_axis.data_values]))

    plot.write_html_plot(Path(TESTING_DIRECTORY, "plot_twice_1.html"))
    plot.write_html_plot(Path(TESTING_DIRECTORY, "plot_twice_2.html"))


def test_bad_units():
    """Expect an exception if no DisplayData added to a plot."""
    plot = DimensionalPlot(TEST_AXIS)
    with pytest.raises(Exception) as exception:
        plot.add_display_data(
            DisplayData(
                [x**2 for x in plot.x_axis.data_values],
                "Temperature",
                native_units="degF",
                display_units="C",
            )
        )

    assert "[current] * [time]" in str(exception)


def test_multi_plot():
    """Test multiple time series on multiple axes in multiple subplots."""
    plot = DimensionalPlot(TEST_AXIS)
    # Time series & axis names explicit, subplot default to 1
    plot.add_display_data(
        DisplayData(
            [x**2 for x in plot.x_axis.data_values],
            name="Power",
            native_units="hp",
            display_units="W",
            y_axis_name="Power or Capacity",
        )
    )
    # Time series name explicit, axis automatically determined by dimensionality, subplot default to 1
    plot.add_display_data(
        DisplayData([x * 10 for x in plot.x_axis.data_values], name="Capacity", native_units="kBtu/h", is_visible=False)
    )
    # Time series and axis will get name from dimensionality
    # subplot default to 1, new axis for new dimension on existing subplot
    plot.add_display_data(DisplayData([x for x in plot.x_axis.data_values], native_units="ft", display_units="cm"))  # type: ignore[misc]
    # Time series & axis names and subplot number are all explicit
    plot.add_display_data(
        DisplayData([x**3 for x in plot.x_axis.data_values], name="Number of Apples", y_axis_name="Quantity"),
        subplot_number=2,
    )
    # Time series and subplot number explicit, axis name automatically determined from time series name
    plot.add_display_data(
        DisplayData(
            [x**4 for x in plot.x_axis.data_values],
            name="Force",
            native_units="lbf",
        ),
        subplot_number=3,
    )

    plot.write_html_plot(Path(TESTING_DIRECTORY, "multi_plot.html"))


def test_basic_marker():
    """Test basic marker plot"""
    plot = DimensionalPlot(TEST_AXIS)
    plot.add_display_data(
        DisplayData(
            [x**2 for x in plot.x_axis.data_values],
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
    plot = DimensionalPlot(TEST_AXIS)
    plot.add_display_data(
        DisplayData(
            [x**2 for x in plot.x_axis.data_values],
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
    plot = DimensionalPlot(TEST_AXIS)
    city_data = {
        "City_A": {2000: [x**2 for x in plot.x_axis.data_values], 2010: [x**3 for x in plot.x_axis.data_values]},
        "City_B": {2000: [x**2.5 for x in plot.x_axis.data_values], 2010: [x**3.5 for x in plot.x_axis.data_values]},
    }
    for city, year_data in city_data.items():
        for year, data in year_data.items():
            plot.add_display_data(
                DisplayData(
                    data,
                    name=city,
                    legend_group=str(year),
                ),
            )
    plot.write_html_plot(Path(TESTING_DIRECTORY, "legend_group.html"))


def test_is_visible():
    """Test visibility of lines in plot and legend."""
    plot = DimensionalPlot(TEST_AXIS)
    plot.add_display_data(
        DisplayData(
            [x**2 for x in plot.x_axis.data_values],
            line_properties=LineProperties(
                color="blue", marker_size=5, marker_line_color="black", marker_fill_color="white", marker_line_width=1.5
            ),
            is_visible=True,
            name="Visible",
        )
    )
    plot.add_display_data(
        DisplayData(
            [x**3 for x in plot.x_axis.data_values],
            line_properties=LinesOnly(
                color="green",
                marker_size=5,
                marker_line_color="black",
                marker_fill_color="white",
            ),
            is_visible=False,
            name="Legend Only",
        )
    )
    plot.write_html_plot(Path(TESTING_DIRECTORY, "is_visible.html"))


def test_get_axis_range():
    checks: list[tuple[list[float], list[float]]] = [([0, 2], [0, 2]), ([0, 23.5], [0, 25])]

    for check in checks:
        min_value = check[0][0]
        max_value = check[0][1]
        assert DimensionalAxis.get_axis_range(min_value, max_value) == check[1]


def test_vertical_grid_lines():
    """Test basic subplot"""
    plot = DimensionalPlot(TEST_AXIS, vertical_grid_lines=True)
    plot.add_display_data(DisplayData([x**2 for x in plot.x_axis.data_values]))
    plot.add_display_data(DisplayData([x**3 for x in plot.x_axis.data_values]), subplot_number=2)
    plot.add_display_data(DisplayData([x**4 for x in plot.x_axis.data_values]), subplot_number=3)

    plot.write_html_plot(Path(TESTING_DIRECTORY, "vertical_grid_lines.html"))
