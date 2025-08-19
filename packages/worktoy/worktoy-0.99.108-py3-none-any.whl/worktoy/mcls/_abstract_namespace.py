"""
AbstractNamespace class provides a base class for custom namespace
objects used in custom metaclasses.
"""
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt, resolveMRO
from ..waitaminute.meta import HookException, DuplicateHook
from . import Base
from .space_hooks import NamespaceHook, ReservedNamespaceHook

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, TypeAlias, Iterator, Union, Self
  from .space_hooks import AbstractSpaceHook

  Bases: TypeAlias = tuple[type, ...]
  Hooks: TypeAlias = list[AbstractSpaceHook]
  MROSpace: TypeAlias = dict[str, list[Any]]
  TypeName: TypeAlias = Union[str, type]


class AbstractNamespace(dict):
  """
  AbstractNamespace defines the custom execution environment used by
  AbstractMetaclass during class construction. It provides a controlled
  and extensible context for evaluating class bodies, enabling advanced
  metaprogramming behavior.

  The core feature of AbstractNamespace is its support for modular
  hook-based behavior. Hooks are instances of subclasses of AbstractHook,
  declared directly within the body of the namespace class. Upon
  declaration, each hook registers itself with the namespace via the
  descriptor protocol.

  These hooks allow interception and transformation of key events during
  class construction, including symbol access, assignment, and final
  namespace compilation. For details on available hook methods and their
  intended usage, refer to the AbstractHook documentation.

  This design allows complex functionality, such as decorator-based
  overload resolution and placeholder replacement, to be cleanly
  separated into reusable components. By defining a namespace subclass
  with the desired combination of hooks, users can tailor the behavior of
  class construction without modifying the core metaclass logic.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  __owner_hooks_list_name__ = '__hook_objects__'

  #  Private Variables
  __meta_class__ = None
  __class_name__ = None
  __base_classes__ = None
  __class_mro__ = None
  __key_args__ = None
  __hash_value__ = None
  __compiled_space__ = None
  __deferred_annotations__ = None
  __type_annotations__ = None
  __class_annotations__ = None
  __global_scope__ = None

  #  Public Variables
  reservedNameHook = ReservedNamespaceHook()
  nameHook = NamespaceHook()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def getBases(self) -> Bases:
    """Returns the base classes of the class under creation."""
    return (*self.__base_classes__,)

  def deepGetItem(self, item: str, **kwargs) -> Any:
    """
    Looks up the given key in the self. If not found, then each base class
    is searched.
    """
    for key, val in dict.items(self, ):
      if key == item:
        return val
    if item in self.getMROSpace():
      return self.getMROSpace()[item]
    raise KeyError(item)

  @classmethod
  def getHookListName(cls, ) -> str:
    """Getter-function for the name of the hook list. """
    if TYPE_CHECKING:  # pragma: no cover
      assert isinstance(cls, dict)
    return cls.__owner_hooks_list_name__

  def getHooks(self, owner: type = None) -> Iterator[AbstractSpaceHook]:
    """Getter-function for the AbstractHook classes. """
    cls = type(self)
    hooks = self.classGetHooks()
    for hook in hooks:
      out = hook.__get__(self, cls, )
      setattr(out, '__space_object__', self)
      yield out

  @classmethod
  def classGetHooks(cls, ) -> Hooks:
    """
    Returns the hooks registered on this class or baseclasses.
    """
    pvtName = cls.getHookListName()
    out = []
    for base in cls.__mro__:
      if issubclass(base, dict):
        hooks = getattr(base, pvtName, [])
        for hook in hooks:
          if hook in out:
            continue
          out.append(hook)
    return out

  def getMetaclass(self, ) -> type:
    """Returns the metaclass."""
    return self.__meta_class__

  def getClassName(self, ) -> str:
    """Returns the name of the class."""
    return self.__class_name__

  def getKwargs(self, ) -> dict:
    """Returns the keyword arguments passed to the class."""
    return {**self.__key_args__, **dict()}

  def getMRO(self, ) -> list[type]:
    """Returns the method resolution order of the class."""
    return self.__class_mro__

  def getMROSpace(self, ) -> MROSpace:
    """Combines the namespaces of all bases in the MRO into a single
    'dict' object with each value being a list of all values provided. """
    mroClasses = [b for b in self.getMRO() if hasattr(b, '__namespace__')]
    mroSpaces = [getattr(b, '__namespace__', ) for b in mroClasses]
    compiledSpaces = [getattr(s, '__compiled_space__') for s in mroSpaces]
    out = dict()
    for compiledSpace in compiledSpaces:
      for key, val in compiledSpace.items():
        existing = out.get(key, [])
        out[key] = [*existing, val]
    return out

  def getMRONamespaces(self) -> list[Self]:
    """Returns for each class in the MRO the instance of
    AbstractNamespace, or subclass of it, used to create it. Nothing is
    returned for classes not derive from 'AbstractMetaclass' or subclass. """
    mroClasses = [b for b in self.getMRO() if hasattr(b, '__namespace__')]
    return [getattr(b, '__namespace__', None) for b in mroClasses]

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def addHook(cls, hook: AbstractSpaceHook) -> None:
    """Adds a hook to the list of hooks. """
    existingHooks = cls.classGetHooks()
    for existingHook in existingHooks:
      existingName = existingHook.getFieldName()
      newName = hook.getFieldName()
      if existingName == newName:
        if existingHook is hook:
          return
        hooks = (existingHook, hook)
        raise DuplicateHook(cls, newName, *hooks)
    pvtName = cls.getHookListName()
    setattr(cls, pvtName, [*existingHooks, hook])

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, mcls: type, name: str, bases: Base, **kwargs) -> None:
    self.__meta_class__ = mcls
    self.__class_name__ = name
    self.__base_classes__ = [*bases, ]
    self.__key_args__ = kwargs or {}
    self.__class_mro__ = resolveMRO(*bases, )
    for hook in self.getHooks():
      setattr(hook, '__space_object__', self)
      hook.preparePhase(self)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __getitem__(self, key: str, **kwargs) -> Any:
    """Returns the value of the key."""
    try:
      val = dict.__getitem__(self, key)
    except KeyError as keyError:
      val = keyError
    for hook in self.getHooks():
      setattr(hook, '__space_object__', self)
      try:
        hook.getItemPhase(key, val)
      except Exception as exception:
        raise HookException(exception, self, key, val, hook)
    else:
      if isinstance(val, KeyError):
        raise val
      return val

  def __setitem__(self, key: str, val: Any, **kwargs) -> None:
    """Sets the value of the key."""
    # if key == '__module__':
    #   globScope = {**vars(sys.modules[val]), }
    #   object.__setattr__(self, '__global_scope__', globScope)
    try:
      oldVal = dict.__getitem__(self, key)
    except KeyError:
      oldVal = None
    for hook in self.getHooks():
      setattr(hook, '__space_object__', self)
      if hook.setItemPhase(key, val, oldVal):
        break  # Breaks out of the loop if handled by hook.
    else:  # If no 'break', the 'else' block is executed.
      dict.__setitem__(self, key, val)

  def __str__(self, ) -> str:
    """Returns the string representation of the namespace object."""
    bases = self.getBases()
    spaceName = type(self).__name__
    clsName = self.getClassName()
    baseNames = ', '.join([base.__name__ for base in bases])
    mclsName = self.getMetaclass().__name__
    info = """Namespace object of type: '%s' created by the '__prepare__' 
    method on metaclass: '%s' with bases: (%s) to create class: '%s'."""
    return textFmt(info % (spaceName, mclsName, baseNames, clsName))

  def __repr__(self, ) -> str:
    """Returns the string representation of the namespace object."""
    bases = self.getBases()
    spaceName = type(self).__name__
    clsName = self.getClassName()
    mclsName = self.getMetaclass().__name__
    baseNames = '%s' % ', '.join([base.__name__ for base in bases])
    mclsName = self.getMetaclass().__name__
    args = """%s, '%s', (%s)""" % (mclsName, clsName, baseNames)
    kwargs = [(k, v) for (k, v) in self.getKwargs().items()]
    kwargStr = ', '.join(['%s=%s' % (k, str(v)) for (k, v) in kwargs])
    if kwargStr:
      kwargStr = ', %s' % kwargStr
    return """%s(%s%s)""" % (spaceName, args, kwargStr)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def preCompile(self, namespace: dict = None) -> dict:
    """The return value from this method is passed to the compile method.
    Subclasses can implement this method to provide special objects at
    particular names in the namespace. By default, an empty dictionary is
    returned. """
    if namespace is None:
      namespace = dict()
    for hook in self.getHooks():
      setattr(hook, '__space_object__', self)
      namespace = hook.preCompilePhase(namespace)
    return namespace

  def compile(self, namespace: dict = None) -> dict:
    """This method is responsible for building the final namespace object.
    Subclasses may reimplement preCompile or postCompile as needed,
    but must not reimplement this method."""
    namespace = self.preCompile(namespace)
    for (key, val) in dict.items(self, ):
      namespace[key] = val
    namespace = self.postCompile(namespace)
    namespace['__metaclass__'] = self.getMetaclass()
    namespace['__namespace__'] = self
    namespace['__keyword_arguments__'] = self.getKwargs()
    self.__compiled_space__ = namespace
    return namespace

  def postCompile(self, namespace: dict) -> dict:
    """The object returned from this method is passed to the __new__
    method in the owning metaclass. By default, this method returns dict
    object created by the compile method after performing certain
    validations. Subclasses can implement this method to provide further
    processing of the compiled object. """
    for hook in self.getHooks():
      setattr(hook, '__space_object__', self)
      namespace = hook.postCompilePhase(namespace)
    return namespace
