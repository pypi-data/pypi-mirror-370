"""The 'validateExistingDirectory' function validates that a given 'str'
object points to an existing directory. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from worktoy.utilities import textFmt
from worktoy.waitaminute import PathSyntaxException

if TYPE_CHECKING:  # pragma: no cover
  pass


def validateExistingDirectory(directory: str, **kwargs) -> str:
  """
  Validates that a given 'str' object points to an existing directory.

  Args:
    directory (str): The directory to validate.

  Returns:
    str: The validated directory.

  Raises:
    FileNotFoundError: If the directory does not exist.
    NotADirectoryError: If the path is not a directory.
  """
  if not os.path.isabs(directory):
    raise PathSyntaxException(directory)
  if not os.path.exists(directory):
    if not kwargs.get('strict', True):
      return ''
    infoSpec = """No directory exists at: '%s'!"""
    info = textFmt(infoSpec % directory)
    raise FileNotFoundError(info)
  if not os.path.isdir(directory):
    if not kwargs.get('strict', True):
      return ''
    infoSpec = """The path '%s' is not a directory!"""
    info = textFmt(infoSpec % directory)
    raise NotADirectoryError(info)
  return os.path.normpath(directory)
