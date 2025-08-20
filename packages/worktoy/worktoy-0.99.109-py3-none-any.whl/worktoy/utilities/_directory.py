"""
Dir provides a descriptor identifying the file from which the owner
received by __get__ is imported.

Please note, that the file is returned
only when the descriptor is accessed through an instance. If accessed
through the class, the descriptor object returns itself.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import sys
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Never


class Directory:
  """
  A descriptor that returns the directory of the file containing the
  instance accessing it.
  """

  def __get__(self, instance: Any, owner: type) -> Any:
    """
    Returns the directory of the file containing the instance accessing it.
    """
    if instance is None:
      return self
    module = sys.modules.get(instance.__class__.__module__)
    filePath = getattr(module, '__file__')
    return os.path.abspath(os.path.dirname(filePath))

  def __set__(self, instance: Any, value: Any, **kwargs) -> Never:
    from worktoy.waitaminute.desc import ReadOnlyError
    raise ReadOnlyError(instance, self, value, )

  def __delete__(self, instance: Any, **kwargs) -> Never:
    from worktoy.waitaminute.desc import ProtectedError
    raise ProtectedError(self, instance, )
