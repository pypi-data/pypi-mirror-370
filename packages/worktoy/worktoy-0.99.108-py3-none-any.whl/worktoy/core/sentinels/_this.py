"""
THIS is the sentinel object representing the class currently under
construction.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Sentinel

if TYPE_CHECKING:  # pragma: no cover
  pass


class THIS(Sentinel):
  """
  THIS is the sentinel object representing the class currently under
  construction. Similar to the 'self' keyword, it is used to refer to the
  class being defined.
  """
