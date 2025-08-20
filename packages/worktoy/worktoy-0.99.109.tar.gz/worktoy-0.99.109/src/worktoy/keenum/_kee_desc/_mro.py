"""
MRO (Method Resolution Order) exposes the method resolution order through
a descriptor class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import AbstractKeeDesc

if TYPE_CHECKING:  # pragma: no cover

  from .. import KeeMeta, KeeNum


class MRO(AbstractKeeDesc):
  """
  MRO (Method Resolution Order) exposes the method resolution order through
  a descriptor class.
  """

  def __instance_get__(self, instance: KeeMeta) -> tuple[KeeMeta, ...]:
    """
    Return the method resolution order of the KeeNum class as a tuple of
    classes.
    """
    from .. import KeeNum
    if instance is KeeNum:
      return ()
    num = instance
    out = [num, ]
    while not num.isRoot:
      out.append(num.base)
      num = num.base
    else:
      return (*out,)
