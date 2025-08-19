"""
IsRoot implements a descriptor flag indicating whether a given KeeNum
class is a root enumeration, that is, is KeeNum itself a base class of it.
Non-root enumerations cannot change the members inherited from the base
enumeration, but can extend them with new members. Inherited members are
guaranteed to have same identity as those in the base class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import AbstractKeeDesc

if TYPE_CHECKING:  # pragma: no cover
  from typing import Type, TypeAlias

  from .. import KeeMeta

  Kee: TypeAlias = Type[KeeMeta]


class IsRoot(AbstractKeeDesc):
  """
  IsRoot implements a descriptor flag indicating whether a given KeeNum
  class is a root enumeration, that is, is KeeNum itself a base class of it.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __instance_get__(self, instance: KeeMeta) -> bool:
    """
    Return True if the instance is a root enumeration, that is, if it is
    KeeNum itself or a subclass of it.
    """
    return True if instance.__bases__[0].__name__ == 'KeeNum' else False
