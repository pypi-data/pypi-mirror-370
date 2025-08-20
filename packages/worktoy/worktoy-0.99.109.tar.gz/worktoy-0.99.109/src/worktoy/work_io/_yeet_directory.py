"""
The 'yeetDirectory' function removes a directory with all contents.
Effectively the same as: 'rm -rf <directory>'.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..utilities import textFmt
from ..waitaminute import PathSyntaxException

if TYPE_CHECKING:  # pragma: no cover
  pass


def yeetDirectory(dirPath: str, **kwargs) -> None:
  """
  Removes a directory with all contents. Effectively the same as: 'rm -rf
  <directory>'.

  Args:
    dirPath (str): The path to the directory to remove.

  Raises:
    FileNotFoundError: If the directory does not exist.
    NotADirectoryError: If the path is not a directory.
    PathSyntaxException: If the path is not absolute.
  """
  if not os.path.isabs(dirPath):
    raise PathSyntaxException(dirPath)
  if not os.path.exists(dirPath):
    if not kwargs.get('strict', True):
      return
    infoSpec = """No directory exists at: '%s'!"""
    info = textFmt(infoSpec % dirPath)
    raise FileNotFoundError(info)
  for item in os.listdir(dirPath):
    itemPath = os.path.join(dirPath, item)
    if os.path.isdir(itemPath):
      yeetDirectory(itemPath, strict=False)
      continue
    os.remove(itemPath)
  else:
    os.rmdir(dirPath)
