"""
The 'worktoy.mcls.space_hooks' package provides the hooks used by the
Namespace system.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._space_desc import SpaceDesc
from ._reserved_names import ReservedNames
from ._abstract_space_hook import AbstractSpaceHook
from ._reserved_namespace_hook import ReservedNamespaceHook
from ._name_hook import NamespaceHook
from ._load_space_hook import LoadSpaceHook

__all__ = [
    'SpaceDesc',
    'ReservedNames',
    'AbstractSpaceHook',
    'ReservedNamespaceHook',
    'NamespaceHook',
    'LoadSpaceHook',
]
