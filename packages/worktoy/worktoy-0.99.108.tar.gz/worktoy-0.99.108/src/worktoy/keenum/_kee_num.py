"""
KeeNum provides the shared baseclass for KeeNum enumerating classes.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import KeeMeta, Kee
from ..core import Object
from ..desc import Field
from ..waitaminute.desc import ReadOnlyError, ProtectedError
from ..waitaminute.keenum import KeeWriteOnceError

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Never


class KeeNum(Object, metaclass=KeeMeta, ):
  """
  KeeNum is the base class for all enumerating classes in the KeeNum
  framework. It provides a common interface and functionality for
  enumerating members."""

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __field_index__ = None
  __field_value__ = None
  __frozen_state__ = None
  __field_kee__ = None  # The 'Kee' object of this member.

  #  Public Variables
  index = Field()
  value = Field()
  kee = Field()

  #  Virtual Variables
  name = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @kee.GET
  def _getKee(self) -> Kee:
    return self.__field_kee__

  @name.GET
  def _getName(self) -> str:
    return self.kee.name

  @index.GET
  def _getIndex(self) -> int:
    return self.kee.index

  @value.GET
  def _getValue(self) -> Any:
    """Return the value of the member."""
    return self.kee.getValue()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, member: Kee) -> None:
    object.__setattr__(self, '__frozen_state__', False)
    self.__field_kee__ = member
    object.__setattr__(self, '__frozen_state__', True)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __setattr__(self, name: str, value: Any) -> None:
    """Set an attribute of the member."""
    if object.__getattribute__(self, '__frozen_state__'):
      raise KeeWriteOnceError(self, name)
    return object.__setattr__(self, name, value)

  def __set_name__(self, owner: type, name: str) -> None:
    """This reimplementation of '__set_name__' is necessary to prevent the
    '__setattr__' method above from raising when a class wants an
    enumeration defined in its namespace. """
    pass

  def __get__(self, instance: Any, owner: type) -> KeeNum:
    """Implementation of '__get__' is necessary for the same reason as
    '__set_name__'. """
    return self

  def __set__(self, instance: Any, value: Any, **kwargs) -> Never:
    """Ensures 'ReadOnlyError' is raised instead of 'KeeWriteOnceError'."""
    raise ReadOnlyError(instance, self, value)

  def __delete__(self, instance: Any, **kwargs) -> Never:
    """Ensures 'ProtectedError' is raised instead of 'KeeWriteOnceError'."""
    raise ProtectedError(instance, self, self)

  def __bool__(self, ) -> bool:
    """
    Members named 'NULL' are always falsy. Other members reflect the
    truthiness of their value.
    """
    if self.name.lower() == 'null':
      return False
    return True if self.value else False

  def __int__(self) -> int:
    """Return the index of the member."""
    return self.index

  def __hash__(self) -> int:
    """Return the hash of the member."""
    return hash((type(self), self.index))

  def __eq__(self, other: Any) -> bool:
    if type(self) is not type(other):
      return NotImplemented
    return True if self is other else False

  def __str__(self) -> str:
    """Return the name of the member."""
    infoSpec = """%s.%s"""
    clsName = type(self).__name__
    info = infoSpec % (clsName, self.name)
    return info

  __repr__ = __str__
