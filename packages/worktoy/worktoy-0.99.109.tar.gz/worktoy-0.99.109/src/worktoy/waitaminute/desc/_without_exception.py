"""
WithoutException provides a custom exception raised to indicate that a
context-only method called without descriptor-context.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class WithoutException(RuntimeError):
  """
  WithoutException provides a custom exception raised to indicate a call
  without context made to a context-only method.
  """

  __slots__ = ('desc',)

  def __init__(self, desc: Any) -> None:
    self.desc = desc
    RuntimeError.__init__(self, )

  def __str__(self, ) -> str:
    infoSpec = """Context-less call detected for descriptor at '%s.%s'!"""
    fbOwner = 'NO-OWNER'
    ownerName = getattr(self.desc.getFieldOwner(), '__name__', fbOwner)
    fbName = 'NO-FIELD'
    from worktoy.utilities import maybe
    fieldName = maybe(self.desc.getFieldName(), fbName)
    info = infoSpec % (ownerName, fieldName)
    return info

  __repr__ = __str__
