"""
EZData leverages the 'worktoy' library to provide a dataclass.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import EZMeta
from ..mcls import BaseObject

if TYPE_CHECKING:  # pragma: no cover
  from typing import Callable, Iterator


def _root(callMeMaybe: Callable) -> Callable:
  """
  _root is a decorator that ensures the decorated function is called
  with the root class of EZData.
  """

  setattr(callMeMaybe, '__is_root__', True)
  return callMeMaybe


class EZData(BaseObject, metaclass=EZMeta):
  """
  EZData is a dataclass that provides a simple way to define data
  structures with validation and serialization capabilities.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @_root
  def __init__(self, *args, **kwargs) -> None:
    """This is just here for type checking purposes. The EZMeta control
    flow removes it with the auto-generated __init__ method."""

  @_root
  def __iter__(self, ) -> Iterator:
    """See documentation for __init__ above."""

  @_root
  def __len__(self, ) -> int:
    """See documentation for __init__ above."""

  @_root
  def __setitem__(self, *_) -> None:
    """See documentation for __init__ above."""

  @_root
  def __getitem__(self, *_) -> None:
    """See documentation for __init__ above."""

  @classmethod
  def __class_len__(cls, ) -> int:
    """Return the number of class variables."""
    return len(getattr(cls, '__slots__', ()))

  @classmethod
  def __class_iter__(cls, ) -> Iterator[str]:
    """Iterate over the class variables."""
    yield from getattr(cls, '__slots__', ())

  @classmethod
  def __class_contains__(cls, item: str) -> bool:
    """Check if the class contains the given item."""
    return item in getattr(cls, '__slots__', ())

  def __set_name__(self, owner: type, name: str) -> None:
    """Removes 'Object.__set_name__' which would set attributes on the
    instance. """
