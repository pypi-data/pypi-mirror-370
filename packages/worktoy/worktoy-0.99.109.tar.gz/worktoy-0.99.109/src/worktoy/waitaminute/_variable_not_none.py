"""VariableNotNone should be raised when a variable is unexpectedly not
None."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class VariableNotNone(Exception):
  """VariableNotNone should be raised when a variable is unexpectedly not
  None."""

  __slots__ = ('name', 'value')

  def __init__(self, *args) -> None:
    """Initialize the VariableNotNone object."""
    self.name, self.value, *_ = [*args, None, None]
    Exception.__init__(self, )

  def __str__(self, ) -> str:
    """Get the info spec."""
    infoSpec = """Unexpected value: '%s' at name '%s' expected to be 
    None!"""
    valueStr = textFmt(str(self.value), )
    name = self.name
    return textFmt(infoSpec % (valueStr, name), )

  __repr__ = __str__
