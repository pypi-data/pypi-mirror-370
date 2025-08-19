"""
The 'worktoy.utilities.mathematics' module provides mathematical utilities
used across the 'worktoy' library.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._constants import pi, arcTan, atan2
from ._trig import sin, cos, tan, cosh, sinh, tanh
from ._exp_log import e, log, exp
from ._factorial import factorial

__all__ = [
    'e',
    'pi',
    'arcTan',
    'atan2',
    'log',
    'exp',
    'sin',
    'cos',
    'tan',
    'cosh',
    'sinh',
    'tanh',
    'factorial',
]
