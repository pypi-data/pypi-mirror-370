"""The 'validateExistingFile' function validates the existence of a file. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from worktoy.utilities import textFmt
from worktoy.waitaminute import PathSyntaxException

if TYPE_CHECKING:  # pragma: no cover
  pass


def validateExistingFile(file: str, **kwargs) -> str:
  """
  Validates that a given 'str' object points to an existing file.

  Args:
    file (str): The file to validate.

  Returns:
    str: The validated file.

  Raises:
    FileNotFoundError: If the file does not exist.
    IsADirectoryError: If the path is a directory.
  """
  if not os.path.isabs(file):
    raise PathSyntaxException(file)
  if not os.path.exists(file):
    if not kwargs.get('strict', True):
      return ''
    infoSpec = """No file exists at: '%s'!"""
    info = textFmt(infoSpec % file)
    raise FileNotFoundError(info)
  if not os.path.isfile(file):
    if not kwargs.get('strict', True):
      return ''
    infoSpec = """The path '%s' is not a file!"""
    info = textFmt(infoSpec % file)
    raise IsADirectoryError(info)
  return str(os.path.normpath(file))
