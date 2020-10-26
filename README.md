# Turning Point Detection

This is a package for the paper https://arxiv.org/abs/2008.02068

## Usage

```
python -m tp_analyzer.us_covid_stats
```
Loads data from CSV included with the package, and produces plots for every
state in the folder 'state\_plots', turinng points in 'turning\_points.csv' and
a distance matrix between sequences of turning points in
'distance\_matrix.csv'.

```
$ python -m tp_analyzer.us_covid_stats --help
usage: us_covid_stats.py [-h] [--data DATA] [--states STATES]

Analyze turning points in US Covid time series data

optional arguments:
  -h, --help       show this help message and exit
  --data DATA      path to a CSV with 'state' and 'cases' fields
  --states STATES  comma-separated list of states to evaluate
```
