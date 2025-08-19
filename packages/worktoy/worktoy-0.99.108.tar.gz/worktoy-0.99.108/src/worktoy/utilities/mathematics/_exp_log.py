"""
Provides the exponential function and natural logarithm
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import cos, sin, atan2

if TYPE_CHECKING:  # pragma: no cover
  from typing import Union


def _exp(z: float, f: float = 1.0) -> float:
  """Returns the exponential of z using the Taylor series expansion."""
  if z > 2:
    return _exp(z / 2, f * 2)
  if z < 0:
    return 1 / _exp(-z)
  shift = 1e16
  term = 1 / shift
  result = 1 / shift
  n = 1

  while abs(term) > 1e-48:
    term *= z / n
    result += term
    n += 1
  else:
    return (shift * result) ** f


def _e() -> float:
  """Returns the base of the natural logarithm."""
  return _exp(1)


e = _e()


def _log(x: Union[float, complex]) -> Union[float, complex]:
  if x ** 2 < 1e-16:
    raise ZeroDivisionError
  if x < 1:
    return -_log(1 / x)
  if x > e:
    return _log(x / e) + 1
  if (1 - x) ** 2 < 1e-32:
    return 0
  term = (x - 1) / x
  result = term
  n = 1

  while abs(term) > 1e-32:
    term *= (x - 1) / x
    result += term / (n + 1)
    n += 1
  else:
    return result


def exp(z: complex) -> complex:
  """Returns the exponential of a complex number."""
  if isinstance(z, (int, float)):
    return exp(z * (1.0 + 0j))
  r = _exp(z.real)
  return r * (cos(z.imag) + sin(z.imag) * 1j)


def log(z: complex, ) -> complex:
  z = complex(z)
  r = abs(z)
  t = atan2(z.imag, z.real)
  return _log(r) + t * 1j
