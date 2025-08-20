"""
This file is part of WorkToy.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.utilities.mathematics import pi

if TYPE_CHECKING:  # pragma: no cover
  from typing import Union


def _sin(x: complex, h: bool = None) -> Union[float, complex]:
  """Returns the sine of x."""
  x = x + 0j
  term = x
  result = x
  n = 1
  while abs(term) > 1e-32:
    term *= (1 if h else -1) * x * x / ((2 * n) * (2 * n + 1))
    result += term
    n += 1
  else:
    return result


def _cos(x: complex, h: bool = None) -> Union[float, complex]:
  """Returns the cosine of x."""
  x = x + 0j
  term = 1
  result = 1
  n = 1
  while abs(term) > 1e-32:
    term *= (1 if h else -1) * x * x / ((2 * n - 1) * (2 * n))
    result += term
    n += 1
  else:
    return result


def cos(x: complex) -> Union[float, complex]:
  """Returns the cosine of x."""
  if abs(x) < 1e-32:
    return 1.
  # if isinstance(x, (float, int)):
  #   if x < 0:
  #     return cos(-x)
  #   if x > pi:
  #     return -cos(x - pi)
  #   if x > pi / 2:
  #     return -cos(pi - x)
  return _cos(x, )


def sin(x: complex) -> Union[float, complex]:
  """Returns the sine of x."""
  if abs(x) < 1e-32:
    return .0
  # if isinstance(x, (float, int)):
  #   if x > 2 * pi:
  #     return sin(x - 2 * pi)
  #   if x < 2 * pi:
  #     return sin(x + 2 * pi)
  #   if x < 0:
  #     return -sin(-x)
  #   if x > pi / 2:
  #     return sin(pi - x)
  return _sin(x, )


def sinh(x: complex) -> Union[float, complex]:
  """Returns the hyperbolic sine of x."""
  return _sin(x, h=True)


def cosh(x: complex) -> Union[float, complex]:
  """Returns the hyperbolic cosine of x."""
  return _cos(x, h=True)


def tan(x: complex) -> Union[float, complex]:
  """Returns the tangent of x."""
  if abs(x) < 1e-16:
    return 0
  if abs(pi - 2 * x) < 1e-16:
    raise ZeroDivisionError
  sinX = _sin(x)
  cosX = _cos(x)
  return sinX / cosX


def tanh(x: complex) -> Union[float, complex]:
  """Returns the hyperbolic tangent of x."""
  if abs(x) < 1e-32:
    return 0
  return sinh(x) / cosh(x)
