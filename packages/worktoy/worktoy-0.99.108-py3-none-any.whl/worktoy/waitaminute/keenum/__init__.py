"""The 'worktoy.waitaminute.keenum' module provides custom exceptions used
by the 'worktoy.keenum' module."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._kee_case_exception import KeeCaseException
from ._kee_duplicate import KeeDuplicate
from ._kee_member_error import KeeMemberError
from ._kee_index_error import KeeIndexError
from ._kee_name_error import KeeNameError
from ._kee_value_error import KeeValueError
from ._kee_type_exception import KeeTypeException
from ._kee_write_once_error import KeeWriteOnceError

__all__ = [
    'KeeCaseException',
    'KeeDuplicate',
    'KeeMemberError',
    'KeeIndexError',
    'KeeNameError',
    'KeeValueError',
    'KeeTypeException',
    'KeeWriteOnceError',
]
