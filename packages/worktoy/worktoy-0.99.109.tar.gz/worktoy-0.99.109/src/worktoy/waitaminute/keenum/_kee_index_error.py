"""
KeeIndexError provides a custom exception raised to indicate that a given
positive index is out of range for a particular enumeration.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class KeeIndexError(IndexError):
  """
  KeeIndexError provides a custom exception raised to indicate that a given
  positive index is out of range for a particular enumeration.
  """

  __slots__ = ('keenum', 'index')

  def __init__(self, keenum: Any, index: int) -> None:
    self.keenum, self.index = keenum, index

  def __str__(self) -> str:
    infoSpec = """KeeNum object: '%s' does not have an index '%d'!"""
    info = infoSpec % (self.keenum, self.index)
    from ...utilities import textFmt
    return textFmt(info)

  __repr__ = __str__
