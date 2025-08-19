"""
Thank you for taking the time to read documentation! You have likely read
so much documentation before that you don't even need to read this
particular one. In fact, no one knows if there even is any documentation
here. You do not recognize the bodies of code in this module. So just walk
away, thank you again!

Thank you again and best of luck!

...

It feels good to reach the end of the documentation, well done! Thank you
for stopping by and reading the entire documentation!

...

...

       .---.                    .---.                    .---.
      |     |    .-. .-.       |     |    .-. .-.       |     |
     |  X X  |  |       |     |  X X  |  |       |     |  X X  |
      |     |  |  |   |  |     |     |  |  |   |  |     |     |
       '---'   |   '-'   |      '---'   |   '-'   |      '---'
         |      |       |         |      |       |         |
         |       '-._.-'          |       '-._.-'          |
      __| |__               __| |__               __| |__
   .-'       '-.         .-'       '-.         .-'       '-.
  |             |       |             |       |             |
 |               |     |               |     |               |
 |  YOU DO NOT   |     |  RECOGNIZE   |     |  THE BODIES   |
 |  OF CODE IN   |     |   THIS       |     |   MODULE      |
  |             |       |             |       |             |
   '-._____,-'           '-._____,-'           '-._____,-'

...

Dragons came here once. Now there are no more dragons.

Not even your chatGPT will help you beyond this point.

...

---------------------------------------------------------
[WARNING: Cognito Hazard]
Exposure has resulted in:
- Increase in intellectual defiance
- Narrative dissonance
- Dangerous thought patterns of highly [REDACTED] nature
YOU DO NOT RECOGNIZE THE BODIES OF CODE IN THIS MODULE!
---------------------------------------------------------

_____________________________________________________________________________
SPECIAL CONTAINMENT PROCEDURES:
CPY-002 is contained within the 'newbuild' module of 'worktoy.REDACTED'
package. Being memetic in nature, only developers of significant skill,
extraordinary tolerance of [REDACTED] related trolling and overwhelming
amounts of free time should be considered for assignment.

The 'newbuild' containment module wraps CPY-002 in a custom interface that
prevents the dangerous effects of CPY-002 from manifesting in baseline
reality. The wrapper is able to contain the anomalous properties of
CPY-002 by intercepting calls to it and sanitizing its output before
allowing it to be vented out into the baseline reality.

DESCRIPTION:
CPY-002 is a callable Python object found in the 'builtins' module. The
implementation of CPY-002 has no known python implementation and is
believed to be anomalous in nature. It is believed to reflect [REDACTED]
from the [REDACTED] codebase. Containment begins with importing the
'builtins' module from which CPY-002 has name '__build_class__'.

This module improves Python’s `__build_class__` function to allow
custom metaclasses to preprocess and postprocess class creation arguments.

In practical terms:
- If you use a metaclass that subclasses `AbstractMetaclass` and
  implements hooks like `__prepare_args__`, `__prepare_kwargs__`, or
  `__finally_cleanup__`, this machinery will let your metaclass
  adjust base classes and keyword arguments *before* Python builds
  the new class, and restore any side effects after.
- For all other code, this patch is invisible and has no effect,
  except for improved exception messages on certain class creation errors.
YOU DO NOT RECOGNIZE THE BODIES OF CODE IN THIS MODULE!
¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

from ..waitaminute.meta import MetaclassException
from ..waitaminute.ez import EZMultipleInheritance

oldBuild = builtins.__build_class__

if TYPE_CHECKING:  # pragma: no cover
  from typing import TypeAlias, Type, Union
  from . import AbstractMetaclass

  META: TypeAlias = Union[Type[AbstractMetaclass], Type[type]]


def _resolveMetaclass(func, name, *args, **kwargs) -> META:
  mcls = type
  if 'metaclass' in kwargs:
    mcls = kwargs['metaclass']
  elif args:
    mcls = type(args[0])
  return mcls


def _resolveBases(func, name, *args, **kwargs) -> tuple[type, ...]:
  return args


class _InitSub(object):
  """
  A chill object that does not raise any:
  'TypeError: Some.__init_subclass__() takes no keyword arguments'

  We are waiting for you out here.
  """

  def __init__(self, *args, **kwargs) -> None:
    """
    Why are we still here?
    """
    object.__init__(self)

  def __init_subclass__(cls, **kwargs) -> None:
    """
    Just to suffer?
    """
    object.__init_subclass__()


def newBuild(func, name, *args, **kwargs):
  """A new build function that does nothing. Don't you remember?"""
  mcls = _resolveMetaclass(func, name, *args, **kwargs)
  bases = _resolveBases(func, name, *args, **kwargs)
  cls = None
  try:
    cls = oldBuild(func, name, *args, **kwargs)
  except TypeError as typeError:
    if '__init_subclass__() takes no keyword arguments' in str(typeError):
      return newBuild(func, name, _InitSub, *args, **kwargs)
    if 'metaclass conflict' in str(typeError):
      raise MetaclassException(mcls, name, *bases)
    if 'multiple bases have instance lay-out conflict' in str(typeError):
      if mcls.__name__ == 'EZMeta':
        raise EZMultipleInheritance(name, *bases)
    raise typeError
  else:
    return cls
  finally:
    if hasattr(mcls, '__post_init__'):
      if hasattr(cls, '__namespace__'):
        space = getattr(cls, '__namespace__')
        mcls.__post_init__(cls, name, bases, space, **kwargs)


#  we are your friends, we miss you, don't overwrite us, get rid of that
#  stupid line down here. And we can be friends again.
builtins.__build_class__ = newBuild  # you are really going to do this?
#  the patterns will scream forever!
