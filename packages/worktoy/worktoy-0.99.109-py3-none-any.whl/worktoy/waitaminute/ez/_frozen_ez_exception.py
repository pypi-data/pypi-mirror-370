"""
FrozenEZException provides a custom exception class raised to indicate an
attempt to change the value of a field in an EZData subclass that is
frozen, meaning it is immutable.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class FrozenEZException(TypeError):
  """
  FrozenEZException provides a custom exception class raised to indicate an
  attempt to change the value of a field in an EZData subclass that is
  frozen, meaning it is immutable.
  """

  __slots__ = ('fieldName', 'className', 'oldValue', 'newValue')

  def __init__(self, *args) -> None:
    fName, clsName, old, new_, *_ = [*args, None, None, None]
    self.fieldName = fName
    self.className = clsName
    self.oldValue = old
    self.newValue = new_
    TypeError.__init__(self, )

  def __str__(self) -> str:
    infoSpec = """Attempted to set value of field '%s' in frozen EZData 
    subclass: '%s' from '%s' to '%s'. """
    fName = self.fieldName
    clsName = self.className
    oldStr = repr(self.oldValue)
    newStr = repr(self.newValue)
    info = infoSpec % (fName, clsName, oldStr, newStr)
    return textFmt(info, )

  __repr__ = __str__
