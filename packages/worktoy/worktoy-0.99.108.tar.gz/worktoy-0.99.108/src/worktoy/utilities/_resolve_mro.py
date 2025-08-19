"""
The 'resolveMRO' function takes any number of classes and creates a tuple
of classes having the same method resolution order (MRO) as a potential
new class inheriting from all of the in the order passed. For example,

class Foo(Tom, Dick, Harry):
  pass

predictedMRO = resolveMRO(Tom, Dick, Harry)
actualMRO = Foo.mro()
predictedMRO == actualMRO
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import joinWords, textFmt

if TYPE_CHECKING:  # pragma no cover
  pass


def resolveMRO(*bases: type, **kwargs) -> list[type]:
  if not bases:
    return []
  if len(bases) == 1:
    return [*bases[0].__mro__, ]
  baseMROs = [base.__mro__ for base in bases]
  maxC = sum([sum([1 for _ in b], ) for b in baseMROs])
  out = []
  _c = kwargs.get('_start', 0)
  while baseMROs:
    for baseMRO in baseMROs:
      base = baseMRO[0]
      tailMROs = [b for b in baseMROs if len(b) > 1]
      tailMROs = [b[1:] for b in tailMROs]
      for tail in tailMROs:
        if base in tail:
          break
      else:
        break
    else:
      infoSpec = """The bases received: (%s) cannot form a consistent mro!"""
      baseNames = joinWords(*[b.__name__ for b in bases], )
      info = textFmt(infoSpec % baseNames)
      raise TypeError(info)
    maybeEmpty = [[b for b in bs if b is not base] for bs in baseMROs]
    baseMROs = [b for b in maybeEmpty if b]
    out.append(base)
    _c += 1
    if _c > maxC:
      break
  else:
    return out
  raise RecursionError
