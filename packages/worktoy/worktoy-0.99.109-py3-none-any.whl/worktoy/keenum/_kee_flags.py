"""
KeeFlags enumerations all combinations of boolean valued flags. It
dynamically adds instances of KeeFlags for each boolean valued entry. The
result is a KeeNum-like enumeration consisting of all possible combinations
of boolean flags.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.keenum import KeeNum
from . import KeeFlagsMeta
from ._kee_desc import Flags, Names

if TYPE_CHECKING:  # pragma: no cover
  from typing import Self, Any


class KeeFlags(KeeNum, metaclass=KeeFlagsMeta):
  """
  KeeFlags is a metaclass that dynamically creates instances of KeeFlags
  for each boolean valued entry. It allows for the creation of an
  enumeration consisting of all possible combinations of boolean flags.

  Important Attributes:
  - flags: A descriptor returning the flags of a particular enumeration
  that are HIGH.

  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Public Variables
  flags = Flags()
  names = Names()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getValue(self) -> int:
    """Returns the integer value of the KeeFlags instance. """

    included = list(KeeNum._getValue(self))
    if not included:
      return 0
    out = included[0].getValue()
    for kee in included:
      out |= kee.getValue()
    return out

  def getMembers(self) -> tuple[Any, ...]:
    """
    Returns a tuple of the members of the KeeFlags instance.
    This method is used to access the members of the KeeFlags instance.
    """
    return (*list(KeeNum._getValue(self)),)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __or__(self, other: Self) -> Self:
    if not isinstance(other, KeeFlags):
      return NotImplemented
    return type(self).fromValue(self.value | other.value)

  def __and__(self, other: Self) -> Self:
    if not isinstance(other, KeeFlags):
      return NotImplemented
    return type(self).fromValue(self.value & other.value)

  def __xor__(self, other: Self) -> Self:
    if not isinstance(other, KeeFlags):
      return NotImplemented
    return type(self).fromValue(self.value ^ other.value)

  def __invert__(self) -> Self:
    return type(self).fromValue(~self.value & ((1 << len(self)) - 1))

  def __bool__(self) -> bool:
    return False if self.name == 'NULL' else True

  def __len__(self) -> int:
    """
    Returns the number of flags in the KeeFlags instance.
    This method is used to get the length of the KeeFlags instance.
    """
    return len(type(self).flags)
