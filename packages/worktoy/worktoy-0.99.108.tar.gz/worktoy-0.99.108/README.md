[![wakatime](https://wakatime.com/badge/github/AsgerJon/WorkToy.svg)](https://wakatime.com/badge/github/AsgerJon/WorkToy) [![codecov](https://codecov.io/gh/AsgerJon/WorkToy/graph/badge.svg?token=FC0KFZJ7JK)](https://codecov.io/gh/AsgerJon/WorkToy)
[![PyPI version](https://badge.fury.io/py/worktoy.svg)](https://pypi.org/project/worktoy/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

# worktoy v0.99.xx

The **worktoy** provides utilities for Python development focused on
reducing boilerplate code, type-safety and readability. Each release is
tested thoroughly on each supported Python version from 3.7* to 3.13.

Note: *Not an endorsement. If your open source project requires Python 3.7,
it's time to update. There are plenty of people willing to help you. If
your project is not open source, you are advised to read AGPL-3.0 on your
way out.

# Table of Contents

- [Installation](#installation)
- [Introduction](#introduction)
- [Features](#features)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

# Installation

Install with pip:

```bash
pip install worktoy
```

When version 1.0 drops, nightly builds will be available by including the
`--pre` flag:

```bash
pip install --pre worktoy
```

# Introduction

Python should be easy. Easy to write, but also easy to read. **worktoy**
helps you write Python code that is as easy to read as it is to write.

# Features

Use `AttriBox` to create one-line type-safe attributes or `Field` to
customize attribute access. Instead of parsing `*args` and
`**kwargs`, use `overload` to provide type specific implementations of
the same function.

# Usage

Below is an example implementation of a complex number using **worktoy**.
Please refer to the docstrings for more information on the individual
components.

```python
"""
ComplexNumber provides a class representation of the complex number
using features found in the 'worktoy' library. Briefly, a complex number
has a real and imaginary part both of which represented here as instances
of 'AttriBox'. The class inherits from the 'BaseObject' class allowing it
to overload functions based on types.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import sys
from math import atan2, cos, sin  # Provides necessary math functions

from worktoy.mcls import BaseObject
from worktoy.desc import AttriBox, Field
from worktoy.dispatch import overload
from worktoy.core.sentinels import THIS

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from typing import Self  # For type hinting in the class methods


class ComplexNumber(BaseObject):
  """
  Function overloading requires customization of the 'type' object
  itself. 'worktoy' provides 'BaseObject' which is derived from the
  'BaseMeta' class which implements the necessary methods for
  overloading.
  """

  REAL = AttriBox[float](0.0)  # Yes, really. AttriBox[TYPE](DEFAULT)
  IMAG = AttriBox[float](0.0)  # But linters may indicate warnings

  ABS = Field()  # Field is quite similar to property
  ARG = Field()  # Requiring accessor methods to be explicitly decorated.

  #  Constructor methods

  @overload(float, float)  # Instantiating from two floats
  @overload(float, int)
  @overload(int, float)
  @overload(int, int)
  def __init__(self, realPart: float, imagPart: float) -> None:
    """
    This constructor is overloaded with any combination of int and float.
    Since the overload decorator returns the function object without
    changes, as many overloads as needed can be added.
    """
    self.REAL = float(realPart)
    self.IMAG = float(imagPart)

  @overload(complex)  # Instantiating from a complex number instead
  def __init__(self, complexNumber: complex) -> None:
    """
    To instantiate from a complex number, a different function
    implementation is necessary.
    """
    self.REAL = complexNumber.real
    self.IMAG = complexNumber.imag

  @overload(THIS)  # THIS?
  def __init__(self, other: Self) -> None:
    """
    But what if you wanted to instantiate the class from another instance
    of the class? The moment this function object is created, the owning
    class itself does not actually exist yet. 'worktoy' provides the
    special token object 'THIS' to indicate the class yet to be created.
    """
    self.REAL = other.REAL
    self.IMAG = other.IMAG

  @overload()  # No arguments
  def __init__(self, **kwargs) -> None:
    """
    This constructor is called when no positional arguments are given. The
    positional arguments determine which constructor is called. The above
    constructors do not support keyword arguments, but this one does.
    """
    if 'real' in kwargs:
      self.REAL = kwargs['real']
    if 'imag' in kwargs:
      self.IMAG = kwargs['imag']

  #  Virtual accessor methods
  @ABS.GET
  def _getAbs(self) -> float:
    """
    The @ABS.GET decorator specifies that this method is the getter
    for the ABS property. When the ABS property is accessed through an
    instance of the class, this method is called.
    """
    return abs(self)  # Yes, we implement __abs__ further down

  @ABS.SET
  def _setAbs(self, value: float) -> None:
    """
    But how does one 'set' a virtual attribute? Well, however one
    wants! In this case, we scale the number to the new absolute value.
    """
    if not self:  # Yes, __bool__ is implemented further down
      raise ZeroDivisionError
    scale = value / abs(self)
    self.REAL *= scale
    self.IMAG *= scale

  @ARG.GET
  def _getArg(self) -> float:
    """
    The ARG property is the argument of the complex number. The @ARG.GET
    decorator specifies this method as getter.
    """
    return atan2(self.IMAG, self.REAL)  # With math.atan2

  @ARG.SET
  def _setArg(self, value: float) -> None:
    """
    The @ARG.SET decorator specifies this method as setter for the ARG
    property. The argument is set by rotating the complex number to the
    new angle.
    """
    if not self:
      raise ZeroDivisionError
    self.REAL = self.ABS * cos(value)
    self.IMAG = self.ABS * sin(value)

  #  Bonus dunder methods as promised

  def __abs__(self, ) -> float:
    """
    The __abs__ method is called when the built-in abs() function is
    called on an instance of the class. It returns the absolute value
    of the complex number.
    """
    return (self.REAL ** 2 + self.IMAG ** 2) ** 0.5

  def __bool__(self, ) -> bool:
    """
    The __bool__ method is called when the built-in bool() function is
    called on an instance of the class. It returns True if the complex
    number is not zero, and False otherwise.
    """
    return True if self.REAL ** 2 + self.IMAG ** 2 > 1e-12 else False

  def __complex__(self, ) -> complex:
    """
    The __complex__ method is called when the built-in complex() function
    is called on an instance of the class. It returns the complex number
    as a complex object.
    """
    return self.REAL + self.IMAG * 1j

  def __str__(self, ) -> str:
    """
    This returns a human-readable string representation of the complex
    number.
    """
    return """%.3f + %.3fJ""" % (self.REAL, self.IMAG)  # Yes, 'J'

  def __repr__(self, ) -> str:
    """
    The string returned by this method should ideally be a valid Python
    expression that recreates the 'self' object when passed to 'eval()'.
    """
    clsName = type(self).__name__  # Get the class name
    x, y = self.REAL, self.IMAG  # Get the real and imaginary parts
    return """%s(%s, %s)""" % (clsName, x, y)

  #  Further dunder methods are left as an exercise to the try-hard readers.


def main(*args) -> int:
  """In the following, we will test the class. """
  # Let's create a few complex numbers
  z1 = ComplexNumber(69, 420)  # two ints
  z2 = ComplexNumber(0.1337, 80085)  # a float and an int
  z3 = ComplexNumber(z1)  # another complex number
  z4 = ComplexNumber(69 + 420 * 1j)  # a complex number
  z5 = ComplexNumber(real=1337, imag=420)  # from keyword arguments
  z0 = ComplexNumber()  # no arguments
  Z = [z0, z1, z2, z3, z4, z5]  # list of complex numbers
  print("""Testing ComplexNumber""")
  for i, z in enumerate(Z):
    if i:
      print(' --- ')
    print('ComplexNumber: z%d = %s' % (i, repr(z)))
    try:
      if (z.ABS - abs(complex(z))) ** 2 > 1e-10:
        raise ValueError('ABS should be equal to abs(complex(z)')
      if (z.REAL - complex(z).real) ** 2 > 1e-10:
        raise ValueError('REAL should be equal to complex(z).real')
      if (z.IMAG - complex(z).imag) ** 2 > 1e-10:
        raise ValueError('IMAG should be equal to complex(z).imag')

    except ValueError as valueError:
      print('oh oh!', valueError)
      break  # Better stop and do some debugging!
    else:
      print('Nice, no error!')
    finally:
      print('That was: %s' % z)
  else:
    print('\nNice, no errors!')
    return 0
  print('Derp!')
  return 1


if __name__ == '__main__':
  sys.exit(main(*sys.argv))


```

Running the above code will produce the following output:

```console

Testing ComplexNumber
ComplexNumber: z0 = ComplexNumber(0.0, 0.0)
Nice, no error!
That was: 0.000 + 0.000J
 --- 
ComplexNumber: z1 = ComplexNumber(69.0, 420.0)
Nice, no error!
That was: 69.000 + 420.000J
 --- 
ComplexNumber: z2 = ComplexNumber(0.1337, 80085.0)
Nice, no error!
That was: 0.134 + 80085.000J
 --- 
ComplexNumber: z3 = ComplexNumber(69.0, 420.0)
Nice, no error!
That was: 69.000 + 420.000J
 --- 
ComplexNumber: z4 = ComplexNumber(69.0, 420.0)
Nice, no error!
That was: 69.000 + 420.000J
 --- 
ComplexNumber: z5 = ComplexNumber(1337.0, 420.0)
Nice, no error!
That was: 1337.000 + 420.000J

Nice, no errors!
```

The above code illustrates the use of the most important features of
**worktoy**. For more details, the docstrings of the individual
components should be consulted.
