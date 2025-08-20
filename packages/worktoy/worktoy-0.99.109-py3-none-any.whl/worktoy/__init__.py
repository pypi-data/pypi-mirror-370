"""The 'worktoy' package provides a collection of utilities leveraging
advanced python features including custom metaclasses and the descriptor
protocol. The readme file included provides detailed documentation on the
included features. The modules provided depend on each other in
implementation, but can be used independently.

The package consists of thr following modules:
- 'parse': For low-level parsing.
- 'text': For working with text.
- 'waitaminute': Provides custom exception classes.
- 'static': For parsing of objects.
- 'mcls': Provides custom metaclasses.
- 'attr': Provides custom descriptors.
- 'ezdata': Provides the 'EZData' class for creating data classes.
- 'keenum': Provides the 'KeeNum' class for creating enums.
"""
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from . import utilities
from . import core
from . import waitaminute
from . import desc
from . import mcls
from . import keenum
from . import ezdata
