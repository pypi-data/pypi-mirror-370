"""
EZDesc provides descriptors intended to provide class specific settings on
the EZMeta metaclass.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..core import Object
from ..utilities import maybe
from ..waitaminute import TypeException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class EZDesc(Object):
  """
  EZDesc provides descriptors intended to provide class specific settings on
  the EZMeta metaclass.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # Fallback Variables
  __fallback_type__ = bool

  #  Private Variables
  __keyword_argument__ = None
  __default_value__ = None  # falls back to 'False'
  __value_type__ = None  # falls back to 'bool'

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getKwarg(self) -> Any:
    """
    Returns the keyword argument that controls the value of the
    descriptor. This must be set to a 'str' object when the descriptor is
    instantiated.
    """
    return self.__keyword_argument__

  def _getValueType(self) -> Any:
    """
    Returns the type of value that the descriptor is expected to hold. If
    a type other than 'bool' is required, it must be provided when
    instantiating the descriptor.
    """
    return maybe(self.__value_type__, self.__fallback_type__)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, key: str, *args) -> None:
    self.__keyword_argument__ = key
    type_, defVal, *_ = [*args, None, None]
    self.__value_type__ = type_
    self.__default_value__ = defVal

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __instance_get__(self, *args, **_) -> Any:
    """
    This method is called when the descriptor is accessed on an instance.
    It should return the value of the descriptor for that instance.
    """
    kwargs = maybe(self.instance.__namespace__.__key_args__, dict())
    value = kwargs.get(self.__keyword_argument__, self.__default_value__)
    valueType = self._getValueType()
    if valueType is bool:
      return True if value else False
    if isinstance(value, valueType):
      return value
    raise TypeException('value', value, valueType, )
