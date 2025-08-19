"""
Names provides the names of the flags analogous to the 'Flags' descriptor
class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Flags

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any

  from .. import KeeMeta


class Names(Flags):
  """
  Names provides the names of the flags analogous to the 'Flags' descriptor
  class. It is used to access the names of the flags in a KeeFlags instance.
  """

  def __get__(self, instance: Any, owner: KeeMeta, **kwargs) -> Any:
    """
    Get the names of the flags of the instance.
    This method is called when the descriptor is accessed on an instance.
    """
    flags = Flags.__get__(self, instance, owner, **kwargs)
    return (*[flag.name for flag in flags],)
