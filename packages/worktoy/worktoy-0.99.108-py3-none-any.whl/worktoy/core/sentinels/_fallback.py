"""
FALLBACK provides a sentinel object indicating that an entry in a 'Dispatch'
object is a fallback entry. In particular, this is the case when a
'TypeSig' object contains only the 'FALLBACK' sentinel and no other type.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Sentinel

if TYPE_CHECKING:  # pragma: no cover
  pass


class FALLBACK(Sentinel):
  """FALLBACK provides a sentinel object indicating that an entry in a
  'Dispatch' object is a fallback entry. In particular, this is the case
  when a 'TypeSig' object contains only the 'FALLBACK' sentinel and no
  other type."""
