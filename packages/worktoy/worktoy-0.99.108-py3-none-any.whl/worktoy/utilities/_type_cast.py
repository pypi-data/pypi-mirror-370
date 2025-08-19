"""
TypeCast encapsulates the logic for instantiating a type from arguments.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


def typeCast(target: type, arg: Any) -> Any:
  """
  Casts the given argument to the specified type, with the following
  special exceptions made for particular target types:
  - If the target is 'str', the given argument must be a 'str' object or
  one of 'bytes' or 'bytearray' that can be decoded to a 'str'. Otherwise,
  raises TypeCastException.
  - If the target is 'bool', the given argument must be one of the four
  following objects: 0, 1, True, or False. Otherwise, raises
  TypeCastException.
  - Target 'int' accepts args of the following types:
    - 'int' (returns the same value)
    - 'float' returns int(arg) if float.is_integer(arg), otherwise raises
    TypeCastException.
    - 'complex' returns int(arg.real) if arg.imag is 0 and
    float.is_integer(arg.real), otherwise raises TypeCastException.
    - 'str' uses try, except, else flow attempting to cast the string to
    'int' with int(arg). If this raises any exception, TypeCastException
    raises from that exception. Else the cast value is returned.
  - Target 'float' accepts args of the following types:
    - 'float' (returns the same value)
    - 'int' returns float(arg) for every integer arg.
    - 'complex' returns float(arg.real) if arg.imag is 0, otherwise raises
    TypeCastException.
    - 'str' uses try, except, else flow attempting to cast the string to
    'float' with float(arg). If this raises any exception, TypeCastException
    raises from that exception. Else the cast value is returned.
  - Target 'complex' accepts args of the following types:
    - 'complex' (returns the same value)
    - 'int' returns float(arg) + 0j.
    - 'float' returns float(arg) + 0j.
    - 'str' uses try, except, else flow attempting to cast the string to
    'complex' with complex(arg). If this raises any exception,
    TypeCastException raises from that exception. Else the cast value is
    returned.
  - Target 'list' accepts args of the following types:
    - 'list' (returns the same value)
    - 'tuple' returns list(arg).
    - 'set' returns list(arg).
    - 'frozenset' returns list(arg).
    - 'dict' returns list(dict.items(arg)).
  - Target 'tuple' accepts the exact same types as 'list' but returns a
  tuple instead of a list.
  - Target 'set' accepts the exact same types as 'list' but returns a set
  instead of a list.
  - Target 'frozenset' accepts the exact same types as 'list' but returns a
  frozenset instead of a list.
  - Target 'dict' accepts only other dictionary-like objects. This is
  achieved by a try, except, else flow attempting to: {**arg,}. If any
  exception is caught, TypeCastException raises from that exception.
  - Target 'type' accepts only classes, as defined by isinstance(arg, type).
  - Target 'Func' accepts nothing. Not even other functions.
  - For all other target types, if the argument is not an instance of
  the target type, it is attempted to be cast to the target type using
  the target type's constructor. If this raises any exception, a
  TypeCastException is raised from that exception.
  """
  if isinstance(arg, target):
    return arg
  if target is type:
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is str:
    if isinstance(arg, (bytes, bytearray)):
      try:
        return arg.decode('utf-8')
      except Exception as exception:
        from worktoy.waitaminute.dispatch import TypeCastException
        raise TypeCastException(target, arg) from exception
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is bool:
    if arg in (True, False, 0, 1):
      return bool(arg)
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is int:
    if isinstance(arg, float):
      if float.is_integer(arg):
        return int(arg)
      from worktoy.waitaminute.dispatch import TypeCastException
      raise TypeCastException(target, arg)
    if isinstance(arg, complex):
      if arg.imag == 0 and float.is_integer(arg.real):
        return int(arg.real)
      from worktoy.waitaminute.dispatch import TypeCastException
      raise TypeCastException(target, arg)
    if isinstance(arg, str):
      try:
        return int(arg)
      except Exception as exception:
        from worktoy.waitaminute.dispatch import TypeCastException
        raise TypeCastException(target, arg) from exception
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is float:
    if isinstance(arg, int):
      return float(arg)
    if isinstance(arg, complex):
      if arg.imag == 0:
        return float(arg.real)
      from worktoy.waitaminute.dispatch import TypeCastException
      raise TypeCastException(target, arg)
    if isinstance(arg, str):
      try:
        return float(arg)
      except Exception as exception:
        from worktoy.waitaminute.dispatch import TypeCastException
        raise TypeCastException(target, arg) from exception
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is complex:
    if isinstance(arg, (int, float)):
      return float(arg) + 0j
    if isinstance(arg, str):
      try:
        return complex(arg)
      except Exception as exception:
        from worktoy.waitaminute.dispatch import TypeCastException
        raise TypeCastException(target, arg) from exception
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is list:
    if isinstance(arg, (tuple, set, frozenset)):
      return list(arg)
    if isinstance(arg, dict):
      return [(k, v) for k, v in arg.items()]
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is tuple:
    if isinstance(arg, (list, set, frozenset)):
      return tuple(arg)
    if isinstance(arg, dict):
      return tuple((k, v) for k, v in arg.items())
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is set:
    if isinstance(arg, (list, tuple, frozenset)):
      return set(arg)
    if isinstance(arg, dict):
      return set((k, v) for k, v in arg.items())
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is frozenset:
    if isinstance(arg, (list, tuple, set)):
      return frozenset(arg)
    if isinstance(arg, dict):
      return frozenset((k, v) for k, v in arg.items())
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg)
  if target is dict:
    try:
      return {**arg}
    except Exception as exception:
      from worktoy.waitaminute.dispatch import TypeCastException
      raise TypeCastException(target, arg) from exception
  try:
    return target(arg)
  except Exception as exception:
    from worktoy.waitaminute.dispatch import TypeCastException
    raise TypeCastException(target, arg) from exception
