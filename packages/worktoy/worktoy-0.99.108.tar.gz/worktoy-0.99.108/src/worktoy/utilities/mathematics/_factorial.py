"""
The 'factorial' function computes the factorial of a non-negative integer.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations


def factorial(n: int, c: int = 1) -> int:
  if n < -1:
    infoSpec = """The implementation of factorial in 
    'worktoy.utilities.mathematics' does not implement the full gamma 
    function. Try using the 'scipy.special.gamma' function instead."""
    from .. import textFmt
    raise ValueError(textFmt(infoSpec))
  if n in [0, 1]:
    return c
  return factorial(n - 1, c * n)
