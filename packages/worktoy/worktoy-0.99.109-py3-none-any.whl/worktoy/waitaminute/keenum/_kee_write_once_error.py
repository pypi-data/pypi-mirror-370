"""
KeeWriteOnceError provides a custom exception raised to indicate attempt
to modify a KeeNum enumeration member. All such members are write-once,
disallowing any and all modifications after initialization.

Note: Subclasses of Kee may implement 'value' with lazy evaluation,
setting it upon first access, after which it becomes immutable.
This implementation detail is invisible to KeeNum users; all
enumeration members appear strictly write-once.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class KeeWriteOnceError(AttributeError):
  """
  KeeWriteOnceError provides a custom exception raised to indicate attempt
  to modify a KeeNum enumeration member. All such members are write-once,
  disallowing any and all modifications after initialization.

  Note: Subclasses of Kee may implement 'value' with lazy evaluation,
  setting it upon first access, after which it becomes immutable.
  This implementation detail is invisible to KeeNum users; all
  enumeration members appear strictly write-once.
  """

  __slots__ = ('keenum', 'member', 'attribute')

  def __init__(self, member: Any, attribute: str) -> None:
    self.keenum = type(member)
    self.member = member
    self.attribute = attribute

  def __str__(self) -> str:
    infoSpec = """Attempt to modify attribute '%s' of member '%s' in '%s'!"""
    key = self.attribute
    num = str(self.member)
    kee = self.keenum.__name__
    info = infoSpec % (key, num, kee)
    from ...utilities import textFmt
    return textFmt(info)

  __repr__ = __str__
