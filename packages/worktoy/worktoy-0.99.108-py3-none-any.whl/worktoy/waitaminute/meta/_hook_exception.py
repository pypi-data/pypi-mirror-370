"""
HookException is raised from the AbstractNamespace class to wrap
exceptions raised by __getitem__ hooks. This is necessary to avoid
confusion with the expected KeyError exception in the metacall system.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from worktoy.mcls import AbstractNamespace
  from worktoy.mcls.space_hooks import AbstractSpaceHook


class HookException(Exception):
  """
  This custom exception allows get item hooks to interrupt calls to
  __getitem__. Because the metacall system requires the __getitem__ to
  specifically raise a KeyError in certain situations, an exception raised
  by a hook might be confused for the KeyError. Instead,
  the AbstractNamespace class will catch exceptions raised by hooks and
  raise them from this exception:
  For example:
  try:
    hook(self, key, val)
  except Exception as exception:
    raise HookException(exception) from exception
  """

  __slots__ = (
      'initialException',
      'namespaceObject',
      'itemKey',
      'errorValue',
      'hookFunction'
  )

  def __init__(
      self,
      exception: Exception,
      namespace: AbstractNamespace,
      key: str,
      val: object,
      hook: AbstractSpaceHook,
  ) -> None:
    self.initialException = exception
    self.namespaceObject = namespace
    self.itemKey = key
    self.errorValue = val
    self.hookFunction = hook
    Exception.__init__(self, )

  def __str__(self) -> str:
    """
    String representation of the HookException.
    """
    spec = """HookException raised from %s! Key: '%s', Value: '%s', 
    Hook: '%s'! Initial exception: %s"""
    cls = type(self).__name__
    info = spec % (
        self.namespaceObject, self.itemKey, self.errorValue,
        self.hookFunction, self.initialException
    )
    return textFmt(info)

  __repr__ = __str__
