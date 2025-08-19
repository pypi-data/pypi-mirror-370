"""
FlagType exposes the type of the underlying flags used in KeeFlags.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import AbstractKeeDesc

if TYPE_CHECKING:  # pragma: no cover
  from typing import Type


class FlagType(AbstractKeeDesc):
  """
  FlagType exposes the type of the underlying flags used in KeeFlags.
  It is used to access the type of the flags in a KeeFlags instance.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __instance_get__(self, instance: FlagType) -> Type:
    """
    Get the type of the flags of the instance.
    This method is called when the descriptor is accessed on an instance.
    """
    return getattr(instance, '__flag_type__', )
