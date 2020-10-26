import pytest

from tp_analyzer import identify_turning_points

def test_simple_turning_points():
  assert identify_turning_points([5, 2, 1, 2, 3, 2, 1, 2, 5], 3) == [2, 4, 6, 8]
  # increase 'l' to 4, the middle '3' becomes overshadowed by the '5's
  assert identify_turning_points([5, 2, 1, 2, 3, 2, 1, 2, 5], 4) == [2, 8]

def test_peak_is_local_maximum():
  # invalid peak 3 due to upcoming 4
  assert identify_turning_points([1, 2, 3, 0, 4], 2) == [3, 4]

def test_trough_is_local_minimum():
  # invalid trough 4 due to upcoming 3
  assert identify_turning_points([1, 6, 5, 4, 6, 3], 2) == [0, 1, 5]

def test_peak_ratio_constraint():
  assert identify_turning_points([50, 20, 10, 20, 50, 20, 1, 2, 3], 2) == [2, 4, 6]
