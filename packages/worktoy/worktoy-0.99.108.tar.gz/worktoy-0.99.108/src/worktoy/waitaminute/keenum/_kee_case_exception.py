"""
KeeCaseException provides a custom exception raised to indicate that a
member of an enumeration was set not with upper case.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  pass


class KeeCaseException(ValueError):
  """
  KeeCaseException provides a custom exception raised to indicate that a
  member of an enumeration was set not with upper case.
  """

  __slots__ = ('name',)

  def __init__(self, name: str, ) -> None:
    """Initialize the KeeCaseException object."""
    self.name = name
    ValueError.__init__(self, )

  def __str__(self) -> str:
    """Return the string representation of the KeeCaseException object."""
    infoSpec = """KeeNum members must have upper case names, but received: 
    '%s'"""
    from ...utilities import textFmt
    return textFmt(infoSpec % self.name)

  __repr__ = __str__
