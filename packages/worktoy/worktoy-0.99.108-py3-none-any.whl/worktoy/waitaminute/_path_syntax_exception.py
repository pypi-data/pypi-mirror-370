"""PathSyntaxException provides a custom exception raised to indicate that
a 'str' object is not a valid absolute path. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from typing import Union, TypeAlias, LiteralString

  Path: TypeAlias = Union[str, bytes, LiteralString]


class PathSyntaxException(ValueError):
  """
  PathSyntaxException provides a custom exception raised to indicate that
  a 'str' object is not a valid absolute path.
  """

  __slots__ = ('badPath',)

  def __init__(self, path: Path) -> None:
    """
    Initialize the PathSyntaxException with the invalid path.

    Args:
      path (str): The invalid path.
    """
    self.badPath = path
    ValueError.__init__(self, )

  def __str__(self, ) -> str:
    """
    Get the string representation of the exception.
    """

    infoSpec = """The path '%s' is not a valid, absolute path!"""
    return textFmt(infoSpec % self.badPath)

  __repr__ = __str__
