"""
NameHook filters named used in the namespace system.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...core.sentinels import METACALL
from ...waitaminute.meta import QuestionableSyntax, DelException
from . import AbstractSpaceHook

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, TypeAlias

  NearMiss: TypeAlias = tuple[str, str]


class NamespaceHook(AbstractSpaceHook):
  """
  NameHook intercepts names added to the namespace and filters out
  "near-miss" identifiers that resemble critical Python dunder methods.
  These mistakes often go unnoticed, leading to subtle bugs or broken
  protocol support.

  This hook raises a QuestionableSyntax exception when such names are
  detected during assignment in the namespace.

  ## Purpose

  Many magic methods in Python have specific names that must be spelled
  exactly. If a user misspells one by inserting or omitting underscores,
  the name is silently ignored by Python and treated as an ordinary
  attribute — sometimes shadowing a builtin or behaving unexpectedly.

  ## Near-miss Examples
  ___________________________________________________________________________
  | Intended Name  | Mistyped Name | Notes                                 |
  |----------------|---------------|---------------------------------------|
  | `__set_name__` | `__setname__` | Misses descriptor registration        |
  | `__getitem__`  | `__get_item__`| Breaks item access in dict-like APIs  |
  | `__setitem__`  | `__set_item__`| Same as above                         |
  | `__delitem__`  | `__del_item__`| Silent failure of delete protocol     |
  | `__delete__`   | `__del__`     | High risk: __del__ ties to GC hooks   |
  ¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
  These errors can be especially difficult to diagnose, as they usually
  do not raise any errors directly — instead, they silently fail to
  participate in expected behaviors or override builtin methods.

  ## Usage
  To use NameHook, simply declare it in your namespace class:

  class Space(AbstractNamespace):  # Must inherit from AbstractNamespace
    #  Custom namespace class inheriting from AbstractNamespace
    nameHook = NameHook()  # Register the hook
"""

  @classmethod
  def _getClassDunders(cls) -> list[str]:
    """
    Get the class dunder names that are allowed in the namespace.
    """
    return [
        '__class_call__',
        '__class_init__',
        '__class_instancecheck__',
        '__class_subclasscheck__',
        '__class_str__',
        '__class_repr__',
        '__class_iter__',
        '__class_next__',
        '__class_bool__',
        '__class_contains__',
        '__class_len__',
        '__class_hash__',
        #  '__class_eq__',  Exhibits highly undefined behaviour!
        #  '__class_ne__',  See above
        #  '__class_getitem__',  See footnote below
        '__class_setitem__',
        '__class_delitem__',
        '__class_getattr__',
        '__class_setattr__',
        '__class_delattr__',
        #  NOTE: '__class_getitem__' is commented out, rather than
        #  omitted, allowing this explanatory note to be found easily.
        #
        #  Since Python 3.7, support for the '__class_getitem__' became a
        #  feature of the interpreter itself. In fact, it inspired the
        #  implementation of all of the above class level hooks. Uniquely
        #  for '__class_getitem__', if it is defined on the class,
        #  the metaclass implementation of '__getitem__' will not be
        #  called.
        #
        #  This behaviour is opposite to the other hooks, as they
        #  are implemented here. 'AbstractMetaclass' provides
        #  implementations of the dunder methods, such that derived
        #  may implement the methods to achieve behaviour otherwise
        #  requiring metaclass reimplementation.
    ]

  @classmethod
  def _getNearMisses(cls) -> list[NearMiss]:
    """
    Get the near-miss names.
    """
    return [
        ('__set_name__', '__setname__'),  # NOQA, miss-spelled name
        ('__getitem__', '__get_item__'),
        ('__setitem__', '__set_item__'),
        ('__delitem__', '__del_item__'),
    ]

  @classmethod
  def _validateName(cls, name: str) -> bool:
    """
    Compares the name to list of potential near-miss names. If the name
    is a near-miss, a QuestionableSyntax exception is raised.
    """
    nearMisses = cls._getNearMisses()
    for nearMiss in nearMisses:
      if name == nearMiss[1]:
        raise QuestionableSyntax(*nearMiss, )
    return False

  def _validateDel(self, ) -> bool:
    """
    Validates that the current class is allowed to implement '__del__'.
    """
    if 'trustMeBro' in self.space.getKwargs():
      return True
    return False

  def setItemPhase(self, key: str, val: Any, old: Any = None, ) -> bool:
    """
    Hook for setItem. This is called before the __setitem__ method of
    the namespace object is called. The default implementation does nothing
    and returns False.
    """
    if key == '__del__':
      if self._validateDel():
        return False
      mcls = self.space.getMetaclass()
      name = self.space.getClassName()
      bases = self.space.getBases()
      raise DelException(mcls, name, bases, self.space)
    return self._validateName(key)

  def preCompilePhase(self, compiledSpace: dict) -> dict:
    """
    Populates the class dunder hooks with the 'METACALL' sentinel object.
    """
    dunderNames = self._getClassDunders()
    for name in dunderNames:
      try:
        _ = self.space.deepGetItem(name)
      except KeyError as keyError:
        compiledSpace[name] = METACALL
        continue
      else:
        continue
    return compiledSpace

  def postCompilePhase(self, compiledSpace: dict) -> dict:
    """
    Hook for postCompile. This is called after the __init__ method of
    the namespace object is called. The default implementation does nothing
    and returns the contents unchanged.
    """
    return compiledSpace
