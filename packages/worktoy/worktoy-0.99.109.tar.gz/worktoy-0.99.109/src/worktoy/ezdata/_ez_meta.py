"""EZMeta provides the metaclass for the EZData class."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import EZDesc
from ..mcls import Base, BaseMeta
from ..ezdata import EZSpace

if TYPE_CHECKING:  # pragma: no cover
  pass


class EZMeta(BaseMeta):
  """EZMeta provides the metaclass for the EZData class."""

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Public Variables
  isFrozen = EZDesc('frozen', bool, False)
  isOrdered = EZDesc('order', bool, False)
  requireKwargs = EZDesc('kw_only', bool, False)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def __prepare__(mcls, name: str, bases: Base, **kwargs: dict) -> EZSpace:
    """Prepare the class namespace."""
    bases = (*[b for b in bases if b.__name__ != '_InitSub'],)
    return EZSpace(mcls, name, bases, **kwargs)
