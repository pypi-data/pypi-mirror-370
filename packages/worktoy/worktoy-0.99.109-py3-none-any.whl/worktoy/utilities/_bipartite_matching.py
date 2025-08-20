"""
The 'bipartiteMatching' function solves the bipartite matching problem by
recursive backtracking with forward checking returns the first encountered
valid mapping.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, TypeAlias

  SlotInts: TypeAlias = dict[Any, tuple[int, ...]]
  SlotMap: TypeAlias = dict[Any, int]


def bipartiteMatching(slots: list[tuple[int, ...]]) -> list[int]:
  """
  Recursive backtracking with forward checking. Given a list of tuples
  of candidate indices, one per slot, finds an assignment of one unique
  index to each slot, with no repeats. Returns list of assigned indices,
  or raises ValueError if no solution exists.
  """
  # Base case: success
  if not slots:
    return []

  # Step 1: fail if any empty
  for opts in slots:
    if not opts:
      raise ValueError('No valid assignment for slot')

  # Step 2: pick slot with fewest options
  idx, opts = min(enumerate(slots), key=lambda x: len(x[1]))

  # Step 3: try each option
  for value in opts:
    # Build reduced slots
    reduced = []
    for j, otherOpts in enumerate(slots):
      if j == idx:
        continue
      reducedOpts = tuple(v for v in otherOpts if v != value)
      reduced.append(reducedOpts)
    try:
      result = bipartiteMatching(reduced)
    except ValueError:
      continue
    # Rebuild full result
    result = result[:idx] + [value] + result[idx:]
    return result

  raise ValueError('No valid assignment for slot %d' % idx)
