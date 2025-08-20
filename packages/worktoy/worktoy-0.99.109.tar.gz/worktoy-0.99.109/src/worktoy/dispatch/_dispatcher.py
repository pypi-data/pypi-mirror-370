"""
Dispatcher encapsulates the mapping from type signature to function
objects and thus provides the core overloading functionality.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import sys
from types import FunctionType as Func
from types import MethodType as Meth
from typing import TYPE_CHECKING

from ..core import Object
from ..utilities import maybe, typeCast, perm
from ..waitaminute import TypeException, VariableNotNone
from ..waitaminute.desc import ReadOnlyError, ProtectedError
from ..dispatch import TypeSig
from ..waitaminute.dispatch import DispatchException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Callable, Never, TypeAlias, Optional, Self

  Method: TypeAlias = Callable[[Any, ...], Any]
  Decorator: TypeAlias = Callable[[Method], Self]
  SigFuncList: TypeAlias = list[tuple[TypeSig, Method]]
  SigFuncMap: TypeAlias = dict[TypeSig, Method]


class Dispatcher(Object):
  """
  Dispatcher encapsulates the mapping from type signature to function
  objects and thus provides the core overloading functionality.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __sig_funcs__ = None
  __fallback_func__ = None
  __field_name__ = None
  __field_owner__ = None
  __finalizer_func__ = None

  #  Public Variables

  #  Virtual Variables

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getSigFuncList(self) -> SigFuncList:
    return maybe(self.__sig_funcs__, [])

  def _getSigFuncMap(self) -> SigFuncMap:
    return {sig: func for sig, func in self._getSigFuncList()}

  def _getFallbackFunction(self) -> Optional[Method]:
    return self.__fallback_func__

  def _getFinalizerFunction(self) -> Optional[Method]:
    """
    Get the finalizer function if it exists.
    """
    return self.__finalizer_func__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def addSigFunc(self, sig: TypeSig, func: Method) -> Method:
    """
    Add a signature-function pair to the internal signature-function map.
    """
    existing = self._getSigFuncList()
    if func is self:
      self.__sig_funcs__ = [*existing, (sig, existing[-1][-1])]
    else:
      self.__sig_funcs__ = [*existing, (sig, func,)]
    return func

  def setFallbackFunction(self, func: Method) -> Method:
    if not callable(func):
      raise TypeException('__fallback_func__', func, Func, Meth)
    if self.__fallback_func__ is not None:
      raise VariableNotNone('__fallback_func__', self.__fallback_func__)
    self.__fallback_func__ = func
    return func

  def setFinalizerFunction(self, func: Method) -> Method:
    """
    Set the finalizer function that will be called when the dispatcher is
    deleted or finalized.
    """
    if not callable(func):
      raise TypeException('__finalizer_func__', func, Func, Meth)
    if self.__finalizer_func__ is not None:
      raise VariableNotNone('__finalizer_func__', self.__finalizer_func__)
    self.__finalizer_func__ = func
    return func

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __get__(self, instance: Any, owner: type) -> Any:
    """
    Descriptor protocol method to return a decorator that can be used to
    register functions with specific type signatures.
    """
    finalizer = self._getFinalizerFunction()
    if instance is None:
      return self
    sigFuncMap = self._getSigFuncMap()

    def dispatch(*args, **kwargs) -> Any:
      try:
        argSig = TypeSig.fromArgs(*args, )
        func = sigFuncMap.get(argSig, None)
        #  FASTEST
        if func is not None:
          return func(instance, *args, **kwargs)
        #  FAST
        for sig, func in sigFuncMap.items():
          if len(argSig) != len(sig):
            continue
          for arg, type_ in zip(args, sig):
            if not isinstance(arg, type_):
              break
          else:
            return func(instance, *args, **kwargs)
        #  SLOW
        for sig, func in sigFuncMap.items():
          castArgs = []
          if len(argSig) != len(sig):
            continue
          for arg, type_ in zip(args, sig):
            if isinstance(arg, type_):
              castArgs.append(arg)
              continue
            try:
              castedArg = typeCast(type_, arg)
            except (ValueError, TypeError):
              break
            else:
              castArgs.append(castedArg)
          else:
            return func(instance, *castArgs, **kwargs)
        #  FALLBACK
        fallback = self._getFallbackFunction()
        if callable(fallback):
          return fallback(instance, *args, **kwargs)
        raise DispatchException(self, args, )
      finally:
        _, exception, __ = sys.exc_info()
        if callable(finalizer):
          try:
            finalizer(instance, *args, **kwargs)
          except Exception as finalException:
            if exception is None:
              raise finalException
            raise exception from finalException

    return dispatch

  def __call__(self, instance: Any, *args, **kwargs) -> Any:
    """
    Allows invoking the dispatcher when accessed through the owning class.
    """
    return self.__get__(instance, type(instance))(*args, **kwargs)

  def __set__(self, instance: Any, value: Any, **kwargs) -> Never:
    """Illegal setter operation"""
    raise ReadOnlyError(self, instance, value)

  def __delete__(self, instance: Any, **kwargs) -> Never:
    """Illegal delete operation"""
    raise ProtectedError(instance, self, )

  def __set_name__(self, owner: type, name: str) -> None:
    self.__field_name__ = name
    self.__field_owner__ = owner
    self.swapAllTHIS(owner)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def clone(self, ) -> Self:
    """
    Create a clone of this DescriptorOverload instance.
    """
    newLoad = type(self)()
    newLoad.__sig_funcs__ = self._getSigFuncList()
    fallback = self._getFallbackFunction()
    if fallback is not None:
      newLoad.__fallback_func__ = fallback
    return newLoad

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def overload(self, *types: type) -> Decorator:
    def decorator(func: Method) -> Self:
      """Decorator to register the function with the given types."""
      self.addSigFunc(TypeSig(*types), func)
      return self

    return decorator

  def finalize(self, func: Method) -> Decorator:
    self.setFinalizerFunction(func)
    return self

  def fallback(self, func: Method) -> Decorator:
    self.setFallbackFunction(func)
    return self

  def flex(self, *types: type, ) -> Decorator:
    """
    Decorator to register a function that can handle any type signature.
    This function will be called if no other signature matches.
    """

    def decorator(func: Method) -> Self:
      for p in perm(*types, ):
        self.addSigFunc(TypeSig(*p), func)
      return self

    return decorator

  def swapAllTHIS(self, thisType: type) -> None:
    """
    Swap all occurrences of THIS in the registered signatures with the
    provided type.
    """
    for sig, func in self._getSigFuncList():
      sig.swapTHIS(thisType)
