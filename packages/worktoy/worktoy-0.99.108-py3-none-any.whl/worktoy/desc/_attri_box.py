"""
AttriBox implements a lazily instantiated and strongly typed descriptor
class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.core import Object
from worktoy.core.sentinels import DELETED

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Self


class AttriBox(Object):
  """
  AttriBox implements a lazily instantiated and strongly typed descriptor
  class.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __field_type__ = None  # The type of the objects stored in the box.

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def getFieldType(self) -> type:
    return self.__field_type__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _createFieldObject(self, ) -> Any:
    """
    Creates a new instance of the field type. This method is called when
    the field is accessed for the first time.
    """
    instance = self.getContextInstance()
    fieldType = self.getFieldType()
    owner = type(instance)
    args = self.getPosArgs(THIS=instance, OWNER=owner, DESC=self)
    kwargs = self.getKeyArgs(THIS=instance, OWNER=owner, DESC=self)
    return fieldType(*args, **kwargs)

  def __instance_get__(self, *args, **kwargs) -> Any:
    """
    Returns the value of the field for the given instance. If the value is
    not set, it initializes it with a new instance of the field type.
    """
    instance = self.getContextInstance()
    pvtName = self.getPrivateName()
    if hasattr(instance, pvtName):
      return getattr(instance, pvtName)
    fieldObject = self._createFieldObject()
    setattr(instance, pvtName, fieldObject)
    return self.__instance_get__(instance, _recursion=True)

  def __instance_set__(self, value: Any, *args, **kwargs) -> None:
    """
    Sets the value of the field for the given instance. If the value is
    not set, it initializes it with a new instance of the field type.
    """
    instance = self.getContextInstance()
    fieldType = self.getFieldType()
    pvtName = self.getPrivateName()
    if isinstance(value, fieldType) or kwargs.get('_root', False):
      return setattr(instance, pvtName, value)
    setattr(instance, pvtName, fieldType(value))

  def __instance_delete__(self, *args, **kwargs) -> None:
    """
    Deletes the value of the field for the given instance. If the value is
    not set, it does nothing.
    """
    self._deletedGuard(self.getContextInstance(), self.__instance_get__())
    self.__instance_set__(DELETED, _root=True)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __class_getitem__(cls, fieldType: type) -> Self:
    """
    Allows the AttriBox to be used as a generic type with a specified
    field type.
    """
    self = object.__new__(cls)
    self.__field_type__ = fieldType
    return self

  def __call__(self, *args: Any, **kwargs: Any) -> Any:
    """
    Allows the AttriBox to be called like a function, returning a new
    instance of the field type.
    """
    Object.__init__(self, *args, **kwargs)
    return self
