import dimes

plot = dimes.TimeSeriesPlot([1,2,3,4,5])
plot.add_time_series(dimes.TimeSeriesData([1,2,3,4,5]))

plot.write_html_plot("output.html")

