"""
BaseSpace provides the namespace class used by worktoy.mcls.BaseMeta
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..dispatch import TypeSig
from ..utilities import maybe
from . import AbstractNamespace
from .space_hooks import LoadSpaceHook

if TYPE_CHECKING:  # pragma: no cover
  from typing import TypeAlias, Callable, Any

  SigFunc: TypeAlias = dict[TypeSig, Callable[..., Any]]
  OverloadMap: TypeAlias = dict[str, SigFunc]
  Bases: TypeAlias = tuple[type, ...]


class BaseSpace(AbstractNamespace):
  """
  BaseSpace is the namespace used by BaseMeta. It enables function
  overloading and related features via hook registration.

  Classes defined using this namespace support method overloading through
  hooks installed automatically in the class body. These hooks handle
  overload collection, dispatch construction, and support for 'THIS' as a
  placeholder during class creation.

  The overload mechanism and other behavior are defined in
  `worktoy.mcls.hooks`. This namespace is returned from BaseMeta.__prepare__.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __overload_map__ = dict()
  __fallback_map__ = dict()
  __finalizer_map__ = dict()

  #  Public Variables
  loadSpaceHook = LoadSpaceHook()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, mcls: type, name: str, bases: Bases, **kw) -> None:
    AbstractNamespace.__init__(self, mcls, name, bases, **kw)
    self.__overload_map__ = dict()
    for space in self.getMRONamespaces():
      for name, sigFunc in getattr(space, '__overload_map__', ).items():
        self.__overload_map__[name] = dict()
        for sig, func in sigFunc.items():
          self.__overload_map__[name][sig] = func
      for name, func in getattr(space, '__fallback_map__', ).items():
        existing = maybe(self.__fallback_map__, dict())
        existing[name] = func
        self.__fallback_map__ = existing
      for name, func in getattr(space, '__finalizer_map__', ).items():
        existing = maybe(self.__finalizer_map__, dict())
        existing[name] = func
        self.__finalizer_map__ = existing

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def addOverload(
      self,
      name: str,
      sig: TypeSig,
      func: Callable
  ) -> None:
    if name not in self.__overload_map__:
      self.__overload_map__[name] = dict()
    self.__overload_map__[name][sig] = func

  def getOverloads(self, ) -> OverloadMap:
    return maybe(self.__overload_map__, {})

  def addFallback(self, key: str, func: Callable) -> None:
    """
    Set a fallback function for the given key in the overload map.
    """
    existing = maybe(self.__fallback_map__, dict())
    existing[key] = func
    self.__fallback_map__ = existing

  def getFallbacks(self) -> dict[str, Callable]:
    """
    Get the fallback functions for the overloads.
    """
    return maybe(self.__fallback_map__, dict())

  def addFinalizer(self, key: str, func: Callable) -> None:
    """
    Add a finalize function for the given key in the overload map.
    """
    existing = maybe(self.__finalizer_map__, dict())
    existing[key] = func
    self.__finalizer_map__ = existing

  def getFinalizers(self, ) -> dict[str, Callable]:
    """
    Get the finalize functions for the overloads.
    """
    return maybe(self.__finalizer_map__, dict())
