"""
AbstractKeeDesc provides an abstract baseclass for the descriptor classes
in the 'worktoy.keenum._kee_desc' module.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Type, TypeAlias

  from .. import KeeMeta

  Kee: TypeAlias = Type[KeeMeta]


class AbstractKeeDesc:
  """
  _KeeDesc provides a specialized descriptor class for the 'KeeMeta'
  class. It should be considered private to the 'worktoy.keenum' module and
  is not intended, nor fit, for general use.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __field_owner__ = None
  __field_name__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __set_name__(self, owner: Kee, name: str) -> None:
    """
    Set the owner and name of the descriptor when it is assigned to a class.
    This is called by Python when the descriptor is created.
    """
    self.__field_owner__ = owner
    self.__field_name__ = name

  def __get__(self, instance: KeeMeta, owner: Kee) -> Any:
    """
    Get the value of the descriptor. If the instance is None, return the
    owner class. Otherwise, return the value from the instance.
    """
    if instance is None:
      return self
    return self.__instance_get__(instance)

  @abstractmethod
  def __instance_get__(self, instance: KeeMeta) -> Any:
    """This method should be implemented by subclasses to specify
    particular functionality. """
