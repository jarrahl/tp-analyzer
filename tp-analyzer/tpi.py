from scipy.signal import savgol_filter
from sortedcontainers import SortedList
import numpy as np
from csv import DictReader
from collections import defaultdict
import matplotlib.pyplot as plt
import math
import sys

from utils import log_grad

SG_WINDOW_SIZE = 61
SG_POLY_ORDER = 2

# 0 = error only, 1 = verbose
DEBUG_LEVEL = 1
def debug(level, s):
  if level >= DEBUG_LEVEL:
    print(s)

# Return the MJ semi-metric distance between two sequences s1,s2
def element_to_set_distance(e, s):
  return min([abs(e-x) for x in s])
 
def set_to_set_distance(s1, s2):
  if len(s1) == 0 or len(s2) == 0:
    return float('inf')
  return 0.5 * (
    sum([element_to_set_distance(e, s2) for e in s1]) / len(s1) + \
    sum([element_to_set_distance(e, s1) for e in s2]) / len(s2))

def turning_point_set_distance(tps1, tps2):
  # assume both sets alternate T/P and start with T, P, ...
  if len(tps1) < 2 or len(tps2) < 2:
    return float('inf')
  return set_to_set_distance(tps1[0::2], tps2[0::2]) +  \
         set_to_set_distance(tps1[1::2], tps2[1::2])

# x_raw[] is time series (list) of reals, already smoothed.
def identifyTurningPoints(x_raw, local_radius=17, peak_ratio=0.2, min_log_grad=0.01):
  x = np.array(x_raw)
  x[x<0] = 0

  # preprocess: cache right-side peak/trough neighbourhood validity
  # valid_peak[i] = True iff x[i] >= max(x[i+1], x[i+2], ..., x[i+local_radius])
  # valid_trough[i] = True iff x[i] <= max(x[i+1], x[i+2], ..., x[i+local_radius])
  valid_peak = np.full((len(x)), False)
  valid_trough = np.full((len(x)), False)
  next_values = SortedList([x[-1]]) # ordered set of next 'local_radius' values
  valid_peak[-1] = True
  valid_trough[-1] = True
  for i in range(len(x)-2, -1, -1):
    valid_peak[i] = x[i] >= next_values[-1]
    valid_trough[i] = x[i] <= next_values[0]
    if i + local_radius < len(x):
      next_values.remove(x[i+local_radius])
    next_values.add(x[i])

  # For now, we assume index 0 is the first trough
  # TODO: generalise to search for first peak or trough
  tps = [0]
  recent_values = SortedList([x[0]]) # ordered set of last 'local_radius' values
  for i in range(1, len(x)):
    # update peak/trough validity based on left-side neighbourhood
    valid_peak[i] &= (x[i] >= recent_values[-1])
    valid_trough[i] &= (x[i] <= recent_values[0])

    if len(tps) % 2 == 1:
      # the last TP we addded was a trough (odd number of turning points)
      if x[i] < x[tps[-1]]:
        # replace last trough with this lower one.
        tps[-1] = i
      elif x[i] > x[tps[-1]] and \
           valid_peak[i] and \
           (len(tps) < 2 or x[i] >= x[tps[-2]] * peak_ratio) and \
           abs(log_grad(tps[-1], x[tps[-1]], i, x[i])) >= min_log_grad:
        # new peak: greater-or-equal to surrounding 'l' values and greater than 
        # previous trough and passes peak ratio check with prev peak and
        # log_grad ratio check with prev trough
        tps.append(i)
    else:
      # the last TP we added was a peak.
      if x[i] > x[tps[-1]]:
        # replace recent peak with this one.
        tps[-1] = i
      elif x[i] < x[tps[-1]] and \
           valid_trough[i] and \
           abs(log_grad(tps[-1], x[tps[-1]], i, x[i])) >= min_log_grad:
        # new trough: less-or-equal to surrounding 'l' values and less than
        # previous peak and passes log_grad ratio check with prev peak
        tps.append(i)
    if i >= local_radius:
      recent_values.remove(x[i-local_radius])
    recent_values.add(x[i])
  return tps

# Assumptions: once a state starts reporting, it reports exactly once every
# following day, and rows are ordered by ascending date.
def load_data(states, plot=True, generate_matrix=False, file='us-states.csv'):
  cumulative = defaultdict(lambda: [0])
  deltas = defaultdict(lambda: [0])
  with open(file) as csvfile:
    reader = DictReader(csvfile)
    for row in reader:
      cumulative[row['state']].append(int(row['cases']))
  deltas = dict([(x, [y[i] - y[i-1] for i in range(1, len(y))]) for (x, y) in cumulative.items()])

  tps = {}
  if not states:
    states = deltas.keys()
  plot_cols = math.floor(math.sqrt(len(states)))
  plot_rows = math.ceil(len(states) / plot_cols)
  for (i, state) in enumerate(states):
    smoothed = savgol_filter(deltas[state], 61, 2)
    smoothed[smoothed<0] = 0
    tps[state] = identifyTurningPoints(smoothed)
    print("Identified: ", [(x, smoothed[x]) for x in tps[state]])
    if plot:
      plt.subplot(plot_rows, plot_cols, i+1, title=state)
      plt.plot(deltas[state], color='c')
      plt.plot(smoothed, color='b')
      for (i, p) in enumerate(tps[state]):
        plt.axvline(x=p, color=['g', 'r'][i % 2])

  if generate_matrix:
    for a in tps:
      for b in tps:
        print(a, b, turning_point_set_distance(tps[a], tps[b]))
  if plot:
    plt.show()

if len(sys.argv) == 3 and sys.argv[1] == "load":
  load_data(sys.argv[2].split(","))
elif len(sys.argv) == 2 and sys.argv[1] == "matrix":
  load_data([], False, True)
  
else:
  print("Usage: %s load [comma-separated list of states]" % (sys.argv[0]))
