"""
KeeSpace provides the namespace class used by the 'worktoy.keenum' module.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls import BaseSpace
from . import KeeSpaceHook, Kee
from ..waitaminute.keenum import KeeDuplicate, KeeTypeException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Dict, TypeAlias

  Members: TypeAlias = Dict[str, Kee]
  Bases: TypeAlias = tuple[type, ...]


class KeeSpace(BaseSpace):
  """KeeSpace provides the namespace class used by the 'worktoy.keenum'
  module. """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  keeSpaceHook = KeeSpaceHook()

  #  Private Variables
  __enumeration_members__ = None
  __member_type__ = None
  __num_list__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def addNum(self, name: str, member: Kee) -> None:
    """Adds the member to the enumeration dict. """
    if self.__enumeration_members__ is None:
      self.__enumeration_members__ = dict()
    member.name = name
    member.index = len(self.__enumeration_members__)
    member = self.typeGuard(member)
    if name in self.__enumeration_members__:
      raise KeeDuplicate(name, member)
    self.__enumeration_members__[name] = member

  def typeGuard(self, member: Kee) -> Kee:
    """Ensures that the member is an instance of KeeNum. """
    if self.__member_type__ is None:
      self.__member_type__ = member.type_
      return member
    if self.__member_type__ is member.type_:
      return member
    name, val, type_ = member.name, member.getValue(), self.__member_type__
    raise KeeTypeException(name, val, type_, )

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, mcls: type, name: str, bases: Bases, **kwargs) -> None:
    """Initializes the KeeSpace. """
    super().__init__(mcls, name, bases, **kwargs)
    base = (bases or [None])[0]
    if hasattr(base, '__namespace__'):
      baseSpace = base.__namespace__
      if getattr(baseSpace, '__enumeration_members__', None) is not None:
        self.__enumeration_members__ = dict()
        baseMembers = baseSpace.__enumeration_members__
        for key in baseMembers:
          self.__enumeration_members__[key] = baseMembers[key]
