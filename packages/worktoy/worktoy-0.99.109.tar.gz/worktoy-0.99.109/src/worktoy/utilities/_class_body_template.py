"""
The ClassBodyTemplate provides a string template for the body of a class
body.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  pass

ClassBodyTemplate = """
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  
  #  Fallback Variables
  
  #  Private Variables
  
  #  Public Variables
  
  #  Virtual Variables

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  
    Method decorators in class bodies are certain to encounter function
    objects rather than bound methods, but this applies only to the
    immediately applied decorator. Decorators applied to already decorated
    methods receive instead the object return by the previous decorator.

    A typical decorator pattern is for the decorator to wrap the decorated
    function object at the '__wrapped__' attribute. Next, the decorator
    class should then implement '__call__' to forward the call to the
    wrapped method.

    An improvement of the above pattern is to emulate the bound method
    behaviour by implementing the descriptor protocol on the decorator
    class. This requires implementing '__get__' to return the wrapped
    function body directly, when the instance argument is 'None' and to
    return a wrapping function that already has the instance at the first
    argument position when the instance argument is not 'None'.

    The most elegant pattern however, is for the decorator to be
    instantiated on the class body separately from the decorated method.
    When decorating the method, the decorator should only record a
    reference to the method or even just the name of the method, before
    returning the decorator instance having applied no changes to it.
    Decorators following this pattern stacks without having to implement
    inelegant workarounds to handle the cases where they decorate another
    decorator.

    IDEA:
    Implement a namespace hooks that recognizes when a decorator is
    getting called and then to allow the hook to handle the control flow
    of applying the decorator!
"""
