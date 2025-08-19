"""EZSlot encapsulates data fields in the EZData class."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..desc import Field
from ..mcls import BaseObject
from ..utilities import maybe

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Self


class EZSlot(BaseObject):
  """EZSlot encapsulates data fields in the EZData class. """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __future_name__ = None
  __type_value__ = None
  __default_value__ = None
  __global_scope__ = None
  __owner_name__ = None

  #  Public Variables
  ownerName = Field()
  name = Field()
  typeValue = Field()
  defaultValue = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @name.GET
  def _getName(self) -> str:
    """Get the name of the slot."""
    return self.__future_name__

  @typeValue.GET
  def _getTypeValue(self, **kwargs) -> type:
    """Get the type value of the slot."""
    return self.__type_value__

  @defaultValue.GET
  def _getDefaultValue(self, **kwargs) -> Any:
    """Get the default value of the slot."""
    return self.__default_value__

  @ownerName.GET
  def _getOwnerName(self) -> str:
    """Get the owner name of the slot."""
    return self.__owner_name__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, name: str) -> None:
    self.__future_name__ = name

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __eq__(self, other: Self) -> bool:
    """
    Compares only against other 'EZSlot' instances, but only by the 'name'
    attribute.
    """
    cls = type(self)
    if isinstance(other, cls):
      if self.name == other.name:
        return True
      return False
    return NotImplemented

  def __str__(self) -> str:
    """Get the string representation of the EZSlot."""
    infoSpec = """%s<%s.%s>(%s: %s)"""
    clsName = type(self).__name__
    valName = maybe(self.__default_value__, '[NONE]')
    typeName = self.typeValue.__name__
    info = infoSpec % (clsName, self.ownerName, self.name, typeName, valName)
    return info

  __repr__ = __str__
