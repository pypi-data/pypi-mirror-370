"""
METACALL sentinel specifies that a class defers to the metaclass for the
class dunder hooks.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Sentinel

if TYPE_CHECKING:  # pragma: no cover
  pass


class METACALL(Sentinel):
  """METACALL sentinel specifies that a class defers to the metaclass for the
  class dunder hooks.
  """
  pass
