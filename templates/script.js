d3.csv('yahoo.csv')
  .row(function(d) {
    d.date = new Date(d.Timestamp * 1000);
    return d;
  })
  .get(function(error, rows) { renderChart(rows); });

function renderChart(data) {
  var chart = fc.chart.linearTimeSeries()
        .xDomain(fc.util.extent(data, 'date'))
        .yDomain(fc.util.extent(data, ['open', 'close']));

  var area = fc.series.area()
        .yValue(function(d) { return d.open; });

  chart.plotArea(area);

  d3.select('#time-series')
        .datum(data)
        .call(chart);
}
