"""
The 'worktoy.ezdata' package provides the EZData dataclass.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen

from ._trust import trust
from ._ez_slot import EZSlot
from ._ez_desc import EZDesc
from ._ez_space_hook import EZSpaceHook
from ._ez_space import EZSpace
from ._ez_meta import EZMeta
from ._ez_data import EZData

__all__ = [
    'trust',
    'EZSlot',
    'EZDesc',
    'EZSpaceHook',
    'EZSpace',
    'EZMeta',
    'EZData',
]
