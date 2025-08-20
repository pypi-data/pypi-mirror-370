"""
The 'maybe' function returns the first value that is not 'None'.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


def maybe(*args) -> Any:
  """
  Returns the first argument that is not None.
  """
  for arg in args:
    if arg is not None:
      return arg
