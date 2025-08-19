"""
The 'textFmt' function provides quick formatting of text. This is
motivated by the fact that Python strings spanning multiple lines contains
the linebreaks verbatim, which is almost never desired.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


def textFmt(*args: Any, **kwargs: Any) -> str:
  """
  Formats a multi-line string by replacing all continuous whitespace,
  including new lines, with a single space. Additionally, intended line
  breaks and indentations may be specified using '<br>' and '<tab>'
  respectively as indicating tokens.

  Args:
    *args: Any number of 'str' objects to be concatenated and formatted.
    Please note that any 'arg' not an instance of 'str' will be replaced
    with 'str(arg)'.
  Kwargs: Additional formatting options:
      - 'newLineToken': Use a different token to indicate line breaks,
      defaults to '<br>'.
      - 'tabToken': Use a different token to indicate indentation,
      defaults to '<tab>'.
      - 'newLineSymbol': Symbol in the returned string indicating new
      line. By default, the value at 'os.linesep' is used. On linux,
      this value is '\n' and on Windows it is '\r\n'.
      - 'indentSymbol': Symbol in the returned string indicating one level
      of indentation, defaults to two spaces.

  Usage:
    from __future__ import annotations

    import sys

    def main(*args) -> int:
      #  Example script
      exampleText = \"\"\"This is the first line,
      but we are still here! <br>But now we are on the second line!
      still here! <br><tab>Third line is even indented!\"\"\"
      formattedText = textFmt(exampleText)
      print(formattedText)

    if __name__ == '__main__':
      sys.exit(main(*sys.argv[1:]))

    output:
   |  This is the first line, but we are still here!
   |  But now we are on the second line!
   |    Third line is even indented!
  """
  if not args:
    return ''
  words = []
  for arg in args:
    if isinstance(arg, str):
      if arg:
        words.append(arg)
    else:
      words.append(str(arg))
  else:
    if not words:
      return ''
  #  Specify tokens and symbols
  nLIn = kwargs.get('newLineToken', '<br>')
  tabIn = kwargs.get('tabToken', '<tab>')
  newTemp = '{{NEWLINE}}'
  tabTemp = '{{TAB}}'
  nLOut = kwargs.get('newLineSymbol', os.linesep)
  tabOut = kwargs.get('indentSymbol', '  ')
  #  Replace tokens with temporary symbols
  parts = [a.replace(nLIn, newTemp).replace(tabIn, tabTemp) for a in words]
  #  Join the parts into a single string
  text = ' '.join(str(part) for part in parts)
  #  Replace multiple spaces with a single space
  text = ' '.join(text.split())
  #  Replace newlines and tabs with the appropriate symbols
  return text.replace(newTemp, nLOut).replace(tabTemp, tabOut).strip()
