"""
Members provides a descriptor returning the enumeration members defined in
this class and those inherited from the base class up to the root class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import AbstractKeeDesc

if TYPE_CHECKING:  # pragma: no cover
  from typing import Iterator
  from .. import KeeMeta, Kee


class Members(AbstractKeeDesc):
  """
  Members provides a descriptor returning the enumeration members defined in
  this class and those inherited from the base class up to the root class.
  """

  def __instance_get__(self, instance: KeeMeta) -> Iterator[Kee]:
    yield from getattr(instance, '__num_members__', [])
