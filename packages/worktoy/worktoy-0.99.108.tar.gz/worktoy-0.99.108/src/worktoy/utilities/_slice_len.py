"""
The 'sliceLen' function takes a slice object and an integer length and
returns the number of elements would be included if the slice were applied
to a sequence of that length.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  pass


def sliceLen(sliceObj: slice, length: int) -> int:
  """
  The 'sliceLen' function takes a slice object and an integer length and
  returns the number of elements would be included if the slice were applied
  to a sequence of that length.

  :param sliceObj: A slice object.
  :param length: An integer representing the length of the sequence.
  :return: The number of elements in the slice.
  """
  return len(range(*sliceObj.indices(length), ))
