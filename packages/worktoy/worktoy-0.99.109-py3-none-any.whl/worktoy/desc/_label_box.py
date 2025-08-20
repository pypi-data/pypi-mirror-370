"""
LabelBox subclasses AttriBox and changes the read-write behaviour to
read-many and write-once. If an instance of LabelBox receives a call to
instance get before any value has been set, it will attempt to create a
value like the AttriBox, but then this value counts as the one write
allowed. Alternatively, if the value is set before the first get,
the value set, subject to type guards, will henceforth be returned.

To indicate that the value must be set, the DELETED sentinel may be passed.

class Foo:
  bar = LabelBox[str](DELETED)  # require a value to be set before first get
  baz = LabelBox[str]('untitled')  # uses 'untitled' as default value
  #  If the default value is ever retrieved, it uses up the single write
  #  operation allowed.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import AttriBox
from ..core.sentinels import DELETED
from ..waitaminute import WriteOnceError

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class LabelBox(AttriBox):
  """
  LabelBox subclasses AttriBox and changes the read-write behaviour to
  read-many and write-once. If an instance of LabelBox receives a call to
  instance get before any value has been set, it will attempt to create a
  value like the AttriBox, but then this value counts as the one write
  allowed. Alternatively, if the value is set before the first get,
  the value set, subject to type guards, will henceforth be returned.
  """

  def __instance_set__(self, value: Any, *args, **kwargs) -> None:
    """
    Sets the value of the field for the given instance. If the value is
    not set, it initializes it with a new instance of the field type.
    """
    instance = self.getContextInstance()
    fieldType = self.getFieldType()
    pvtName = self.getPrivateName()
    if value is DELETED:
      return setattr(instance, pvtName, DELETED)
    if hasattr(instance, pvtName):
      if getattr(instance, pvtName) is not DELETED:
        oldValue = getattr(instance, pvtName)
        raise WriteOnceError(self, oldValue, value)
    if isinstance(value, fieldType):
      return setattr(instance, pvtName, value)
    setattr(instance, pvtName, fieldType(value))
