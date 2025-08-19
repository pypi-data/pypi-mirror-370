"""The 'worktoy.workWrap' function receives an integer defining character
width and any number of strings. The function then returns a list of
strings containing the words from the strings received such that each
entry in the list does not exceed the character width. """
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations


def wordWrap(width: int, *textLines, **kwargs) -> str:
  """The wordwrap function wraps the input text to a specified width."""
  newLine = kwargs.get('newLine', '<br>').strip().lower()
  if not isinstance(width, int):
    from ..waitaminute import TypeException
    raise TypeException('width', width, int)
  words = []
  for line in textLines:
    if not isinstance(line, str):
      from ..waitaminute import TypeException
      raise TypeException('line', line, str)
    words.extend(line.split())
  lines = []
  line = []
  while words:
    word = words.pop(0)
    if word.lower() == newLine or len(' '.join([*line, word])) > width:
      lines.append(' '.join(line))
      line = []
      continue
    line.append(word)
  return '\n'.join(lines)
