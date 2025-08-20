"""
TypeSig encapsulates type signatures for overloads
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.core.sentinels import THIS
from worktoy.utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from typing import TypeAlias, Self, Iterator, Union

  RawTypes: TypeAlias = tuple[type, ...]
  HASHABLE: TypeAlias = Union[type, int]


class TypeSig:
  """TypeSig encapsulates type signatures for overloads. """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables

  #  Fallback Variables

  #  Private Variables
  __raw_types__ = None

  #  Public Variables

  #  Virtual Variables

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getRawTypes(self) -> RawTypes:
    return self.__raw_types__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, *rawTypes: type) -> None:
    self.__raw_types__ = rawTypes

  @classmethod
  def fromArgs(cls, *args, ) -> Self:
    """
    Create a TypeSig from the given arguments.
    """
    return cls(*[type(arg) for arg in args], )

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __iter__(self, ) -> Iterator[type]:
    yield from self._getRawTypes()

  def __hash__(self, ) -> int:
    # if THIS in self:
    #   raise NotImplementedError
    return hash(self._getRawTypes())

  def __len__(self, ) -> int:
    return len(self._getRawTypes())

  def __contains__(self, type_: HASHABLE) -> bool:
    for rawType in self._getRawTypes():
      if rawType is type_:
        return True
    return False

  def __eq__(self, other: object) -> bool:
    if not isinstance(other, type(self)):
      return NotImplemented
    if len(self) != len(other):
      return False
    for this, that in zip(self, other):
      if this is not that:
        return False
    return True

  def __str__(self) -> str:
    """Returns a string representation of the type signature."""
    infoSpec = """%s object with %d types: %s"""
    typeStr = '[%s]' % ', '.join(str(t) for t in self)
    n = len(self)
    clsName = type(self).__name__
    return textFmt(infoSpec % (clsName, n, typeStr))

  def __repr__(self) -> str:
    """Returns code that would recreate the type signature."""
    infoSpec = """%s(%s)"""
    typeStr = ', '.join(repr(t) for t in self)
    return textFmt(infoSpec % (type(self).__name__, typeStr))

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def swapTHIS(self, thisType: type) -> None:
    newTypes = []
    for rawType in self._getRawTypes():
      if rawType is THIS:
        newTypes.append(thisType)
      else:
        newTypes.append(rawType)
    self.__raw_types__ = (*newTypes,)
