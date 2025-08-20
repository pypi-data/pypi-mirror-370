"""
KeeTypeException provides a custom exception raised to indicate member
with wrong type in an enumeration.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class KeeTypeException(TypeError):
  """
  KeeTypeException provides a custom exception raised to indicate member
  with wrong type in an enumeration.
  """

  __slots__ = ('name', 'value', 'expectedTypes')

  def __init__(self, name: str, value: Any, *types) -> None:
    """Initialize the KeeTypeException object."""
    self.name = name
    self.value = value
    self.expectedTypes = types
    TypeError.__init__(self, )

  def __str__(self) -> str:
    """Return the string representation of the KeeTypeException object."""
    infoSpec = """KeeNum member '%s' has value '%s' of type '%s', but 
    expected type to be: '%s'!"""
    name = self.name
    typeNames = [t.__name__ for t in self.expectedTypes]
    from ...utilities import joinWords
    typeStr = joinWords(*["""'%s'""" % name for name in typeNames], )
    value = str(self.value)
    valueType = type(self.value).__name__
    info = infoSpec % (name, value, valueType, typeStr)
    return info

  __repr__ = __str__
