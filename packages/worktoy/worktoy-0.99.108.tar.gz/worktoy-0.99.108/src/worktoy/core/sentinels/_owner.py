"""
OWNER provides a sentinel object used together with THIS by the descriptor
flow where OWNER provides a placeholder for the owning class, while THIS
refers to an instance of the class (self typically).
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Sentinel

if TYPE_CHECKING:  # pragma: no cover
  pass


class OWNER(Sentinel):
  """
  OWNER provides a sentinel object used together with THIS by the descriptor
  flow where OWNER provides a placeholder for the owning class, while THIS
  refers to an instance of the class (self typically).
  """
