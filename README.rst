About
=====

argparseDecorator is a tool to ease working with the
argparse_ library to build custom command line interpreters.

Instead of setting up the 'ArgumentParser' object by hand and then adding
all the required arguments the argparseDecorator supplies a custom decorator_
to mark any function as a command and to generate the ArgumentParser arguments
from the function signature.

Here is a simple example of a command that reverses the input:

..code:: python

    >>> from argparsedecorator import *
    >>> parser = ArgParseDecorator()

    >>> @parser.command
    ... def reverse(word):
    ...     print(word[::-1])


With this a command can be executed like this

..code:: python

    >>> parser.execute("reverse foobar")
    raboof



.. _argparse: https://docs.python.org/3/library/argparse.html
.. _decorator: https://docs.python.org/3/glossary.html#term-decorator