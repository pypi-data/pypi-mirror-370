"""
KeeNameError provides a custom exception raised to indicate an attempt to
resolve a member of an enumeration with an unrecognized name.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class KeeNameError(KeyError):
  """
  KeeNameError provides a custom exception raised to indicate an attempt to
  resolve a member of an enumeration with an unrecognized name.
  """

  __slots__ = ('keenum', 'name')

  def __init__(self, keenum: Any, name: str) -> None:
    self.keenum, self.name = keenum, name

  def __str__(self) -> str:
    infoSpec = """KeeNum enumeration: '%s' has no member named '%s'!"""
    info = infoSpec % (self.keenum, self.name)
    from ...utilities import textFmt
    return textFmt(info)

  __repr__ = __str__
