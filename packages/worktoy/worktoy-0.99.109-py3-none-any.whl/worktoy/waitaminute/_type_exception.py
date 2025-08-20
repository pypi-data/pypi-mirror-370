"""TypeException is a custom exception class for handling type related
errors. Specifically, this exception should NOT be raised if the object is
None instead of the expected type. This is because None indicates absense
rather than type mismatch. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt, joinWords

if TYPE_CHECKING:  # pragma: no cover
  pass


class TypeException(TypeError):
  """
  TypeException is a custom exception class for handling type related
  errors. Specifically, this exception should NOT be raised if the object is
  None instead of the expected type.
  """

  __slots__ = ('varName', 'actualObject', 'actualType', 'expectedTypes',)

  def __init__(self, name: str, obj: object, *types) -> None:
    """Initialize the TypeException with the name of the variable, the
    received object, and the expected types."""
    TypeError.__init__(self, )
    self.varName = name
    self.actualObject = obj
    self.actualType = type(obj)
    self.expectedTypes = types

  def __str__(self) -> str:
    """String representation of the TypeException."""
    infoSpec = """Expected object at name '%s' to be an instance of %s, 
    but received object: '%s' of type '%s'!"""
    typeNames = [t.__name__ for t in self.expectedTypes]
    typeStr = joinWords(*["""'%s'""" % name for name in typeNames], set='or')
    objStr = repr(self.actualObject)
    if len(objStr) > 50:
      objStr = """%s...""" % objStr[:47]
    clsType = type(self.actualObject).__name__
    info = infoSpec % (self.varName, typeStr, objStr, clsType)
    return textFmt(info)

  __repr__ = __str__
