"""
DelException is a custom exception raised when someone attempts to create
a class that implements the '__del__' method without providing the custom
keyword argument: 'trustMeBro=True'.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class DelException(SyntaxError):
  """
  DelException is a custom exception raised when someone attempts to create
  a class that implements the '__del__' method without providing the custom
  keyword argument: 'trustMeBro=True'.
  """
  __slots__ = ('mcls', 'name', 'bases', 'space')

  def __init__(self, *args) -> None:
    """Initialize the DelException with the class."""
    self.mcls, self.name, self.bases, self.space = args
    SyntaxError.__init__(self, )

  def __str__(self) -> str:
    """Return a string representation of the DelException."""
    infoSpec = """When attempting to derive a class named '%s' from the 
    metaclass '%s', the '__del__' method was found in the namespace! This 
    is almost always a typo, but if not this error can be suppressed by 
    passing the keyword argument 'trustMeBro=True' during class creation. """
    if TYPE_CHECKING:  # pragma: no cover
      assert isinstance(self.bases, tuple)
    if self.bases:
      mclsSpec = """%s with bases: (%s)"""
    else:
      mclsSpec = """%s%s"""
    basesStr = ', '.join(base.__name__ for base in self.bases)
    mclsName = mclsSpec % (self.mcls.__name__, basesStr)
    info = infoSpec % (self.name, mclsName)
    return textFmt(info, )

  __repr__ = __str__
