## cdf 

### Fixed

- When deploying datapoints subscriptions and specifying timeseries IDs,
Toolkit now correctly splits request such that you can have up to 10,000
timeseries IDs in one subscription. Before you could only have the
request limit which is 100 timeseries IDs.

## templates

No changes.