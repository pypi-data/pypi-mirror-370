"""
ReservedNameHook protects reserved names from being overridden.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...waitaminute.meta import ReservedName
from . import AbstractSpaceHook, ReservedNames

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class ReservedNamespaceHook(AbstractSpaceHook):
  """
  ReservedNameHook prevents redefinition of names that are reserved for
  use by Python or the metaclass system. These names are typically
  populated automatically during class construction and must not be
  reassigned by user code.

  ## Protected Names

  The following names are treated as reserved:

  - `__dict__`              – Internal attribute dictionary
  - `__weakref__`           – Weak reference support slot
  - `__module__`            – Name of the module defining the class
  - `__annotations__`       – Type hint storage
  - `__match_args__`        – Structural pattern matching
  - `__doc__`               – Docstring
  - `__name__`              – Class name
  - `__qualname__`          – Fully qualified class name
  - `__firstlineno__`       – Source line for class definition
  - `__static_attributes__` – Internal metadata used by the metaclass

  ## Behavior

  During namespace population (i.e., when a class body assigns names),
  any attempt to override a name in the reserved list will raise a
  ReservedName exception — *but only if* the name already exists in the
  namespace. This prevents accidental clobbering of values while still
  allowing deferred initialization.

  ## Usage
  To use NameHook, simply declare it in your namespace class:

  class Space(AbstractNamespace):  # Must inherit from AbstractNamespace
    #  Custom namespace class inheriting from AbstractNamespace
    reservedNameHook = ReservedNameHook()  # Register the hook
"""

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Public variables
  reservedNames = ReservedNames()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def setItemPhase(self, key: str, val: Any, old: Any = None, ) -> bool:
    """
    The setItemHook method is called when an item is set in the
    namespace.
    """
    if key in self.reservedNames:
      if key in self.space:
        raise ReservedName(key)
    return False
