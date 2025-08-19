"""
The 'stringList' takes a string and returns a list of strings containing
substrings separated by a separator (default: ', ').

Keyword argument 'sep' specifies the separator(s) to use. More than one
separator may be specified by passing a non-empty iterable of strings.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations


def stringList(*args: str, **kwargs) -> list[str]:
  """
  Splits input strings using all provided separators in sequence.

  Keyword-only argument 'sep' may be a string or list of strings. Each
  separator is applied in turn, so that later separators act on results
  of earlier splits.
  """
  sep = kwargs.get('separator', ', ')
  if isinstance(sep, str):
    out = []
    for arg in args:
      out.extend(arg.split(sep))
    return [a.strip() for a in out if a.strip()]
  if isinstance(sep, (list, tuple)):
    out = [*args, ]
    for s in sep:
      out = stringList(*out, separator=s)
    return [a.strip() for a in out if a.strip()]
  from ..waitaminute import TypeException
  raise TypeException('separator', sep, str, list, tuple)
