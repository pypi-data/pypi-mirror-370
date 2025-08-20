"""
ContextInstance provides a contextually aware descriptor allowing
descriptor objects to access the currently active owning instance,
that is, the object passed to '__get__'. This allows the descriptor
implementation in the 'Object' class to create a context manager in which
the active instance is certain to be the one passed to the current
'__get__' method. This implies the limitation that this descriptor should
not be attempted accessed, except from within an activate context manager.

ContextInstance has a companion clas: 'ContextOwner' created on the same
principle, but returning instead the owner. That is, the second argument
passed to '__get__'.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class ContextInstance:
  """
  Exposes the instance passed to the '__get__' method on the owning 'Object'
  object.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __get__(self, instance: Any, owner: type) -> Any:
    if instance is None:
      return self
    return instance.getContextInstance()


class ContextOwner:
  """
  Exposes the owner passed to the '__get__' method on the owning 'Object'
  object.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __get__(self, instance: Any, owner: type) -> Any:
    if instance is None:
      return self
    return instance.getContextOwner()
