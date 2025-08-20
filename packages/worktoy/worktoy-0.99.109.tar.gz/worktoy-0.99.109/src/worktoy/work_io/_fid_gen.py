"""FidGen provides filename generator. Given a format specification and a
directory, it returns the next available filename of the given format."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..dispatch import overload
from ..desc import Field
from ..mcls import BaseObject
from ..utilities import maybe, stringList
from ..waitaminute import TypeException
from . import validateExistingDirectory, validateAvailablePath

if TYPE_CHECKING:  # pragma: no cover
  from typing import Optional, Any, TypeAlias

  ArgRes: TypeAlias = tuple[Optional[str], tuple[Any, ...]]


class FidGen(BaseObject):
  """
  FidGen provides filename generator. Given a format specification and a
  directory, it returns the next available filename of the given format.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Fallback variables
  __fallback_extension__ = 'json'
  __fallback_directory__ = os.path.abspath(os.path.dirname(__file__))

  #  Private variables
  __base_name__ = None
  __generated_names__ = None
  __file_spec__ = None
  __file_extension__ = None
  __file_directory__ = None

  #  Public variables
  fileExtension = Field()
  fileDirectory = Field()
  fileSpec = Field()

  #  Virtual variables
  filePath = Field()
  nextName = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getGeneratedNames(self) -> list[str]:
    """
    Getter-function for the generated names.
    """
    return maybe(self.__generated_names__, [])

  def _createFileSpec(self) -> None:
    """
    Creator-function for the file specification.
    """
    baseName = maybe(self.__base_name__, type(self).__name__, )
    chars = []
    for i, char in enumerate(baseName):
      if char.upper() == char:
        if i:
          chars.append('_%s' % char.lower())
          continue
        chars.append(char.lower())
        continue
      chars.append(char)
    snakeName = ''.join(chars)
    spec = """%s%%03d.%s""" % (snakeName, self.fileExtension)
    self.__file_spec__ = spec

  @fileSpec.GET
  def _getFileSpec(self, **kwargs) -> str:
    """Get the file specification."""
    if self.__file_spec__ is None:
      if kwargs.get('_recursion', False):
        raise RecursionError
      self._createFileSpec()
      return self._getFileSpec(_recursion=True, )
    if isinstance(self.__file_spec__, str):
      return str(os.path.join(self.fileDirectory, self.__file_spec__))
    raise TypeException('__file_spec__', self.__file_spec__, str)

  @fileExtension.GET
  def _getFileExtension(self, **kwargs) -> str:
    """Get the file extension."""
    return maybe(self.__file_extension__, self.__fallback_extension__, )

  @fileDirectory.GET
  def _getFileDirectory(self, **kwargs) -> str:
    """Get the file directory."""
    return maybe(self.__file_directory__, self.__fallback_directory__, )

  @nextName.GET
  def _getNextName(self, n=None) -> str:
    """
    Retrieves the next available filename based on the file specification.
    """
    n = maybe(n, 0)  # easier to cover wink wink
    while not validateAvailablePath(self.fileSpec % n, strict=False):
      n += 1
      if n > 100:
        break
    else:
      out = self.fileSpec % n
      self._addGeneratedName(out)
      return out
    raise RecursionError

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _addGeneratedName(self, name: str) -> None:
    """
    Adds a generated name to the list of generated names.
    """
    existing = self._getGeneratedNames()
    self.__generated_names__ = [*existing, name]

  @fileExtension.SET
  def _setFileExtension(self, value: str) -> None:
    """Set the file extension."""
    if not isinstance(value, str):
      raise TypeException('__file_extension__', value, str)
    if not value:
      raise ValueError('__file_extension__ must be a non-empty string')
    self.__file_extension__ = value

  @fileDirectory.SET
  def _setFileDirectory(self, value: str, **kwargs) -> None:
    """Set the file directory."""
    self.__file_directory__ = validateExistingDirectory(value)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @overload(str)
  def __init__(self, fileName: str, **kwargs) -> None:
    """Initialize the FidGen object."""
    self.__base_name__ = fileName
    if kwargs:
      self.__init__(**kwargs)

  @overload(str, str, str)
  @overload(str, str)
  def __init__(self, *args, **kwargs) -> None:
    posArgs = (*args,)
    argDir, posArgs = self._findDirectory(*posArgs)
    argExt, posArgs = self._findFileExtension(*posArgs)
    for arg in posArgs:
      self.baseName = arg
    if argDir is not None:
      self.fileDirectory = argDir
    if argExt is not None:
      self.fileExtension = argExt
    if kwargs:
      self.__init__(**kwargs)

  @overload()  # kwargs
  def __init__(self, **kwargs) -> None:
    """Initialize the FidGen object."""
    nameKeys = stringList("""name, file, fileName, filename, file_name""")
    extKeys = stringList("""ext, extension, file_extension""")
    dirKeys = stringList("""dir, directory, file_directory""")
    name, kwargs = self.parseKwargs(str, *nameKeys, **kwargs)
    ext, kwargs = self.parseKwargs(str, *extKeys, **kwargs)
    dir_, kwargs = self.parseKwargs(str, *dirKeys, **kwargs)
    if all([i is not None for i in [name, ext, dir_]]):
      self.__init__(name, ext, dir_, )

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __get__(self, instance: Any, owner: type, **kwargs) -> FidGen:
    """
    When the owning class is created, Python calls this method to allowing
    the type signatures to be updated with the owner class. This is
    necessary as the type signatures are able to reference the owning
    class before it is created by using the 'THIS' token object in place
    of it.
    """
    self.__context_caller__ = instance
    return self.__instance_get__()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @staticmethod
  def _findDirectory(*args) -> ArgRes:
    """Finds the directory in positional arguments. """
    unusedArgs = []
    posArgs = [*reversed(args), ]
    while posArgs:
      arg = posArgs.pop()
      if isinstance(arg, str):
        if os.path.isdir(arg):
          out = arg
          unusedArgs.extend(posArgs)
          break
        unusedArgs.append(arg)
    else:
      return None, (*args,)
    return out, (*unusedArgs,)

  @staticmethod
  def _getCommonExtensions() -> list[str]:
    """Returns a list of common file extensions."""
    return stringList(
        """json, txt, csv, xml, html, pdf, doc, csv, py, 
        mkv, mp4, mp3, wav, jpg, png, gif, zip, tar, gz, bz2"""
    )

  @classmethod
  def _findFileExtension(cls, *args) -> ArgRes:
    """Finds the file extension in positional arguments. """
    unusedArgs = []
    posArgs = [*reversed(args), ]
    while posArgs:
      arg = posArgs.pop()
      if isinstance(arg, str):
        if str.startswith(arg, '*.'):
          out = arg[2:]
          unusedArgs.extend(posArgs)
          break
        if arg in cls._getCommonExtensions():
          out = arg
          unusedArgs.extend(posArgs)
          break
        unusedArgs.append(arg)
    else:
      return None, (*args,)
    return out, (*unusedArgs,)
