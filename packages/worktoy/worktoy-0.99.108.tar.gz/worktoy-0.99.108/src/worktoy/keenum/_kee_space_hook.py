"""
KeeSpaceHook collects the KeeMember objects encountered in the class
bodies of KeeNum classes. This happens during the 'setItemPhase'. To avoid
context leakage, the members are collected in the owning namespace object.
The namespace object is expected to implement a method called
'addEnumeration' which 'KeeHook' calls to register the members. The
'KeeHook' provides no further functionality than deciding what key,
value pairs to collect as future members of the enumeration.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls.space_hooks import AbstractSpaceHook
from . import Kee

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Type, TypeAlias, Callable
  from . import KeeMeta

  __INIT__: TypeAlias = Callable[[KeeMeta, Kee], None]
  __GET__: TypeAlias = Callable[[KeeMeta, KeeMeta, Type[KeeMeta]], Any]


class KeeSpaceHook(AbstractSpaceHook):
  """
  KeeSpaceHook collects the KeeMember objects encountered in the class
  bodies of KeeNum classes. This happens during the 'setItemPhase'. To avoid
  context leakage, the members are collected in the owning namespace object.
  The namespace object is expected to implement a method called
  'addEnumeration' which 'KeeHook' calls to register the members. The
  'KeeSpaceHook' provides no further functionality than deciding what key,
  value pairs to collect as future members of the enumeration.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def setItemPhase(self, key: str, val: Any, old: Any = None, ) -> bool:
    """Hook for setItem. This is called before the __setitem__ method of
    the namespace object is called. The default implementation does nothing
    and returns False. """

    if isinstance(val, Kee):
      self.space.addNum(key, val)
      return True
    return False
