"""
MissingVariable is a custom exception class raise to indicate that a
variable has not been assigned a value when accessed. Generally indicates
that the variable has no fallback value.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class MissingVariable(AttributeError):
  """MissingVariable is a custom exception class raise to indicate that a
  variable has not been assigned a value when accessed. Generally indicates
  that the variable has no fallback value."""

  __slots__ = ('name', 'instance', 'type_')

  def __init__(self, instance: Any, name: str, type_: type) -> None:
    self.name = name
    self.instance = instance
    self.type_ = type_
    AttributeError.__init__(self, )

  def __str__(self) -> str:
    infoSpec = """Missing variable '%s' of type '%s' in instance '%s'!"""
    instanceName = getattr(self.instance, '__name__', 'Unknown')
    info = infoSpec % (self.name, self.type_.__name__, instanceName)
    return textFmt(info)

  __repr__ = __str__
