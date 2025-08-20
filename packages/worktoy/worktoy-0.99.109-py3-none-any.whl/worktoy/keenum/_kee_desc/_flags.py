"""
Flags returns a tuple of the flags that make up a KeeFlags subclass.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import AbstractKeeDesc

if TYPE_CHECKING:  # pragma: no cover
  from typing import TypeAlias, Type, Any

  from .. import KeeFlags, KeeMeta

  Flags: TypeAlias = Type[KeeFlags]


class Flags(AbstractKeeDesc):
  """
  Flags is a descriptor that returns a tuple of the flags that make up a
  KeeFlags subclass. It is used to access the flags of a KeeFlags instance.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __get__(self, instance: Any, owner: KeeMeta, **kwargs) -> Any:
    """
    Get the flags of the instance as a tuple.
    This method is called when the descriptor is accessed on the class.
    If the instance is None, it returns the flags of the class.
    """
    if instance is None:
      keeFlags = getattr(owner, '__kee_flags__', )
      if not keeFlags:
        return ()
      out = []
      for name, flag in keeFlags.items():
        out.append(flag)
      out.sort(key=lambda f: f.index)
      return (*out,)
    return self.__instance_get__(instance)

  def __instance_get__(self, instance: KeeFlags) -> tuple:
    """
    Get the flags of the instance as a tuple.
    This method is called when the descriptor is accessed on an instance.
    """

    return instance.getMembers()
