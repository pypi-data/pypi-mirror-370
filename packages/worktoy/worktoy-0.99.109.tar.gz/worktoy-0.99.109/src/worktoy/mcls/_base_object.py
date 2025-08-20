"""
BaseObject is the standard entry point for using the worktoy library.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import BaseMeta
from ..core import Object

if TYPE_CHECKING:  # pragma: no cover
  pass


class BaseObject(Object, metaclass=BaseMeta):
  """
  BaseObject combines the core functionality of Object with the
  hook-based metaclass behavior of BaseMeta.

  From Object, it inherits robust constructor handling, controlled
  descriptor mutation, and context-aware access to instance and owner
  information. From BaseMeta, it gains support for function overloading
  and other hook-based class construction features via BaseSpace.

  Subclass this when you want both: sane, safe object semantics and
  overload-aware metaclass support.
  """
  pass
