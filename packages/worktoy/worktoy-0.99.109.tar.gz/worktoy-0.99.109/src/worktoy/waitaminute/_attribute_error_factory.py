"""
The 'attributeErrorFactory' instantiates 'AttributeError' with a message
that matches the built-in message if a given object does not have a given
attribute. This allows simulating the absense of an attribute. For example:

class Bar:  # secret descriptor!

  __fallback_value__ = 'lol'
  __field_name__ = None
  __field_owner__ = None

  def __set_name__(self, owner: type, name: str) -> None:
    self.__field_name__ = name
    self.__field_owner__ = owner

  def __get__(self, instance: object, owner: type) -> object:
    if instance is None:
      return self
    if hasattr(owner, '__trust_me_bro__'):
      pvtName = '__%s__' % self.__field_name__
      fallback = self.__fallback_value__
      return getattr(instance, pvtName, fallback)
    raise attributeErrorFactory(owner, self.__field_name__)


class Foo:
  __trust_me_bro__ = True
  bar = Bar()


class Sus:
  bar = Bar()


if __name__ == '__main__':
  foo = Foo()
  print(foo.bar)  # This will return the fallback value 'lol'
  sus = Sus()
  print(sus.bar)  # Raises AttributeError


The above attribute error will have the following message:
AttributeError: 'Sus' object has no attribute 'bar'
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


def attributeErrorFactory(owner: Any, field: str) -> AttributeError:
  """
  Factory function that creates an AttributeError with a message that
  matches the built-in message if a given object does not have a given
  attribute.
  """
  if isinstance(owner, type):
    owner = owner.__name__
  elif not isinstance(owner, str):
    owner = type(owner).__name__
  infoSpec = """AttributeError: '%s' object has no attribute '%s'"""
  info = infoSpec % (str(owner), str(field))
  return AttributeError(textFmt(info))
