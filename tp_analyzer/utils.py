from math import log

def log_grad(x1, y1, x2, y2):
  if y2 <= 0:
    return float('-inf')
  if y1 <= 0 or x1 == x2:
    return float('inf')
  return (log(y2) - log(y1)) / (x2 - x1)

def element_to_set_distance(v, s):
  """Returns shortest distance of some value to any element of a set."""
  return min([abs(v-x) for x in s])
 
def set_to_set_distance(s1, s2):
  """Returns distance between two sets, as defined in original paper."""
  if len(s1) == 0 or len(s2) == 0:
    return float('inf')
  return 0.5 * (sum([element_to_set_distance(e, s2) for e in s1]) / len(s1) +
                sum([element_to_set_distance(e, s1) for e in s2]) / len(s2))

def turning_point_set_distance(tps1, tps2):
  """
  Returns distance between two sets of turning points. This is defined as the
  distance between the two sets of peaks plus the distance between the two
  sets of troughs.
  """
  # Assume both sets alternate T/P and start with T, P, ...
  if len(tps1) < 2 or len(tps2) < 2:
    return float('inf')
  return (set_to_set_distance(tps1[0::2], tps2[0::2]) +  
          set_to_set_distance(tps1[1::2], tps2[1::2]))
