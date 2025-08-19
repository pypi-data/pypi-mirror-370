"""EZHook collects the field entries in EZData class bodies. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls import AbstractNamespace as ASpace
from ..mcls.space_hooks import AbstractSpaceHook, ReservedNames
from ..utilities import textFmt, maybe, stringList
from ..waitaminute import TypeException, attributeErrorFactory
from ..waitaminute.ez import UnorderedEZException, EZDeleteException
from ..waitaminute.ez import UnfrozenHashException, FrozenEZException
from ..waitaminute.meta import ReservedName
from . import EZSlot

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Iterator, Callable, TypeAlias, Any, Never, Self

  from worktoy.ezdata import EZData

  Slots: TypeAlias = tuple[str, ...]
  SlotTypes: TypeAlias = Callable[[EZData, str], type]
  SlotDefaults: TypeAlias = Callable[[EZData, str], Any]

  Dunder: TypeAlias = Callable[[Any], Any]
  Factory: TypeAlias = Callable[[], Dunder]
  Factories: TypeAlias = dict[str, Factory]
  __INIT__: TypeAlias = Callable[[EZData], None]
  __LT__: TypeAlias = Callable[[EZData, EZData], bool]
  __LE__: TypeAlias = Callable[[EZData, EZData], bool]
  __GT__: TypeAlias = Callable[[EZData, EZData], bool]
  __GE__: TypeAlias = Callable[[EZData, EZData], bool]
  __EQ__: TypeAlias = Callable[[EZData, EZData], bool]
  __HASH__: TypeAlias = Callable[[EZData], int]
  __STR__: TypeAlias = Callable[[EZData], str]
  __REPR__: TypeAlias = Callable[[EZData], str]
  __ITER__: TypeAlias = Callable[[EZData], Iterator]
  __LEN__: TypeAlias = Callable[[EZData], int]
  __GETITEM__: TypeAlias = Callable[[EZData, str], Any]
  __SETITEM__: TypeAlias = Callable[[EZData, str, Any], None]
  __DELITEM__: TypeAlias = Callable[[EZData, str], Never]
  __GETATTR__: TypeAlias = Callable[[EZData, str], Any]
  __SETATTR__: TypeAlias = Callable[[EZData, str, Any], None]
  __DELATTR__: TypeAlias = Callable[[EZData, str], Never]
  AS_TUPLE: TypeAlias = Callable[[EZData], tuple[Any, ...]]
  AS_DICT: TypeAlias = Callable[[EZData], dict[str, Any]]


class EZSpaceHook(AbstractSpaceHook):
  """EZHook collects the field entries in EZData class bodies. """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  __bad_names__ = """__slots__, __init__, __eq__, 
    __iter__, __getitem__, __setitem__, __getattr__, __len__, __hash__"""
  __auto_names__ = """__slots__, __init__, __eq__, __str__, __repr__,
    __iter__, __getitem__, __setitem__, __getattr__, __len__, __hash__"""

  #  Private Variables
  __new_callables__ = None
  __added_slots__ = None
  __typehint_mode__ = None
  __normal_mode__ = None

  #  Public Variables
  reservedNames = ReservedNames()
  if TYPE_CHECKING:  # pragma: no cover
    from . import EZSpace
    space: EZSpace

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getAutoNameFactoryDict(self, ) -> Factories:
    """Returns a dictionary of auto-named methods."""
    return {
        '__init__'   : self.initFactory,
        '__eq__'     : self.eqFactory,
        '__hash__'   : self.hashFactory,
        '__str__'    : self.strFactory,
        '__repr__'   : self.reprFactory,
        '__iter__'   : self.iterFactory,
        '__len__'    : self.lenFactory,
        '__getitem__': self.getItemFactory,
        '__setitem__': self.setItemFactory,
        '__delitem__': self.delItemFactory,
        '__getattr__': self.getAttrFactory,
        '__setattr__': self.setAttrFactory,
        '__delattr__': self.delAttrFactory,
        '__lt__'     : self.ltFactory,
        '__le__'     : self.leFactory,
        '__gt__'     : self.gtFactory,
        '__ge__'     : self.geFactory,
        'asTuple'    : self.asTupleFactory,
        'asDict'     : self.asDictFactory,
    }

  def _getBadNames(self) -> list[str]:
    """Returns a tuple of names that are reserved and should not be used."""
    return stringList(self.__bad_names__, )

  def _getAddedSlots(self) -> list[EZSlot]:
    """Returns a list of slots added by the current class body."""
    addedSlots = maybe(self.__added_slots__, [])
    ownerName = self.space.getClassName()
    out = []
    for ezSlot in addedSlots:
      if ezSlot.__owner_name__ == ownerName:
        out.append(ezSlot)
    return out

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def addSlot(self, ezSlot: EZSlot, **kwargs) -> None:
    """Adds a slot entry"""
    existing = self._getAddedSlots()
    if ezSlot in existing:
      return
    ezSlot.__owner_name__ = self.space.getClassName()
    self.__added_slots__ = [*existing, ezSlot]

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def preCompilePhase(self, compiledSpace: dict) -> dict:
    """Sets the factory created functions"""
    for name, factory in self._getAutoNameFactoryDict().items():
      compiledSpace[name] = factory()
    return compiledSpace

  def postCompilePhase(self, compiledSpace: dict) -> dict:
    """The postCompileHook method is called after the class is compiled."""
    ezSlots = self._getAddedSlots()
    if self.space.getKwargs().get('order', False) and ezSlots:
      for ezSlot in ezSlots:
        val = ezSlot.__default_value__
        try:
          _ = val < val or val > val
        except Exception as exception:
          if 'not supported between instances of ' in str(exception):
            clsName = self.space.getClassName()
            fName = ezSlot.name
            fType = ezSlot.typeValue
            raise UnorderedEZException(clsName, fName, fType)
          raise exception
    compiledSpace['__slot_objects__'] = ezSlots
    compiledSpace['__slots__'] = [ez.name for ez in ezSlots]
    return compiledSpace

  def setItemPhase(self, key: str, value: Any, oldValue: Any, ) -> bool:
    """
    Creates a slot entry for the given key and value, when value is not a
    callable, a descriptor or a special reserved name.
    """
    if key in self._getBadNames():
      if not hasattr(value, '__is_root__'):
        raise ReservedName(key)
      return True  # Ignores @_root decorated methods
    if key in self.reservedNames:
      return False  # Already handled by ReservedNameHook
    if callable(value):
      return False
    if hasattr(value, '__get__'):
      return False
    ezSlot = EZSlot(key)
    ezSlot.__type_value__ = type(value)
    ezSlot.__default_value__ = value
    self.addSlot(ezSlot)
    return True

  def preparePhase(self, space: ASpace, ) -> None:
    for base in self.space.getBases():
      for ezSlot in getattr(base, '__slot_objects__', []):
        self.addSlot(ezSlot)

  # \_____________________________________________________________________/ #
  #  Method factories
  # /¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨\ #
  @staticmethod
  def initFactory() -> __INIT__:
    """
    Creates the '__init__' method for the EZData class.
    """

    def __init__(self, *args, **kwargs) -> None:
      """
      The generated '__init__' method sets attributes on the instance
      based on given arguments. Keyword arguments take precedence.
      Positional arguments are applied in order.
      """
      posArgs = [*args, ]
      while len(posArgs) < len(self.__slot_objects__):
        posArgs.append(None)
      for (arg, slot) in zip(args, self.__slot_objects__):
        if arg is None:
          continue
        if not isinstance(arg, slot.typeValue):
          if slot.typeValue is not str:
            try:
              setattr(self, slot.name, slot.typeValue(arg))
            except Exception as e:
              raise TypeException('arg', arg, slot.typeValue, ) from e
            else:
              continue
          raise TypeException('arg', arg, slot.typeValue, )
        setattr(self, slot.name, arg)
      for key, val in kwargs.items():
        if key in self.__slots__:
          slot = self.__slot_objects__[self.__slots__.index(key)]
          if not isinstance(val, slot.typeValue):
            if slot.typeValue is not str:
              setattr(self, key, slot.typeValue(val))
              continue
            raise TypeException('val', val, slot.typeValue, )
          setattr(self, key, val)

    setattr(__init__, '__auto_generated__', True)
    return __init__

  @classmethod
  def ltFactory(cls, ) -> __LT__:
    """Creates the '__lt__' method for the EZData class. """

    def __lt__(self, other: Self) -> bool:
      if not type(self).isOrdered:
        raise UnorderedEZException(type(self).__name__)
      if type(self) is not type(other):
        return NotImplemented
      for slot in getattr(self, '__slots__'):
        selfVal, otherVal = getattr(self, slot), getattr(other, slot)
        if selfVal < otherVal:
          return True
        elif selfVal > otherVal:
          return False
        continue
      return False

    return __lt__

  @classmethod
  def leFactory(cls, ) -> __LE__:
    """Creates the '__le__' method for the EZData class. """

    def __le__(self, other: Self) -> bool:  # NOQA
      if not type(self).isOrdered:
        raise UnorderedEZException(type(self).__name__)
      if type(self) is not type(other):
        return NotImplemented
      for slot in getattr(self, '__slots__'):
        selfVal, otherVal = getattr(self, slot), getattr(other, slot)
        if selfVal < otherVal:
          return True
        elif selfVal > otherVal:
          return False
        continue
      return True

    return __le__

  @classmethod
  def gtFactory(cls, ) -> __GT__:
    """Creates the '__gt__' method for the EZData class."""

    def __gt__(self, other: Self) -> bool:
      if not type(self).isOrdered:
        raise UnorderedEZException(type(self).__name__)
      if type(self) is not type(other):
        return NotImplemented
      for slot in getattr(self, '__slots__'):
        selfVal, otherVal = getattr(self, slot), getattr(other, slot)
        if selfVal > otherVal:
          return True
        elif selfVal < otherVal:
          return False
        continue
      return False

    return __gt__

  @classmethod
  def geFactory(cls, ) -> __GE__:
    """Creates the '__ge__' method for the EZData class. """

    def __ge__(self, other: Self) -> bool:
      if not type(self).isOrdered:
        raise UnorderedEZException(type(self).__name__)
      if type(self) is not type(other):
        return NotImplemented
      for slot in getattr(self, '__slots__'):
        selfVal, otherVal = getattr(self, slot), getattr(other, slot)
        if selfVal > otherVal:
          return True
        elif selfVal < otherVal:
          return False
        continue
      return True

    return __ge__

  @staticmethod
  def eqFactory() -> __EQ__:
    """
    Creates the '__eq__' method for the EZData class.
    """

    def __eq__(self, other: EZData) -> bool:
      """
      Instances of EZData are equal if each of their data fields are equal.
      """
      if type(self) is not type(other):
        return NotImplemented
      for slot in self.__slot_objects__:
        if getattr(self, slot.name) != getattr(other, slot.name):
          return False
      return True

    setattr(__eq__, '__auto_generated__', True)
    return __eq__

  @staticmethod
  def hashFactory() -> __HASH__:
    """Creates the '__hash__' method for the EZData class."""

    def __hash__(self) -> int:
      """The hash of an EZData instance is the hash of its data fields."""
      if type(self).isFrozen:
        values = []
        for slot in self.__slots__:
          values.append(getattr(self, slot))
        return hash((*values,))
      clsName = self.__slot_objects__[0].ownerName
      raise UnfrozenHashException(clsName)

    setattr(__hash__, '__auto_generated__', True)
    return __hash__

  @staticmethod
  def strFactory() -> __STR__:
    """The strFactory method is called when the class is created."""

    def __str__(self) -> str:
      """The __str__ method is called when the class is created."""
      clsName = type(self).__name__
      names = [ezSlot.name for ezSlot in self.__slot_objects__]
      vals = [str(getattr(self, name)) for name in names]
      keyVals = ['%s=%s' % (name, val) for name, val in zip(names, vals)]
      return """%s(%s)""" % (clsName, ', '.join(keyVals))

    setattr(__str__, '__auto_generated__', True)
    return __str__

  @staticmethod
  def reprFactory(*ezSlots) -> __REPR__:
    """The reprFactory method is called when the class is created."""

    def __repr__(self) -> str:
      """The __repr__ method is called when the class is created."""
      infoSpec = """%s(%s)"""
      clsName = type(self).__name__
      fieldNames = [ezSlot.name for ezSlot in self.__slot_objects__]
      fieldValues = [getattr(self, name) for name in fieldNames]
      fieldRepr = []
      for field in fieldValues:
        if isinstance(field, str):
          fieldRepr.append("""'%s'""" % field)
          continue
        fieldRepr.append(str(field))
      if fieldRepr:
        info = infoSpec % (clsName, ', '.join(fieldRepr))
      else:
        info = infoSpec % (clsName, '')
      return textFmt(info)

    setattr(__repr__, '__auto_generated__', True)
    return __repr__

  @staticmethod
  def iterFactory() -> __ITER__:
    """The iterFactory method is called when the class is created."""

    def __iter__(self, ) -> Iterator:
      """Implementation of the iteration protocol"""
      for key in self.__slots__:
        yield getattr(self, key)

    setattr(__iter__, '__auto_generated__', True)
    return __iter__

  @staticmethod
  def lenFactory() -> __LEN__:
    """The lenFactory method is called when the class is created."""

    def __len__(self) -> int:
      """The __len__ method is called when the class is created."""
      return len(self.__slots__)

    setattr(__len__, '__auto_generated__', True)
    return __len__

  @staticmethod
  def getItemFactory() -> __GETITEM__:
    """The getItemFactory method is called when the class is created."""

    def __getitem__(self, identifier: str) -> Any:
      """The __getitem__ method is called when the class is created."""
      if isinstance(identifier, int):
        if identifier < 0:
          return self[identifier + len(self)]
        if identifier < len(self):
          #  Uses the 'int' valued identifier to retrieve the name from
          #  the '__slots__' tuple. Then this name is passed recursively
          #  back to '__getitem__' retrieving the value from 'str'.
          return self[self.__slots__[identifier]]
        infoSpec = """Index %d out of range for '%s' with %d slots."""
        clsName = type(self).__name__
        info = infoSpec % (identifier, clsName, len(self.__slots__))
        raise IndexError(textFmt(info))
      if isinstance(identifier, str):
        #  Uses the 'str' valued identifier to retrieve the value. The
        #  identifier may initially have been an 'int' value, resolved to
        #  a 'str' value as described above.
        if identifier in self.__slots__:
          return getattr(self, identifier)
        e = attributeErrorFactory(type(self), identifier)
        raise KeyError(identifier) from e
      if isinstance(identifier, slice):
        sliceKeys = self.__slots__[identifier]
        out = []
        for sliceKey in sliceKeys:
          out.append(self[sliceKey])
        return (*out,)
      raise TypeException('key', identifier, str, int, slice)

    setattr(__getitem__, '__auto_generated__', True)
    return __getitem__

  @staticmethod
  def setItemFactory() -> __SETITEM__:

    def __setitem__(self, identifier: Any, value: Any) -> None:
      """
      Assigns value(s) to this object’s slots via integer index, slot name,
      or slice.

      - If 'identifier' is an int, it is interpreted as a positional index
        into the slot sequence. Negative indices are supported. Raises
        IndexError if out of range.

      - If 'identifier' is a str, it must match one of the defined slot
        names, otherwise KeyError is raised.

      - If 'identifier' is a slice, it refers to a contiguous subset of slot
        names. The 'value' assigned must be an iterable of equal length. If
        lengths differ, raises IndexError. If a string is provided as the
        'value', raises TypeError with an explanatory message—this
        prevents the common error of assigning an iterable of characters,
        but bytes and bytearray are allowed.

      Raises TypeException if 'identifier' is not an int, str, or slice.
      """

      if isinstance(identifier, int):
        if identifier < 0:
          return self.__setitem__(identifier + len(self), value)
        if identifier < len(self):
          return self.__setitem__(self.__slots__[identifier], value)
        infoSpec = """Index %d out of range for '%s' with %d slots."""
        clsName = type(self).__name__
        info = infoSpec % (identifier, clsName, len(self))
        raise IndexError(textFmt(info))
      if isinstance(identifier, str):
        if identifier in self.__slots__:
          return setattr(self, identifier, value)
        raise KeyError(identifier)
      if isinstance(identifier, slice):
        if isinstance(value, str):
          infoSpec = """Tried setting slice: 'self[%s]' to a 'str' object: 
          '%s'. Because this is nearly always not meant to be taken as an 
          iterable of characters, 'EZData' does not allow this despite the 
          fact that Python technically does. Please note that this 
          prohibition applies only to 'str' not to 'bytes' or 'bytearray'."""
          info = textFmt(infoSpec % (identifier, value))
          raise TypeError(info)
        sliceSlots = self.__slots__[identifier]
        if len(sliceSlots) != len(value):
          infoSpec = """Slice '%s' of '%s' with %d slots cannot be set to 
          value of length %d!"""
          clsName = type(self).__name__
          lenSlots = len(self)
          lenValue = len(value)
          info = infoSpec % (identifier, clsName, lenSlots, lenValue)
          raise IndexError(textFmt(info))
        for (slot, val) in zip(sliceSlots, value):
          self.__setitem__(slot, val)
        else:
          return
      raise TypeException('key', identifier, str, int, slice)

    setattr(__setitem__, '__auto_generated__', True)
    return __setitem__

  @staticmethod
  def delItemFactory() -> __DELITEM__:
    """Creates '__delitem__' method that always raise TypeError"""

    def __delitem__(self, key: Any) -> Never:
      infoSpec = """EZData classes does not support deletion of slots, 
      but received "del self['%s']" on class: '%s'!"""
      clsName = type(self).__name__
      info = infoSpec % (key, clsName)
      raise TypeError(textFmt(info))

    setattr(__delitem__, '__auto_generated__', True)
    return __delitem__

  @staticmethod
  def getAttrFactory() -> __GETATTR__:
    """The getAttrFactory method is called when the class is created."""

    def __getattr__(self, key: str) -> Any:
      """If the given key is in one of the '__slots__', but this method
      still is invoked, it means that 'object.__getattribute__' was unable
      to retrieve a value for the given key. This method confirms that no
      value is present at 'self' nor in any base. In this case, the method
      attempts to set a default value at the given key for 'self'. """

      if key not in self.__slots__:  # Raises
        raise attributeErrorFactory(self, key)
      value = None
      exception = None
      slot = [s for s in self.__slot_objects__ if s.name == key][0]
      value = getattr(slot, 'defaultValue')
      setattr(self, key, value)
      return value

    setattr(__getattr__, '__auto_generated__', True)
    return __getattr__

  @staticmethod
  def setAttrFactory() -> __SETATTR__:
    """The setAttrFactory method is called when the class is created."""

    def __setattr__(self, key: str, value: Any) -> None:
      """Sets the value of the given key in the EZData instance."""
      if key not in self.__slots__:
        raise attributeErrorFactory(self, key)
      if type(self).isFrozen:
        try:
          oldValue = object.__getattribute__(self, key, )
        except AttributeError:
          return object.__setattr__(self, key, value)
        else:
          slot0 = self.__slot_objects__[0]
          clsName = slot0.ownerName
          oldValue = getattr(self, key, )
          raise FrozenEZException(key, clsName, oldValue, value)
      return object.__setattr__(self, key, value)

    setattr(__setattr__, '__auto_generated__', True)
    return __setattr__

  @staticmethod
  def delAttrFactory() -> __DELATTR__:
    """The delAttrFactory method is called when the class is created."""

    def __delattr__(self, key: str) -> Never:
      """Illegal deleter"""
      raise EZDeleteException(type(self), key, )

    setattr(__delattr__, '__auto_generated__', True)
    return __delattr__

  @staticmethod
  def asTupleFactory() -> AS_TUPLE:
    """The asTupleFactory method is called when the class is created."""

    def asTuple(self, ) -> tuple:
      """Returns a tuple of the values of the EZData instance."""
      return tuple(getattr(self, key) for key in self.__slots__)

    setattr(asTuple, '__auto_generated__', True)
    return asTuple

  @staticmethod
  def asDictFactory() -> AS_DICT:
    """The asDictFactory method is called when the class is created."""

    def asDict(self: EZData) -> dict:
      """Returns a dictionary of the values of the EZData instance."""
      return {key: getattr(self, key) for key in self.__slots__}

    setattr(asDict, '__auto_generated__', True)
    return asDict
