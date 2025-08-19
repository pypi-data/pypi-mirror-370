"""
ReservedNames provides a list of reserved names that are set
automatically by the interpreter.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt
from ...core import Object

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Iterator


class ReservedNames(Object):
  """
  ReservedNames provides a list of reserved names that are set
  automatically by the interpreter.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  __reserved_names__ = [
      '__dict__',
      '__weakref__',
      '__module__',
      '__annotations__',
      '__match_args__',
      '__doc__',
      '__name__',
      '__qualname__',
      '__firstlineno__',
      '__static_attributes__',
  ]

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __iter__(self) -> Iterator[str]:
    """
    Iterate over the reserved names.
    """
    yield from self.__reserved_names__

  def __contains__(self, name: str) -> bool:
    """Check if the name is in the reserved names."""
    for item in self:
      if item == name:
        return True
    return False

  def __len__(self) -> int:
    """Get the number of reserved names."""
    return len(self.__reserved_names__)

  def __str__(self, ) -> str:
    """Get the string representation of the metaclass."""
    info = 'ReservedNames:\n%s'
    names = '<br><tab>'.join([name for name in self])
    return textFmt(info % names)

  __repr__ = __str__

  def __instance_get__(self, *args, **kwargs) -> Any:
    """
    Get the reserved name by its string identifier.
    """
    return self
