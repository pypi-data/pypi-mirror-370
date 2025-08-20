"""
The 'unpack' function squeezes a tuple of arguments until no array like
member remains.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


def unpack(*args: Any, **kwargs) -> tuple[Any, ...]:
  """
  Recursively unpacks iterables from positional arguments.

  This function traverses the given positional arguments and flattens
  any array-like values (iterables), except for str and bytes, which
  are treated as atomic.

  Supported keyword arguments:

  - shallow (bool, default False):
    If True, only unpacks the first level of nested iterables.

  - strict (bool, default True):
    If True, raises ValueError if no iterable argument was found.
    If False, returns arguments unchanged if no iterable is found.

  Args:
    *args: Positional arguments to unpack.
    **kwargs: Optional 'shallow' and 'strict' flags.

  Returns:
    tuple[Any, ...]: A flattened tuple of arguments.

  Raises:
    ValueError: If strict is True and no iterable was found.
  """
  if not args:
    if kwargs.get('strict', True):
      from worktoy.waitaminute import UnpackException
      raise UnpackException(*args, )
    return ()
  out = []
  iterableFound = False
  for arg in args:
    if isinstance(arg, (str, bytes,)):
      out.append(arg)
      continue
    if isinstance(arg, Iterable):
      if kwargs.get('shallow', False):
        out.extend(arg)
      else:
        out = [*out, *unpack(*arg, shallow=False, strict=False)]
      iterableFound = True
      continue
    out.append(arg)
  if iterableFound or not kwargs.get('strict', True):
    return (*out,)
  from worktoy.waitaminute import UnpackException
  raise UnpackException(*args, )
