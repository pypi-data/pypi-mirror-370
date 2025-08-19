"""
The 'worktoy.waitaminute.desc' package provides the custom exceptions
specific to the implementation of the descriptor protocol in the 'worktoy'
library.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._descriptor_exception import DescriptorException
from ._access_error import AccessError
from ._protected_error import ProtectedError
from ._read_only_error import ReadOnlyError
from ._without_exception import WithoutException

__all__ = [
    'DescriptorException',
    'AccessError',
    'ReadOnlyError',
    'ProtectedError',
    'WithoutException',
]
