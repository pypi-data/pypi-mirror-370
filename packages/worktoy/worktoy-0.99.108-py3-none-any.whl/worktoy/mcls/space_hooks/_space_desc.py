"""
SpaceDesc provides a descriptor class for 'AbstractSpaceHook' objects,
exposing it to the namespace object.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class SpaceDesc:
  """
  SpaceDesc provides a descriptor class for 'AbstractSpaceHook' objects,
  exposing it to the namespace object.
  """

  def __get__(self, instance: Any, owner: type) -> Any:
    """Returns the space hook of the 'AbstractSpaceHook' instance."""
    if instance is None:
      return self
    return getattr(instance, '__space_object__')
