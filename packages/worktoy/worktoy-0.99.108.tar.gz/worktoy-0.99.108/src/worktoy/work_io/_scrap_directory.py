"""The 'scrapDirectory' function removes empty directories."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..utilities import textFmt
from . import validateExistingDirectory

if TYPE_CHECKING:  # pragma: no cover
  pass


def scrapDirectory(dirPath: str, **kwargs) -> None:
  """
  Removes empty directory at the specified path.
  """
  try:
    validateExistingDirectory(dirPath)
  except FileNotFoundError as fileNotFoundError:
    if kwargs.get('strict', True):
      raise fileNotFoundError
  except NotADirectoryError as notADirectoryError:
    infoSpec = """The path received by 'scrapDirectory': '%s' is not a 
    directory!"""
    info = textFmt(infoSpec % dirPath)
    raise NotADirectoryError(info) from notADirectoryError
  else:
    os.rmdir(dirPath)
