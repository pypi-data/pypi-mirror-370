"""
EZMultipleInheritance provides a custom exception raised when any attempt
is made to create a class that inherits from multiple subclasses of EZData.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import joinWords

if TYPE_CHECKING:  # pragma: no cover
  from typing import Type
  from worktoy.ezdata import EZData


class EZMultipleInheritance(TypeError):
  """
  EZMultipleInheritance provides a custom exception raised when any attempt
  is made to create a class that inherits from multiple subclasses of EZData.
  """

  __slots__ = ('name', 'bases')

  def __init__(self, name: str, *bases: Type[EZData]) -> None:
    """
    Initialize the EZMultipleInheritance exception.

    :param name: The name of the class being created.
    :param bases: The base classes that are being inherited from.
    """
    self.name = name
    self.bases = bases
    TypeError.__init__(self, )

  def __str__(self) -> str:
    infoSpec = """Attempted to create class '%s' with multiple EZData 
    subclasses: '%s'. """
    baseStr = joinWords(*[b for b in self.bases])
    return infoSpec % (self.name, baseStr)

  __repr__ = __str__
