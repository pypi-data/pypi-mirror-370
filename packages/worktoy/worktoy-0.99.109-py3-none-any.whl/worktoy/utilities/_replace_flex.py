"""
The 'replaceFlex' function provides a vastly superior alternative to the
'str.replace' function.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import maybe


def replaceFlex(text: str, old: str, new: str, n: int = None) -> str:
  """
  Replaces only the nth occurrence of 'old' with 'new' in text.
  n is 1-based.
  """
  n = maybe(n, 1)
  i = -1
  for _ in range(n):
    i = text.find(old, i + 1)
    if i == -1:
      return text
  return text[:i] + new + text[i + len(old):]
