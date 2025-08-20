"""
UnpackException is a custom exception raised to indicate that an unpacking
operation found no argument requiring unpacking. This is raised by the
'unpack' function in the 'worktoy.core' module when the 'strict' mode is
enabled and no iterable is found among the arguments. Please note that
this function does not consider strings or bytes as unpackable iterables.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class UnpackException(ValueError):
  """
  UnpackException is a custom exception raised to indicate that an unpacking
  operation found no argument requiring unpacking. This is raised by the
  'unpack' function in the 'worktoy.core' module when the 'strict' mode is
  enabled and no iterable is found among the arguments. Please note that
  this function does not consider strings or bytes as unpackable iterables.
  """

  __slots__ = ('posArgs',)

  def __init__(self, *args) -> None:
    """
    Initialize the UnpackException with an optional message.
    """
    self.posArgs = args
    ValueError.__init__(self, )

  def __str__(self) -> str:
    """
    Return a string representation of the UnpackException.
    """
    infoSpec = """'unpack' found no iterable argument from: \n'%s'\nand is 
    running in strict mode (default). Change this by setting keyword 
    argument 'strict' to False."""
    argStr = '\n  '.join([str(arg) for arg in self.posArgs])
    info = infoSpec % argStr
    return textFmt(info)

  __repr__ = __str__
