"""
The 'worktoy.dispatch' package provides the overload functionality used
across the 'worktoy' library. It provides the central 'Dispatch' class
which facilitates mapping from type signatures to function objects.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._type_sig import TypeSig
from ._dispatcher import Dispatcher
from ._overload import overload, overload

__all__ = [
    'TypeSig',
    'Dispatcher',
    'overload',
    'overload',
]
