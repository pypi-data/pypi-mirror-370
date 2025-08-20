"""
EZDeleteException provides a custom exception class raised to indicate an
attempt to delete a field in an EZData subclass. EZData subclasses do not
allow deletion of fields.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class EZDeleteException(TypeError):
  """
  EZDeleteException provides a custom exception class raised to indicate an
  attempt to delete a field in an EZData subclass. EZData subclasses do not
  allow deletion of fields.
  """

  __slots__ = ('name', 'cls')

  def __init__(self, cls: type, name: str, ) -> None:
    self.cls = cls
    self.name = name
    TypeError.__init__(self, )

  def __str__(self) -> str:
    infoSpec = """Attempted to delete field '%s' in EZData subclass '%s'. 
    EZData subclasses do not allow deletion of fields. """
    fName = self.name
    clsName = self.cls.__name__
    info = infoSpec % (fName, clsName)
    return textFmt(info, )

  __repr__ = __str__
