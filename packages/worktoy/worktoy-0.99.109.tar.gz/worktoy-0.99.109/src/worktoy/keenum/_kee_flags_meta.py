"""KeeFlagsMeta provides the metaclass for KeeFlags."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from string import ascii_letters, digits
from typing import TYPE_CHECKING

from worktoy.keenum import KeeMeta
from worktoy.mcls import AbstractMetaclass
from . import KeeFlagsSpace as KSpace
from ._kee_desc import FlagType
from ..utilities import replaceFlex
from ..waitaminute import attributeErrorFactory
from ..waitaminute.keenum import KeeNameError

if TYPE_CHECKING:  # pragma: no cover
  from typing import TypeAlias, Self, Any

  Bases: TypeAlias = tuple[type, ...]


class KeeFlagsMeta(KeeMeta):
  """KeeFlagsMeta is the metaclass for KeeFlags, providing additional
  functionality for handling flags."""

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Public Variables
  flagType = FlagType()

  @classmethod
  def __prepare__(mcls, name: str, bases: Bases, **kw) -> KSpace:
    """Replaces the KeeSpace with KeeFlagsSpace"""
    bases = (*[b for b in bases if b.__name__ != '_InitSub'],)
    return KSpace(mcls, name, bases, **kw)

  def __new__(mcls, name: str, bases: Bases, space: KSpace, **kw) -> Self:
    """
    Creates a new instance of the class.
    This method is called when the class is created.
    """
    if name == 'KeeFlags':
      return AbstractMetaclass.__new__(mcls, name, bases, space, **kw)
    return super().__new__(mcls, name, bases, space.expandNum(), **kw)

  def __getattr__(cls, key: str) -> Any:
    """
    Resolves the key to a Kee instance.
    This method is called when an attribute is accessed on the class.
    """
    try:
      out = cls._resolveKey(key)
    except KeeNameError as keeNameError:
      raise attributeErrorFactory(cls, key) from keeNameError
    else:
      return out

  def _resolveKey(cls, key: str) -> Any:
    """Resolves the key to a Kee instance."""
    if key == 'ALL':
      return ~cls._resolveKey('NULL')
    try:
      value = KeeMeta._resolveKey(cls, key)
    except KeeNameError as keeNameError:
      for item in cls:
        if cls._resolveNames(key, *item.names):
          return item
      raise keeNameError
    else:
      return value

  @classmethod
  def _resolveNames(mcls, identifier: str, *names) -> bool:
    """Resolves the names to a Kee instance."""
    if not names:
      chars = '%s%s' % (ascii_letters, digits)
      if any(c in chars for c in identifier):
        return False
      return True
    names = [*names, ]
    name = names.pop().lower()
    identifier = identifier.lower()
    if name in identifier:
      for i in range(str.count(identifier, name)):
        test = replaceFlex(identifier, name, '?' * len(name), i + 1)
        if mcls._resolveNames(test, *names):
          return True
    return False
