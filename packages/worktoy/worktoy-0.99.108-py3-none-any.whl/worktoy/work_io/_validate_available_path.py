"""The 'validateExistingFile' function validates that a given 'str' object
is a valid file or directory path that does not already exist. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from worktoy.utilities import textFmt
from worktoy.waitaminute import PathSyntaxException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Union, TypeAlias, LiteralString

  Path: TypeAlias = Union[str, bytes, LiteralString]


def validateAvailablePath(path: Path, **kwargs) -> str:
  """
  Validates that a given 'str' object is a valid file or directory path
  that does not already exist.

  Args:
    path (str): The path to validate.

  Returns:
    str: The validated path.

  Raises:
    FileExistsError: If the file or directory already exists.
    NotADirectoryError: If the path is not a directory.
  """
  if not os.path.isabs(path):
    raise PathSyntaxException(path)
  if os.path.exists(path):
    if not kwargs.get('strict', True):
      return ''
    infoSpec = """The path '%s' already exists!"""
    info = textFmt(infoSpec % path)
    raise FileExistsError(info)
  return str(os.path.normpath(path))
