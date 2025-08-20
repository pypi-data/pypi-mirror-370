"""
This files provides mathematical constants used by the
'worktoy.utilities.mathematics' module.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  pass


def _arctanPi(z: float, shift: float = None, **kwargs) -> float:
  """Using Taylor series to compute arctan to compute pi."""
  if shift is None:
    shift = 1e12
  term = z
  result = z
  n = 1

  while abs(term) > kwargs.get('epsilon', 1e-32):
    term *= -z * z
    result += term / (2 * n + 1)
    n += 1
  else:
    return shift * result


def _pi() -> float:
  """Returns the value of pi."""
  out = 44 * _arctanPi(1 / 57)
  out += 7 * _arctanPi(1 / 239)
  out -= 12 * _arctanPi(1 / 682)
  return (4 * out + 96 * _arctanPi(1 / 12943)) * 1e-12


pi = _pi()


def _arctan(x: float) -> float:
  """Returns the arctangent of x using the Taylor series expansion."""
  return _arctanPi(x, shift=1, )


def _arcTanUnit(x: float) -> float:
  """
  Implements a Taylor series expansion for the arctangent function
  for values near 1.
  """

  result = pi / 4
  term = (x - 1) / (x + 1)
  w = (x - 1) / (x + 1)
  n = 1
  while abs(term) > 1e-32:
    result += term / (2 * n - 1)
    term *= -w ** 2
    n += 1
    if n > 100:  # pragma: no cover
      break
  else:
    return result
  raise RecursionError  # pragma: no cover


def arcTan(x: float) -> float:
  """
  Returns the arctangent of a complex number.
  Uses the Taylor series expansion for values near 1.
  """
  if abs(x) < 1e-16:
    return 0.0
  if abs(x - 1) < 1e-16:
    return pi / 4
  if abs(x - 1) < 0.5:
    return _arcTanUnit(x)
  if x < 0:
    return -arcTan(-x)
  if x > 1:
    return pi / 2 - arcTan(1 / x)
  return _arctan(x)


def atan2(y: float, x: float) -> float:
  """Returns the arctangent of y/x, handling the quadrant correctly."""
  if x > 0:
    return arcTan(y / x)
  if x < 0:
    if y >= 0:
      return arcTan(y / x) + pi
    else:
      return arcTan(y / x) - pi
  if y > 0:
    return pi / 2
  if y < 0:
    return -pi / 2
  return 0.0
