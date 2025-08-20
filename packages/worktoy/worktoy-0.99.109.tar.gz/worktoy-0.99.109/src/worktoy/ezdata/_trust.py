"""
The 'trust' function decorates functions to indicate that they should be
ignored by the class creation process. It sets an attribute '__is_root__'
to True, which is treated as a signal to several space hook classes to
ignore the function. Decorated functions will not be available at runtime.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Callable


def trust(callMeMaybe: Callable) -> Callable:
  """Please note, that decorated functions will not be available at
  runtime. """
  setattr(callMeMaybe, '__is_root__', True)
  return callMeMaybe
