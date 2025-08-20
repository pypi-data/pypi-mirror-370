"""
DELETED indicates deletion. If any 'object.__getattribute__' would return
DELETED, it should instead raise an AttributeError. The core classes in
the 'worktoy.core' module implements this behaviour. The example below
illustrates the motivation behind this sentinel.

A descriptor class implements a default value that descriptor objects
return if the normal __get__ is not able to find a value on a given
owning instance. Each descriptor object may have its own default value,
but if not, the class provides a fallback value. Thus, when accessing
the descriptor described in this example, the descriptor attempts three
separate lookups:
1.  from the instance passed to __get__
2.  a default value set on the descriptor object itself
3.  the fallback value set on the descriptor class itself

Instead of requiring handling three different lookups, the '__delete__'
functionality may be implemented by 'setting' the descriptor to the
DELETED sentinel. Then, the first lookup finds the DELETED sentinel,
which signals the 'Desc.__get__' method to raise 'AttributeError'.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Sentinel

if TYPE_CHECKING:  # pragma: no cover
  pass


class DELETED(Sentinel):
  """
  DELETED should raise an AttributeError
  """
  pass
