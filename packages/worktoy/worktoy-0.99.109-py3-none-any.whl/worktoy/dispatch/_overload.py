"""
The 'overload' function provides a decorator setting type signatures for
particular function overload. This overloading implementation requires
that the owning class is derived from 'BaseMeta' or a subclass of
'BaseMeta'. Other classes must use the 'Dispatcher' descriptor from
'worktoy.dispatch' instead.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.dispatch import TypeSig
from ..utilities import maybe, perm
from ..waitaminute import attributeErrorFactory

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Callable, TypeAlias, Self, Iterator, Never

  Method: TypeAlias = Callable[..., Any]
  Decorator: TypeAlias = Callable[[Method], Self]


class overload:  # NOQA
  """
  Entry collected by LoadSpaceHook
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __sig_func_dict__ = None
  __next_sig__ = None
  __next_func__ = None
  __latest_func__ = None
  __fallback_func__ = None
  __finalizer_func__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getSigFuncDict(self) -> dict[TypeSig, Method]:
    return maybe(self.__sig_func_dict__, dict())

  def _getLatestFunc(self) -> Method:
    if self.__latest_func__ is None:
      raise RuntimeError
    return self.__latest_func__

  def isFallback(self) -> bool:
    """Check if the current overload is a fallback function."""
    return False if self.__fallback_func__ is None else True

  def getFallback(self, ) -> Method:
    """Get the fallback function for the overload."""
    return self.__fallback_func__

  def isFinalizer(self) -> bool:
    """Check if the current overload is a finalizer function."""
    return False if self.__finalizer_func__ is None else True

  def getFinalizer(self, ) -> Method:
    """Get the finalizer function for the overload."""
    return self.__finalizer_func__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _addSigFunc(self, sig: TypeSig, func: Method) -> None:
    existing = self._getSigFuncDict()
    existing[sig] = func
    self.__latest_func__ = func
    self.__sig_func_dict__ = existing

  def _extendLatest(self, sig: TypeSig) -> None:
    """Extend the latest function with a new signature."""
    self._addSigFunc(sig, self._getLatestFunc())

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __new__(cls, *types, **kwargs) -> Decorator:
    """Create a decorators that sets the type signature for the function."""

    if kwargs.get('_root', False):
      return super(overload, cls).__new__(cls)

    def decorator(func: Method) -> overload:
      if isinstance(func, cls):
        func._extendLatest(TypeSig(*types, ))
        return func
      self = super(overload, cls).__new__(cls)
      self._addSigFunc(TypeSig(*types, ), func)
      return self

    return decorator

  def __init__(self, *args, **kwargs) -> None:
    pass

  @classmethod
  def flex(cls, *types: type) -> Decorator:
    """Create a decorator that sets the type signature for the function."""

    def decorator(func: Method) -> Self:
      self = cls(_root=True)
      for p in perm(*types, ):
        self._addSigFunc(TypeSig(*p, ), func)
      return self

    return decorator

  @classmethod
  def fallback(cls, func) -> Self:
    """Create a decorator that sets the fallback function for the
    overload."""
    self = cls(_root=True)
    self.__fallback_func__ = func
    return self

  @classmethod
  def finalize(cls, func: Method) -> Self:
    """Create a decorator that sets the finalizer function for the
    overload."""
    self = cls(_root=True)
    self.__finalizer_func__ = func
    return self

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __getattr__(self, key: str) -> Any:
    funcs = [f for _, f in self._getSigFuncDict().items()]
    if funcs:
      func = funcs[0]
    elif self.isFallback():
      func = self.getFallback()
    else:
      raise attributeErrorFactory(self, key)
    try:
      value = getattr(func, key)
    except AttributeError:
      raise attributeErrorFactory(self, key)
    else:
      return value

  def __iter__(self, ) -> Iterator[tuple[TypeSig, Method]]:
    """Iterate over the signatures and functions in the overload."""
    yield from self._getSigFuncDict().items()

  if TYPE_CHECKING:  # pragma: no cover
    def __call__(self, func: Method) -> Never:
      """Linter friendly explicitly disabled call method. """
