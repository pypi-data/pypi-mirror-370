# TimeSeries (class TimeSeriesWidget)

- This notebook purpose is to visualize Mascope database data in one Figure for long period of time.
- As a _Default_ NO time aggregation method is used and long-time series is plotted.
- User can aggregate time by 'Diurnal cycle', Hourly', 'Daily', 'Weekly' or 'Monthly'.
- Under **Figure settings**:
  - From **Select legend column for scatterplot** user can specify to use _target_compound_formula_, _target_compound_name_ or combination of those (_trace_name_) as a legend for sub-selecting traces.
  - Select between 'median' or 'mean' for time aggregation (_Default_: 'mean').
  - Check to **Add line to scatter plot** will add line between same trace scatter points in figure (_Default_: True).
  - Check to **Add trend line to scatterplot** will add _Ordinary Least Squares (OLS)_ -trendline between same trace scatter points in figure (_Default_: True).
- Changes in widgets takes effect from **Update figure(s)** -button.
