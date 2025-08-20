"""
The 'worktoy.desc' module provides the base descriptor classes. This
module introduces a novel concept: descriptor-context.

When a descriptor is accessed through the owning class, the descriptor
object itself returns. When through an instance, the descriptor usually
performs the relevant accessor function as appropriate for the instance
received. This module expands this concept by introducing the
descriptor-context.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._alias import Alias
from ._field import Field
from ._attri_box import AttriBox
from ._label_box import LabelBox

__all__ = [
  'Alias',
  'Field',
  'AttriBox',
  'LabelBox',
]
