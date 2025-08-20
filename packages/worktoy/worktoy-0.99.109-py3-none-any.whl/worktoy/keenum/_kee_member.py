"""
KeeMember encapsulates a member of an enumeration.

Defining properties: (independent properties)
  - name: The name of the member. This is the name by which the member
  appears in the class body of the enumeration. It is the name passed to
  the '__set_name__' method. These must be unique with enumerations and
  must be uppercase. The case requirement is more than convention,
  it is enforced. When an enumeration class body contains key, value pairs
  with the key not in uppercase, it is understood to mean that the value
  does not represent a member of the enumeration.
  - value: The value of the member. Uniquely, this value is not required
  to be unique across members of the same enumeration.
  - index: The index of the member. This index specifies how many members
  are before this member in the enumeration.

KeeMember may be used directly or may be further subclassed. The KeeNum
classes are created by the KeeMeta class which define the class behaviour
post creation, and KeeMember define how members are included in the
enumeration.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.core import Object
from worktoy.desc import Field
from worktoy.utilities import maybe, textFmt
from worktoy.waitaminute import VariableNotNone
from worktoy.waitaminute.keenum import KeeCaseException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Self, Type, TypeAlias

  KEENUM: TypeAlias = Type[object]


class Kee(Object):
  """KeeMember encapsulates a member of an enumeration. """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables

  #  Fallback Variables

  #  Private Variables
  __field_index__ = None
  __field_type__ = None

  #  Public Variables
  name = Field()
  index = Field()

  #  Virtual Variables
  type_ = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def getValue(self) -> Any:
    """Subclasses are free to implement this method to modify how the
    underlying value is retrieved. By default, the first argument passed
    to the constructor is returned as the value of the member or if
    absent, then the name of the member is returned."""
    return maybe(self.__field_value__, self.name)

  @type_.GET
  def _getType(self) -> type:
    """
    This method must return the type of the object that would return
    from the 'getValue' method. The default implementation requires the
    type be defined in the brackets:

    FOO = Kee[int](69)  # The type is 'int'
    """
    return self.__field_type__

  @name.GET
  def _getName(self) -> str:
    """Set by 'Object.__set_name__' when the enumeration is created."""
    return self.__field_name__

  @index.GET
  def _getIndex(self) -> int:
    """Set by 'Object.__set_name__' when the enumeration is created."""
    return self.__field_index__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  The 'KeeSpace' namespace class expects to be able to set 'name' and
  #  'index' after the 'Kee' object is but before the enumeration class is
  #  created. Subclasses that change this behaviour must also implement
  #  these changes  in the 'KeeSpace' class.

  @name.SET
  def _setName(self, name: str) -> None:
    if not name.isupper():
      raise KeeCaseException(name)
    if self.__field_name__ is not None:
      raise VariableNotNone('name', self.__field_name__)
    self.__field_name__ = name

  @index.SET
  def _setIndex(self, index: int) -> None:
    if self.__field_index__ is not None:
      raise VariableNotNone('index', self.__field_index__)
    self.__field_index__ = index

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def __class_getitem__(cls, fieldType: type) -> Self:
    """
    This method is called when the class is used as a type hint.
    It allows the class to be used as a type hint for the value type of
    the enumeration member.
    """
    self = cls.__new__(cls)
    self.__field_type__ = fieldType
    return self

  def __call__(self, *args, **kwargs) -> Self:
    """
    The Kee class uses the special syntax similar to AttriBox from the
    'worktoy.desc' package: NAME = Kee[int](69). This does change the
    '__call__' method to perform the role of the '__init__' method,
    but with the caveat that '__call__' must return 'self'.
    """
    Object.__init__(self, *args, **kwargs)
    if len(args) == 1:
      if isinstance(args[0], self.type_):
        self.__field_value__ = args[0]
        return self
    self.__field_value__ = self.type_(*args, **kwargs)
    return self

  def __str__(self) -> str:
    """Return the string representation of the member."""
    infoSpec = """<%s member: %s>"""
    clsName = type(self).__name__
    info = infoSpec % (clsName, self.name)
    return textFmt(info)

  __repr__ = __str__
