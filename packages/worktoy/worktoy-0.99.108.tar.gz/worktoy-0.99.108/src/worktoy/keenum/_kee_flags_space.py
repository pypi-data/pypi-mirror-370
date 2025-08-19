"""
KeeFlagsSpace subclasses KeeSpace from the worktoy.keenum package
providing the namespace object required for KeeFlags.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.keenum import KeeSpace, Kee
from worktoy.mcls import BaseSpace
from worktoy.utilities import maybe
from worktoy.waitaminute import TypeException
from worktoy.waitaminute.keenum import KeeDuplicate

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Self, Type, TypeAlias

  Bases: TypeAlias = tuple[Type, ...]


class KeeFlagsSpace(KeeSpace):
  """
  KeeFlagsSpace subclasses KeeSpace from the worktoy.keenum package
  providing the namespace object required for KeeFlags.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __kee_flags__ = None
  __flag_type__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def addNum(self, name: str, member: Kee, ) -> Any:
    """
    Returns the KeeFlags instance associated with this space.
    """
    member.name = name
    member.index = len(self.__kee_flags__)
    if self.__flag_type__ is None:
      self.__flag_type__ = member.type_
    elif self.__flag_type__ is not member.type_:
      raise TypeException('member', member, self.__flag_type__, )
    if name in self.__kee_flags__:
      raise KeeDuplicate(name, member)
    self.__kee_flags__[name] = member

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, mcls: type, name: str, bases: Bases, **kwargs) -> None:
    BaseSpace.__init__(self, mcls, name, bases, **kwargs)
    self.__enumeration_members__ = None
    base = (bases or [None])[0]
    if base.__name__ == 'KeeFlags':
      self.__kee_flags__ = dict()
      self.__flag_type__ = None
    else:
      space = getattr(base, '__namespace__', dict())
      self.__kee_flags__ = getattr(space, '__kee_flags__', dict())
      self.__flag_type__ = getattr(space, '__flag_type__', None)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def expandNum(self, ) -> Self:
    """Creates a num instance for each combination of flags. """
    N = 2 ** len(self.__kee_flags__)  # Number of combinations
    for i in range(N):
      included = []
      for j, (name, member) in enumerate(self.__kee_flags__.items()):
        if i & (1 << j):
          included.append(member)
      included.sort(key=lambda m: m.index)
      items = [m.name for m in included]
      name = '_'.join(items) or 'NULL'
      kee = Kee[set](set(included))
      KeeSpace.addNum(self, name, kee)
    return self

  def postCompile(self, namespace: dict) -> dict:
    """
    Post-compiles the namespace by expanding the flags.
    This method is called after the namespace has been compiled.
    """
    namespace = KeeSpace.postCompile(self, namespace)
    namespace['__kee_flags__'] = maybe(self.__kee_flags__, dict())
    namespace['__flag_type__'] = maybe(self.__flag_type__, object)
    return namespace
