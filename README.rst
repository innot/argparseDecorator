About
=====

.. warning::
    this program is not finished. It was uploaded to GitHub as a backup.
    It is not yet feature complete and some parts may or may not work.

argparseDecorator is a tool to ease working with the
argparse_ library to build custom command line interpreters.

Instead of setting up the 'ArgumentParser' object by hand and then adding
all the required arguments the argparseDecorator supplies a custom decorator_
to mark any function as a command and to generate the ArgumentParser
from the function signature.

Here is a simple example of a command that reverses the input:

.. code:: python

    >>> from argparsedecorator import *
    >>> parser = ArgParseDecorator()

    >>> @parser.command
    ... def reverse(word):
    ...     print(word[::-1])


With this a command can be executed like this

.. code:: python

    >>> parser.execute("reverse foobar")
    raboof


argparseDecorator makes heavy use (and propably misuse) of type_annotations_ to
pass additional information to the ArgumentParser. For example the following
command will add up a list of numbers or, if '--squared' is added to the command,
will calculate the sum of the squares.

.. code:: python

    @parser.command
    def add(values: OneOrMore[float], squared: Option = True) -> None:
        if squared:
            values = [x*x for x in values]
        print sum(values)


'OneOrMore[float]' tells the decorator, that 'values' must have at least one value and
that it is accepting only valid numbers (int or float). 'Option = True' marks 'squared'
as an option (starting with '--') and that it has the the value 'True' if set on the
command line or 'False' otherwise.

The 'add' command can now be used like this

.. code:: python

    >>> parser.execute("add 1 2 3 4")
    10

    >>> parser.execute("add --squared 1 2 3 4")
    30

Take a look at the Annotations_ API for all supported annotations and more examples.

.. _Annotations: https://argparseDecorator.readthdocs.io/.

The argparseDecorator also uses the docstring_ of a decorated function to get a description
of the command that is used for help and some additional meta information about arguments
that can not be easily written as annotations.

.. code:: python

    @parser.command
    def add(values: OneOrMore[float], squared: Option = True) -> None:
        """
        Add up a list of numbers.
        :param values: one or more numbers
        :param squared: when present square each number first
        :alias squared: -sq
        """
        if squared:
            values = [x*x for x in values]
        print sum(values)


Now the help command, which is supplied by the argparseDecorator, can output some
information

.. code:: python
    >>> parser.execute("help add")
    usage:  add [--squared] values [values ...]

    Add up a list of numbers.

    positional arguments:
      values          one or more numbers

    optional arguments:
      --squared, -sq  when present square each number first

See the Docstring_ API for more details and examples.

Requirements
============
* Works best with Python 3.10 or higher
    - the new type unions with '|' make the annotations múch more readable
* Works with Python 3.7+
    - some features require the use of 'from __future__ import annotations'
* No other dependencies

Installation
============
{TODO} If the requirements are met, then a simple

.. code:: bash

    $ pip import argparseDecorator

will install the argParseDecorator module.

Documentation
=============
Comprehensive documentation is available at https://argparseDecorator.readthedocs.io/.


.. _argparse: https://docs.python.org/3/library/argparse.html
.. _decorator: https://docs.python.org/3/glossary.html#term-decorator
.. _type_annotations: https://docs.python.org/3/library/typing.html
.. _docstring: https://peps.python.org/pep-0257/
