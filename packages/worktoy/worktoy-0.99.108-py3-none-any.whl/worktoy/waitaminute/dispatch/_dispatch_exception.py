"""DispatchException provides a custom exception raised when an instance
of OverloadDispatcher fails to resolve the correct function from the
given arguments. Because the overload protocol relies on type matching,
this exception subclasses TypeError such that it can be caught by external
error handlers. """
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, TypeAlias

  Args: TypeAlias = tuple[Any, ...]
  Excs: TypeAlias = tuple[Exception, ...]

  from worktoy.dispatch import Dispatcher


class DispatchException(TypeError):
  """DispatchException provides a custom exception raised when an instance
  of OverloadDispatcher fails to resolve the correct function from the
  given arguments. Because the overload protocol relies on type matching,
  this exception subclasses TypeError such that it can be caught by external
  error handlers. """

  __slots__ = ('dispatch', 'args', 'excs')

  def __init__(self, dispatch: Dispatcher, args: Args, ) -> None:
    self.dispatch = dispatch
    self.args = args
    TypeError.__init__(self, )

  def __str__(self) -> str:
    """
    Return a string representation of the DispatchException.
    """
    infoSpec = """Dispatcher object: '%s' failed to dispatch arguments: 
    <br><tab>%s<br><tab>matching type signature: '%s'<br>"""
    dispStr = str(self.dispatch)
    argsStr = ', '.join(str(arg) for arg in self.args)
    from ...dispatch import TypeSig
    typeStr = str(TypeSig.fromArgs(*self.args))
    info = infoSpec % (dispStr, argsStr, typeStr)
    return textFmt(info, )

  __repr__ = __str__
