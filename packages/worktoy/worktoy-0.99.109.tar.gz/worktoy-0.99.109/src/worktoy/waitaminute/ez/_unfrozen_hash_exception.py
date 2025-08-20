"""
UnfrozenHashException provides a custom exception class raised to indicate
that an attempt was made to hash an instance of an EZData subclass that is
not frozen. This means that the 'isFrozen' flag was False (default is
False). Please note that only frozen EZData subclasses can be hashed.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class UnfrozenHashException(TypeError):
  """
  UnfrozenHashException provides a custom exception class raised to indicate
  that an attempt was made to hash an instance of an EZData subclass that is
  not frozen. This means that the 'isFrozen' flag was False (default is
  False). Please note that only frozen EZData subclasses can be hashed.
  """

  __slots__ = ('className',)

  def __init__(self, className: str) -> None:
    self.className = className
    TypeError.__init__(self, )

  def __str__(self) -> str:
    infoSpec = """Attempted to hash EZData subclass '%s' which is not 
    frozen. Only frozen EZData subclasses can be hashed. """
    info = infoSpec % self.className
    return textFmt(info, )

  __repr__ = __str__
