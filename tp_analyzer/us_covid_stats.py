import argparse
import pkg_resources
import os
from csv import DictReader
from collections import defaultdict
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

from .utils import turning_point_set_distance
from .identify_tps import identify_turning_points 

# Parameters for Savitzky-Golay filtering.
SG_WINDOW_SIZE = 61
SG_POLY_ORDER = 2

# Hard-coded output files, will parameretize these in future.
TP_OUTPUT_CSV = "turning_points.csv"
DISTANCE_MATRIX_OUTPUT_CSV = "distance_matrix.csv"
SURGE_REPORT_OUTPUT_TXT = "surge_report.txt"
PLOT_DIR = "state_plots"
PKG_DATA_FILE = "data/us-states.csv"

def process_data(file, states=[], plot_dir="", output_csv="", pad_zeroes=True):
  # Assumptions: once a state starts reporting, it reports exactly once every
  # following day, and rows are ordered by ascending date. We expect a field
  # called 'state' and a field called 'cases', which represents the cumulative
  # number of cases for that state/date.
  # If 'pad_zeroes' is true, insert a sequence of '0's before each state's 
  # first reported day, so that every sequence is the same length.
  cumulative = {}
  with open(file) as csvfile:
    reader = DictReader(csvfile)
    days = 0
    prevdate = None
    line = 0
    for row in reader:
      line += 1
      if ('date' not in row) or ('state' not in row) or ('cases' not in row):
        print("Error (line %d): data must contain 'date', 'state' and 'cases' fields." % (line))
        return
      if row['state'] not in cumulative:
        cumulative[row['state']] = [0] * (days if pad_zeroes else 0)
      cumulative[row['state']].append(int(row['cases']))
      if row['date'] != prevdate:
        if prevdate and row['date'] < prevdate:
          print("Error (line %d): dates must be in ascending order" % (line)) 
          return
        days += 1
        prevdate = row['date']
  deltas = dict([(x, [y[i] - y[i-1] for i in range(1, len(y))])
                 for (x, y) in cumulative.items()])
  tps = {}
  output_csv_file = open(output_csv, "w")
  nlines = 0

  # If states is empty, assume we want all states.
  if not states:
    states = deltas.keys()
  #plot_cols = math.floor(math.sqrt(len(states)))
  #plot_rows = math.ceil(len(states) / plot_cols)
  for (i, state) in enumerate(states):
    smoothed = savgol_filter(deltas[state], SG_WINDOW_SIZE, SG_POLY_ORDER)
    smoothed[smoothed<0] = 0
    tps[state] = identify_turning_points(smoothed)
    output_csv_file.write(
        state + "," + ",".join([str(x) for x in tps[state]]) + "\n")
    nlines += 1
    if plot_dir:
      #plt.subplot(plot_rows, plot_cols, i+1, title=state)
      plt.plot(deltas[state], color='c')
      plt.plot(smoothed, color='b')
      for (i, p) in enumerate(tps[state]):
        plt.axvline(x=p, color=['g', 'r'][i % 2])
      plot_filename = "%s/%s.png" % (plot_dir, state)
      plt.savefig(plot_filename)
      print("Wrote plot to %s" % (plot_filename))
      plt.clf()
  output_csv_file.close()
  print("Wrote %d lines to %s" % (nlines, output_csv))
  return tps

def generate_distance_matrix(tps, out=""):
  # tps is a dictionary keyed by state name, containing lists of turning
  # point indices.
  # out is a file name to write to. Empty string = print to stdout.
  f_out = open(out, "w") if out else sys.stdout
  nlines = 0
  for a in tps:
    for b in tps:
      nlines += 1
      f_out.write("%s,%s,%.2f\n" % 
                  (a, b, turning_point_set_distance(tps[a], tps[b])))
  f_out.close()
  print("Wrote %d lines to %s" % (nlines, out))

def generate_surge_report(tps, out=""):
  # tps is a dictionary keyed by state name, containing lists of turning
  # point indices.
  # out is a file name to write to. Empty string = print to stdout.
  states_by_tps_len = defaultdict(lambda: [])
  f_out = open(out, "w") if out else sys.stdout
  for (a, b) in tps.items():
    states_by_tps_len[len(b)].append(a)
  # special case tps_len=0/1
  for tps_len in sorted(states_by_tps_len.keys()):
    f_out.write(
      "%s surge %d:\n" % ("Over" if (tps_len % 2)  else "In", int(tps_len/2)))
    f_out.write("\n".join(states_by_tps_len[tps_len]) + "\n\n")


# Default usage: python -m tp_analyzer.us_covid_stats [data_file] [states]
# Produces distance_matrix.csv with (state, state, distance) triples
# Produces turning_points.csv with (state, turning_points...)
# Produces folder state_plots/ with .png for each state.
if __name__ == "__main__":
  argparser = argparse.ArgumentParser(
      description="Analyze turning points in US Covid time series data")
  argparser.add_argument("--data", default="",
                         help="path to a CSV with 'state' and 'cases' fields")
  argparser.add_argument("--states", default="",
                         help="comma-separated list of states to evaluate")
  args = argparser.parse_args()
  data_file = (args.data or pkg_resources.resource_filename(
      'tp_analyzer', PKG_DATA_FILE))
  states = [x.strip() for x in args.states.split(",")] if args.states else []

  try:
    os.mkdir(PLOT_DIR)
  except FileExistsError:
    pass
  except Exception as e:
    print("Failed to create %s directory." % (PLOT_DIR), e)
    exit()  
  tps = process_data(data_file, states, PLOT_DIR, TP_OUTPUT_CSV)
  generate_distance_matrix(tps, out=DISTANCE_MATRIX_OUTPUT_CSV)
  generate_surge_report(tps, out=SURGE_REPORT_OUTPUT_TXT)
