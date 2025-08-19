"""
DESC sentinel provides a placeholder for the descriptor object in the
descriptor flow along with THIS and OWNER.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Sentinel

if TYPE_CHECKING:  # pragma: no cover
  pass


class DESC(Sentinel):
  """
  DESC sentinel provides a placeholder for the descriptor object in the
  descriptor flow along with THIS and OWNER.
  """
