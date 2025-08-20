"""
The 'worktoy.waitaminute.meta' provides the custom exceptions used by the
class creation flow in 'worktoy.core'.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._illegal_instantiation import IllegalInstantiation
from ._hook_exception import HookException
from ._duplicate_hook import DuplicateHook
from ._metaclass_exception import MetaclassException
from ._del_exception import DelException
from ._questionable_syntax import QuestionableSyntax
from ._reserved_name import ReservedName

__all__ = [
    'DuplicateHook',
    'IllegalInstantiation',
    'HookException',
    'MetaclassException',
    'DelException',
    'QuestionableSyntax',
    'ReservedName',
]
