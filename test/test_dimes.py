#pylint:disable=C0114

from dimes import TimeSeriesPlot, TimeSeriesData

def test_something():
    plot = TimeSeriesPlot([1,2,3,4,5])
    plot.add_time_series(TimeSeriesData([x**2 for x in plot.time_values]))
    plot.add_time_series(TimeSeriesData([x**3 for x in plot.time_values]))

    plot.write_html_plot("output.html")
