"""SubclassException should be raised when a class is not a subclass of
the expected base class. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class SubclassException(TypeError):
  """SubclassException should be raised when a class is not a subclass of
  the expected base class."""

  __slots__ = ('cls', 'expected')

  def __init__(self, cls: type, base: type) -> None:
    """Initialize the exception with the object and expected base class."""
    self.cls, self.expected = cls, base
    TypeError.__init__(self, )

  def __str__(self) -> str:
    """
    Return a string representation of the SubclassException object.
    """
    infoSpec = """Expected class '%s' to be a subclass of '%s'!"""
    clsName = type(self.cls).__name__
    baseName = type(self.expected).__name__
    info = infoSpec % (clsName, baseName)
    return textFmt(info)

  __repr__ = __str__
