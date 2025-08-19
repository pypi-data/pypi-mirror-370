"""
DuplicateHookError is a custom exception raised when an attempt is made to
register a hook at a name already populated with a hook. If 'oldHook is
newHook' is True, this exception may not be appropriate.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class DuplicateHook(Exception):
  """
  DuplicateHookError is a custom exception raised when an attempt is made to
  register a hook at a name already populated with a hook. If 'oldHook is
  newHook' is True, this exception may not be appropriate.
  """

  __slots__ = ('owner', 'name', 'existingHook', 'newHook')

  def __init__(self, *args, ) -> None:
    _owner, _name, _oldHook, _newHook = [*args, None, None, None, None][:4]
    self.owner = _owner
    self.name = _name
    self.existingHook = _oldHook
    self.newHook = _newHook
    Exception.__init__(self, )

  def __str__(self) -> str:
    """
    String representation of the exception.
    """
    infonSpec = """The class '%s' already has a hook registered 
    at name: '%s'! The existing hook is '%s', and the new hook is '%s'."""
    ownerName = self.owner.__name__
    oldHook = str(self.existingHook)
    newHook = str(self.newHook)
    info = infonSpec % (ownerName, self.name, oldHook, newHook)
    return textFmt(info)

  __repr__ = __str__
