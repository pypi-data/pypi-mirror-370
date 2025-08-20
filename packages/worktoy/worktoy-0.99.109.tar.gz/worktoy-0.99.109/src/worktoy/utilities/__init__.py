"""
The 'worktoy.utilities' module provides small, standalone utilities used
across the 'worktoy' library.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._perm import perm
from ._slice_len import sliceLen
from ._type_cast import typeCast
from ._class_body_template import ClassBodyTemplate
from ._bipartite_matching import bipartiteMatching
from ._unpack import unpack
from ._maybe import maybe
from ._replace_flex import replaceFlex
from ._text_fmt import textFmt
from ._string_list import stringList
from ._directory import Directory
from ._join_words import joinWords
from ._resolve_mro import resolveMRO
from ._word_wrap import wordWrap

__all__ = [
    'perm',
    'sliceLen',
    'typeCast',
    'ClassBodyTemplate',
    'bipartiteMatching',
    'unpack',
    'maybe',
    'replaceFlex',
    'textFmt',
    'stringList',
    'Directory',
    'joinWords',
    'resolveMRO',
    'wordWrap',
]
