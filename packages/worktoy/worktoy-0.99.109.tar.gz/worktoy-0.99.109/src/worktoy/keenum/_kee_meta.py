"""
KeeMeta provides the metaclass for the 'worktoy.keenum' module.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ._kee_desc import Base, MRO, Members, IsRoot
from ..mcls import BaseMeta
from . import KeeSpace as KSpace, Kee
from ..waitaminute import TypeException, attributeErrorFactory
from ..waitaminute.keenum import KeeNameError, KeeIndexError
from ..waitaminute.keenum import KeeMemberError, KeeValueError

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, TypeAlias, Self, Iterator

  from . import KeeNum

  Bases: TypeAlias = tuple[type, ...]


class KeeMeta(BaseMeta):
  """
  KeeMeta provides the metaclass for the 'worktoy.keenum' module.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __allow_instantiation__ = False
  __num_members__ = None
  __is_root__ = None

  #  Public Variables
  isRoot = IsRoot()
  base = Base()
  mroNum = MRO()
  members = Members()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def __prepare__(mcls, name: str, bases: Bases, **kw: Any) -> KSpace:
    """Prepares the namespace for the class."""
    bases = (*[b for b in bases if b.__name__ != '_InitSub'],)
    return KSpace(mcls, name, bases, **kw)

  def __new__(mcls, name: str, bases: Bases, space: KSpace, **kw) -> Self:
    """
    Creates a new instance of the class.
    This method is called when the class is created.
    """
    cls = super().__new__(mcls, name, bases, space, **kw)
    cls.__num_members__ = []
    if name == 'KeeNum':
      return cls
    base = (bases or [None])[0]
    # if not hasattr(base, '__enumeration_members__'):
    #   raise TypeException('base', base, Kee, )
    cls.__allow_instantiation__ = True

    for i, (key, kee) in enumerate(space.__enumeration_members__.items()):
      self = getattr(base, key, None)
      if self is None:
        self = cls(kee, )
      setattr(cls, key, self)
      cls.__num_members__.append(self)
    cls.__allow_instantiation__ = False
    return cls

  def __call__(cls, *args, **kwargs) -> Any:
    """
    Prevents instantiation of the class.
    This method is called when the class is instantiated.
    """
    if cls.__allow_instantiation__:
      return super().__call__(*args, **kwargs)
    return cls._resolveMember(args[0])

  def __getitem__(cls, identifier: Any) -> Kee:
    """
    Gets a member of the enumeration by index or key.
    This method is used to get a member of the enumeration by index or key.
    """
    return cls._resolveMember(identifier)

  def __getattr__(cls, name: str) -> Kee:
    """
    Gets a member of the enumeration by name.
    This method is used to get a member of the enumeration by name.
    """
    try:
      self = cls._resolveKey(name)
    except KeeNameError as keeNameError:
      error = attributeErrorFactory(cls, name)
      raise error from keeNameError
    else:
      return self

  def __iter__(cls, ) -> Iterator[Self]:
    """
    Iterates over the members of the enumeration.
    This method is used to iterate over the members of the enumeration.
    """
    yield from cls.members

  def __len__(cls, ) -> int:
    """
    Returns the number of members in the enumeration.
    This method is used to get the number of members in the enumeration.
    """
    return sum(1 for _ in cls)

  def __contains__(cls, identifier: Any) -> bool:
    """
    Checks if the enumeration contains a member by index or key.
    This method is used to check if the enumeration contains a member.
    """
    try:
      _ = cls._resolveMember(identifier)
    except (IndexError, KeyError):
      return False
    else:
      return True

  def __instancecheck__(cls, instance: Any) -> bool:
    """
    Checks if the instance is a member of the enumeration.
    This method is used to check if the instance is a member of the
    enumeration.
    """
    return True if issubclass(type(instance), cls) else False

  def __subclasscheck__(cls, subclass: type) -> bool:
    """
    Checks if the subclass is a subclass of the enumeration.
    This method is used to check if the subclass is a subclass of the
    enumeration.
    """
    if not hasattr(subclass, '__mro__'):
      return False
    for item in subclass.__mro__:
      if item is cls:
        return True
    return False

  def __str__(cls) -> str:
    """
    Returns a string representation of the enumeration.
    This method is used to get a string representation of the enumeration.
    """
    infoSpec = """<KeeNum '%s': %d members>"""
    clsName = cls.__name__
    n = len(cls.__num_members__)
    info = infoSpec % (clsName, n)
    return info

  __repr__ = __str__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _resolveMember(cls, identifier: Any) -> Any:
    """
    Resolves a member of the enumeration.
    This method is used to resolve a member of the enumeration.
    """
    if isinstance(identifier, int):
      return cls._resolveIndex(identifier)
    if isinstance(identifier, str):
      return cls._resolveKey(identifier)
    if type(type(identifier)) is type(cls):
      for member in cls:
        if member is identifier:
          return member
      raise KeeMemberError(cls, identifier)
    try:
      member = cls.fromValue(identifier)
    except KeeValueError:
      from . import KeeNum
      raise TypeException('identifier', identifier, int, str, KeeNum)
    else:
      return member

  def _resolveIndex(cls, index: int) -> Kee:
    """
    Resolves a member of the enumeration by index.
    This method is used to resolve a member of the enumeration by index.
    """
    if index < 0:
      return cls[len(cls) + index]
    if index < len(cls):
      return cls.__num_members__[index]
    raise KeeIndexError(cls, index)

  def _resolveKey(cls, key: str) -> Kee:
    """
    Resolves a member of the enumeration by key.
    This method is used to resolve a member of the enumeration by key.
    """
    for member in cls.__num_members__:
      if member.name.lower() == key.lower():
        return member
    raise KeeNameError(cls, key)

  def fromValue(cls, value: Any) -> KeeNum:
    """
    Resolves a member of the enumeration by value.
    This method is used to resolve a member of the enumeration by value.
    """
    for member in cls.__num_members__:
      if member.value == value:
        return member
    raise KeeValueError(cls, value)
