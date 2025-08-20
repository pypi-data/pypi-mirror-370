"""
TypeCastException is a custom exception class raised by the 'typeCast'
function from the 'worktoy.static' module to indicate that a value could
not be cast to the target type.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class TypeCastException(TypeError):
  """
  TypeCastException is a custom exception class raised by the 'typeCast'
  function from the 'worktoy.static' module to indicate that a value could
  not be cast to the target type.
  """

  __slots__ = ('type_', 'arg')

  def __init__(self, type_: type, arg: Any) -> None:
    """Initialize the TypeCastException with the value and target type."""
    self.type_ = type_
    self.arg = arg
    TypeError.__init__(self, )

  def __str__(self) -> str:
    """Get the string representation of the exception."""
    infoSpec = """Unable to cast value '%s' to type '%s'!"""
    typeStr = self.type_.__name__
    argStr = str(self.arg)
    info = infoSpec % (argStr, typeStr)
    from ...utilities import textFmt
    return textFmt(info)

  __repr__ = __str__
