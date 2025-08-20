"""The 'newDirectory' function creates a new directory at the specified
path. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from . import validateAvailablePath

if TYPE_CHECKING:  # pragma: no cover
  from typing import Union, TypeAlias, LiteralString

  Path: TypeAlias = Union[str, bytes, LiteralString]


def newDirectory(path: Path) -> str:
  """
  Creates a new directory at the specified path.

  Args:
    path (str): The path where the new directory will be created.

  Returns:
    str: The path of the newly created directory.

  Raises:
    FileExistsError: If the directory already exists.
    NotADirectoryError: If the path is not a directory.
    PathSyntaxException: If the path is not absolute.
  """
  validateAvailablePath(path)
  os.makedirs(path, exist_ok=True)
  return os.path.normpath(path)
