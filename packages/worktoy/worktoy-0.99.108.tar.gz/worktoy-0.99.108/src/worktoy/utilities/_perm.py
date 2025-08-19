"""
perm: Efficient unique permutation generator.

This module provides the function `perm`, which yields all unique
permutations of its input arguments. The function works efficiently even
when the input contains duplicate elements, producing each unique ordering
exactly once.

Usage example:
  for p in perm('Tom', 'Tom', 'Harry'):
    print(p)
  # Outputs:
  # ('Tom', 'Tom', 'Harry')
  # ('Tom', 'Harry', 'Tom')
  # ('Harry', 'Tom', 'Tom')

The generator approach allows iteration over permutations without building
the entire result list in memory, making it suitable for large or memory-
constrained applications.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Iterator


def perm(*items: Any) -> Iterator[tuple[Any, ...]]:
  if not items:
    yield items
  dupes, dupe = [], lambda x: x in dupes or list.append(dupes, x)
  for j, t in enumerate(items):
    if not dupe(t):
      yield from [(t,) + p for p in perm(*items[:j], *items[j + 1:])]
