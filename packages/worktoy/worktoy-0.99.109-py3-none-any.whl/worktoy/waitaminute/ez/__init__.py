"""
The 'worktoy.waitaminute.ez' module provides custom exception classes used
by the 'worktoy.ezdata' module.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._ez_multiple_inheritance import EZMultipleInheritance
from ._unordered_ez_exception import UnorderedEZException
from ._unfrozen_hash_exception import UnfrozenHashException
from ._frozen_ez_exception import FrozenEZException
from ._ez_delete_exception import EZDeleteException

___all__ = [
    'EZMultipleInheritance',
    'UnorderedEZException',
    'UnfrozenHashException',
    'FrozenEZException',
    'EZDeleteException',
]
