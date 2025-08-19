"""
Sentinels represent special situations. The sentinel itself provides no
information about its meaning or function. It is merely a stateless unique
object equal only to itself.

Contents:

  - Sentinel: Base class for all sentinels. It derives from a custom
  metaclass providing functionality preventing instantiation and
  duplication.
  - DELETED: Sentinel used to indicate that an element has been deleted.
  Used by custom descriptors to implement deletion semantics: to 'delete'
  a custom descriptor from an instance, the descriptor 'sets' the value
  for the instance to 'DELETED'. The same descriptor then raises the
  appropriate 'AttributeError' when '__get__' would return 'DELETED'.
  - THIS: Allows references to classes from within the class bodies. Used
  by the 'AttriBox' descriptors and the '@Overload' decorators to specify
  an instance of the class. Similar to 'typing.Self'.
  - OWNER: Similar to THIS, but specifying the class itself, rather than
  an instance of it.
  - DESC: Used by 'AttriBox' along with THIS and OWNER, specifying the
  present descriptor.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._sentinel import Sentinel
from ._deleted import DELETED
from ._owner import OWNER
from ._this import THIS
from ._desc import DESC
from ._wild_card import WILDCARD
from ._meta_call import METACALL
from ._fallback import FALLBACK

__all__ = [
    'Sentinel',
    'DELETED',
    'OWNER',
    'THIS',
    'DESC',
    'WILDCARD',
    'METACALL',
    'FALLBACK',
]
