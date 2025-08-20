"""
Sentinel provides the base class for the sentinel objects provided by the
'worktoy.core.sentinels' module. By subclassing 'type' and becoming a
metaclass, it allows sentinel objects to be instances of 'type' and thus
classes.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.utilities import maybe

if TYPE_CHECKING:  # pragma: no cover
  from typing import Self, Never

  Bases = tuple[type, ...]


class _Sentinel(type):
  """
  Sentinel keeps track of all sentinel objects and prevents multiple
  sentinels of the same name from being created. It also prevents its
  derived classes from being instantiated.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  __registered_sentinels__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def _getRegisteredSentinels(mcls) -> list[Self]:
    """
    Get the dictionary of registered sentinel classes.
    """
    return maybe(mcls.__registered_sentinels__, [])

  @classmethod
  def _getNamedSentinel(cls, sentinelName: str, ) -> Self:
    """
    Returns registered sentinel having this name.
    """
    existing = cls._getRegisteredSentinels()
    for existingSentinel in existing:
      if existingSentinel.__name__ == sentinelName:
        return existingSentinel
    raise KeyError(sentinelName)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def _registerSentinel(mcls, sentinel: Self) -> None:
    """
    Register a sentinel class to prevent multiple sentinels of the same name
    from being created.
    """
    existing = mcls._getRegisteredSentinels()
    mcls.__registered_sentinels__ = [*existing, sentinel]

  @classmethod
  def __prepare__(mcls, name: str, bases: Bases, **kwargs) -> dict:
    """
    Prepare the class namespace for the sentinel class.
    """
    return dict()

  def __new__(mcls, name: str, bases: Bases, space: dict, **kwargs) -> Self:
    """
    Create a new sentinel class. If a sentinel with the same name already
    exists, return it instead of creating a new one.
    """
    try:
      cls = mcls._getNamedSentinel(name)
    except KeyError as keyError:
      if kwargs.get('_recursion', False):
        raise keyError from RecursionError
      namespace = dict()
      cls = super().__new__(mcls, name, (), namespace, **kwargs)
      mcls._registerSentinel(cls)
      return mcls.__new__(mcls, name, (), {}, _recursion=True)
    else:
      return cls

  def __call__(cls, *__, **_) -> Never:
    """
    Raises 'IllegalInstantiation'.
    """
    from worktoy.waitaminute.meta import IllegalInstantiation
    raise IllegalInstantiation(cls)

  def __str__(cls) -> str:
    """
    Return the string representation of the sentinel.
    """
    return """<Sentinel: '%s'>""" % cls.__name__

  __repr__ = __str__


class Sentinel(metaclass=_Sentinel):
  """
  Sentinel is the base class for all sentinel objects in the 'worktoy.core'
  module. It prevents instantiation and ensures that only one instance of
  each sentinel exists.
  """
  pass
