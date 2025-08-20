"""
DescriptorException provides a base class for the exceptions raised by
descriptors. By having a shared base class, the 'Object' class is able to
recognize situations where a descriptor has raised an exception. These
exceptions propagate *without* being passed to the fallback method.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  pass


class DescriptorException(Exception):
  """
  Base class for exceptions raised by descriptors.
  """
  pass
