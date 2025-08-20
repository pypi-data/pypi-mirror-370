"""
KeeValueError provides a custom exception raised to indicate that an
enumeration class has no members with a given value.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any

  from ...keenum import KeeMeta


class KeeValueError(ValueError):
  """
  KeeValueError provides a custom exception raised to indicate that an
  enumeration class has no members with a given value.
  """

  __slots__ = ('keenum', 'value')

  def __init__(self, keenum: KeeMeta, value: Any) -> None:
    self.keenum, self.value = keenum, value

  def __str__(self) -> str:
    infoSpec = """KeeNum enumeration: '%s' has no member with value '%s'!"""
    info = infoSpec % (self.keenum, self.value)
    from ...utilities import textFmt
    return textFmt(info)

  __repr__ = __str__
