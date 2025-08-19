"""
UnorderedEZException provides a custom exception raised when attempting to
sort an EZData subclass not supporting ordering. This is either because
the 'isOrdered' attribute is specifically set to False (default is True),
or if the subclass owns a field of a type that does not support ordering.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class UnorderedEZException(TypeError):
  """
  UnorderedEzException provides a custom exception raised when attempting to
  sort an EZData subclass not supporting ordering. This is either because
  the 'isOrdered' attribute is specifically set to False (default is True),
  or if the subclass owns a field of a type that does not support ordering.
  """

  __slots__ = ('className', 'fieldName', 'fieldType')

  def __init__(self, *args) -> None:
    """
    Initialize the UnorderedEzException exception.

    :param className: The name of the EZData subclass that is unordered.
    :param fieldName: Optional name of the field that does not support
    ordering.
    """
    cls, fName, fType, *_ = [*args, None, None]
    self.className = getattr(cls, '__name__', cls)
    self.fieldName, self.fieldType = None, None
    if fType is not None:
      self.fieldType = fType
      self.fieldName = fName
    TypeError.__init__(self, )

  def _isOrderedStr(self) -> str:
    """When 'isOrdered' is 'False'."""
    infoSpec = """Attempted to sort EZData subclass '%s' which has the 
    'order' class keyword set to 'False'. """
    info = infoSpec % self.className
    from worktoy.utilities import textFmt
    return textFmt(info, )

  def _fieldOrderedStr(self) -> str:
    """When a field does not support ordering."""
    infoSpec = """Attempted to sort EZData subclass '%s' which has the 
    field '%s' of type: '%s' that does not support ordering. """
    clsName = self.className
    fName = self.fieldName
    typeName = self.fieldType.__name__
    info = infoSpec % (clsName, fName, typeName)
    return textFmt(info, )

  def __str__(self) -> str:
    if self.fieldName is None or self.fieldType is None:
      return self._isOrderedStr()
    return self._fieldOrderedStr()

  __repr__ = __str__
