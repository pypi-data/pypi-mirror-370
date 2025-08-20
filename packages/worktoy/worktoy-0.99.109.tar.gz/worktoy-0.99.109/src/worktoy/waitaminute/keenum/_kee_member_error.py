"""
KeeMemberError provides a custom exception raised to indicate that an
object that is an instance of 'KeeNum' is not a member of a particular
enumeration.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from ...keenum import KeeMeta, KeeNum


class KeeMemberError(KeyError):
  """
  KeeMemberError provides a custom exception raised to indicate that an
  object that is an instance of 'KeeNum' is not a member of a particular
  enumeration.
  """

  __slots__ = ('keenum', 'member')

  def __init__(self, keenum: KeeMeta, member: KeeNum) -> None:
    self.keenum, self.member = keenum, member

  def __str__(self) -> str:
    infoSpec = """KeeNum object: '%s' is not a member of the enumeration 
    '%s'!"""
    info = infoSpec % (self.member, self.keenum)
    from ...utilities import textFmt
    return textFmt(info, )

  __repr__ = __str__
