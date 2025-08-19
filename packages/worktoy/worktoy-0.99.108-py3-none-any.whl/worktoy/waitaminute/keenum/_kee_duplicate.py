"""
KeeDuplicate is a custom exception raised to indicate that a KeeNum
class received a duplicate entry for an enumeration.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class KeeDuplicate(Exception):
  """
  KeeDuplicate is a custom exception raised to indicate that a KeeNum
  class received a duplicate entry for an enumeration.
  """

  __slots__ = ('name', 'value')

  def __init__(self, name: str, value: Any) -> None:
    """Initialize the KeeDuplicate object."""
    self.name = name
    self.value = value
    Exception.__init__(self, )

  def __str__(self, ) -> str:
    """Return the string representation of the KeeDuplicate object."""
    infoSpec = """Duplicate KeeNum member '%s' with value '%s'!"""
    info = infoSpec % (self.name, str(self.value))
    return textFmt(info)

  __repr__ = __str__
