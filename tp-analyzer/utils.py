from math import log

def log_grad(x1, y1, x2, y2):
  if y2 <= 0:
    return float('-inf')
  if y1 <= 0 or x1 == x2:
    return float('inf')
  return (log(y2) - log(y1)) / (x2 - x1)
