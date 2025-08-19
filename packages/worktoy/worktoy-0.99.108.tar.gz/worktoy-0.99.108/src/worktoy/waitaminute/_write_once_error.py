"""WriteOnceError is a custom error class raised to indicate that a
variable was attempted to be written to more than once."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any

  from worktoy.core import Object


class WriteOnceError(TypeError):
  """WriteOnceError is a custom error class raised to indicate that a
  variable was attempted to be written to more than once."""

  __slots__ = ('desc', 'oldValue', 'newValue')

  def __init__(self, desc: Object, oldVal: Any, newVal: Any) -> None:
    self.desc = desc
    self.oldValue = oldVal
    self.newValue = newVal
    TypeError.__init__(self, )

  def __str__(self) -> str:
    infoSpec = """Attempted to overwrite write-once attribute at '%s.%s' 
    having existing value: '%s' with new value: '%s'!"""
    owner = getattr(self.desc, '__field_owner__', object())  # no __name__
    ownerName = getattr(owner, '__name__', 'Unknown')
    fieldName = getattr(self.desc, '__field_name__', 'Unknown')
    oldStr = str(self.oldValue)
    newStr = str(self.newValue)
    info = infoSpec % (ownerName, fieldName, oldStr, newStr)
    return textFmt(info)

  __repr__ = __str__
