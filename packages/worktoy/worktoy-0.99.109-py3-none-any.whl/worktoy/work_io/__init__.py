"""The 'worktoy.work_io' module provides I/O functionalities. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._validate_existing_directory import validateExistingDirectory
from ._validate_existing_file import validateExistingFile
from ._validate_available_path import validateAvailablePath
from ._fid_gen import FidGen
from ._scrap_directory import scrapDirectory
from ._new_directory import newDirectory
from ._yeet_directory import yeetDirectory

__all__ = [
    'validateExistingDirectory',
    'validateExistingFile',
    'validateAvailablePath',
    'FidGen',
    'scrapDirectory',
    'newDirectory',
    'yeetDirectory',
]
