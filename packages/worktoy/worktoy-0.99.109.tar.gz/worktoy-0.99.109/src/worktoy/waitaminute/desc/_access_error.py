"""
AccessError is raised when a descriptor does not provide a way to retrieve
a requested value. This exception is raised by 'Desc' and its subclasses
failing to implement '__instance_get__' or which falls back to the parent
implementation under certain conditions.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import DescriptorException
from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class AccessError(DescriptorException, AttributeError):
  """
  AccessError is raised when a descriptor does not provide a way to retrieve
  a requested value. This exception is raised by 'Desc' and its subclasses
  failing to implement '__instance_get__' or which falls back to the parent
  implementation under certain conditions.
  """

  __slots__ = ('desc',)

  def __init__(self, desc) -> None:
    """
    Initializes the AccessError with the class that failed to provide a
    value.
    """
    self.desc = desc
    DescriptorException.__init__(self, )

  def __str__(self) -> str:
    """
    Returns a string representation of the AccessError.
    """
    infoSpec = """The '%s' descriptor at '%s.%s' failed to retrieve a 
    value!"""
    descTypeName = type(self.desc).__name__
    ownerName = self.desc.__field_owner__.__name__
    fieldName = self.desc.__field_name__
    info = infoSpec % (descTypeName, ownerName, fieldName)
    return textFmt(info)

  __repr__ = __str__
