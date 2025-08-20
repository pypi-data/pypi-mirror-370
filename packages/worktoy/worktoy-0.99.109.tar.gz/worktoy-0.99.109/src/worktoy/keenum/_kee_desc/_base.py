"""
Base provides a descriptor returning the immediate base class of the
KeeNum class. Eventually, the root class returns KeeNum itself.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import AbstractKeeDesc

if TYPE_CHECKING:  # pragma: no cover
  from .. import KeeMeta


class Base(AbstractKeeDesc):
  """
  Base provides a descriptor returning the immediate base class of the
  KeeNum class. Eventually the root class returns KeeNum itself.
  """

  def __instance_get__(self, instance: KeeMeta) -> KeeMeta:
    """
    Return the immediate base class of the KeeNum class. If the instance is
    a root enumeration, return KeeNum itself.
    """
    from .. import KeeNum
    if instance is KeeNum:
      return KeeNum
    return KeeNum if instance.isRoot else instance.__bases__[0]
