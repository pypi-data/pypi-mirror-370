"""
Field provides a property-like descriptor implementation allowing
descriptor owners to decorate methods to designate them as accessors.
Since these are identified by name, the function object are entirely
unaffected by the decoration and subclasses can override any decorated
method and the descriptor uses the overridden method instead.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..core import Object
from ..utilities import maybe
from ..waitaminute.desc import ProtectedError, ReadOnlyError, AccessError

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Callable, TypeAlias

  CallMeMaybe: TypeAlias = Callable[..., Any]


class Field(Object):
  """
  Flexible descriptor requiring accessor methods to be decorated. Please
  note that the instance of 'Field' can decorate only methods appearing
  below it in the class body.

  @GET - Decorate one method designating it as the 'getter'. It should be
  a normal instance method that can be run without any other arguments.

  @SET - Decorate any number of methods as setters. Every such method runs
  in response to __set__

  @DELETE - Decorate any number of methods as deleters. Optionally, implement
  by setting the value to the 'DELETED' sentinel object.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __get_key__ = None
  __set_keys__ = None
  __delete_keys__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getGetterKey(self) -> str:
    if not isinstance(self.__get_key__, str):
      raise AccessError(self)
    return self.__get_key__

  def _getSetterKeys(self, newValue: Any = None) -> tuple[str, ...]:
    return (*[k for k in maybe(self.__set_keys__, ()) if k],)

  def _getDeleterKeys(self) -> tuple[str, ...]:
    return (*[k for k in maybe(self.__delete_keys__, ()) if k],)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def GET(self, callMeMaybe: Callable) -> Callable:
    """
    Decorator for the getter method. The method should be a normal instance
    method that can be run without any other arguments.
    """
    self.__get_key__ = callMeMaybe.__name__
    return callMeMaybe

  def SET(self, callMeMaybe: Callable) -> Callable:
    """
    Decorator for the setter method. The method should be a normal instance
    method that can be run without any other arguments.
    """
    existing = maybe(self.__set_keys__, ())
    self.__set_keys__ = (*existing, callMeMaybe.__name__,)
    return callMeMaybe

  def DELETE(self, callMeMaybe: Callable) -> Callable:
    """
    Decorator for the deleter method. The method should be a normal instance
    method that can be run without any other arguments.
    """
    existing = maybe(self.__delete_keys__, ())
    self.__delete_keys__ = (*existing, callMeMaybe.__name__,)
    return callMeMaybe

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __instance_get__(self, *args, **kwargs) -> Any:
    """
    Retrieves the getter from the owner of instance and the registered
    name of getter function. Please note that while the instance received
    is certain to satisfy: isinstance(instance, self.getFieldOwner()),
    the field owner is the class where the descriptor was instantiated.
    For this reason, the decorated method is retrieved by name from the
    owner of the instance received.
    """
    getterKey = self._getGetterKey()
    getterFunc = getattr(self.getContextInstance(), getterKey, )
    return getterFunc(*args, **kwargs)

  def __instance_set__(self, val: Any, *args, **kwargs) -> None:
    """
    All decorated setters are retrieved in the same fashion as the getter.
    """
    setterKeys = self._getSetterKeys(val)
    if not setterKeys:
      raise ReadOnlyError(self.instance, self, val, )
    instance = self.getContextInstance()
    setterFuncs = [getattr(instance, k) for k in setterKeys]
    setterFuncs = [f for f in setterFuncs if callable(f)]
    for setterFunc in setterFuncs:
      setterFunc(val, *args, **kwargs)

  def __instance_delete__(self, *args, **kwargs) -> None:
    """
    All decorated deleters are retrieved in the same fashion as the getter.
    """
    deleterKeys = self._getDeleterKeys()
    if not deleterKeys:
      oldVal = self.__instance_get__()
      raise ProtectedError(self.instance, self, oldVal)
    for key in deleterKeys:
      getattr(self.instance, key, )(**kwargs)

  #  For linters who won't chill out
  if TYPE_CHECKING:  # pragma: no cover
    __add__: CallMeMaybe
    __sub__: CallMeMaybe
    __mul__: CallMeMaybe
    __truediv__: CallMeMaybe
    __floordiv__: CallMeMaybe
    __mod__: CallMeMaybe
    __divmod__: CallMeMaybe
    __pow__: CallMeMaybe
    __lshift__: CallMeMaybe
    __rshift__: CallMeMaybe
    __and__: CallMeMaybe
    __xor__: CallMeMaybe
    __or__: CallMeMaybe
    __lt__: CallMeMaybe
    __le__: CallMeMaybe
    __eq__: CallMeMaybe
    __ne__: CallMeMaybe
    __gt__: CallMeMaybe
    __ge__: CallMeMaybe
    __hash__: CallMeMaybe
    __bool__: CallMeMaybe
    __str__: CallMeMaybe
    __repr__: CallMeMaybe
