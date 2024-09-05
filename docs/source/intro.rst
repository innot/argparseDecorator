Introduction
============

argparseDecorator is a tool to ease working with the Python :external:mod:`argparse`
library to build custom command line interpreters.

Instead of setting up the :external:class:`~argparse.ArgumentParser` object by hand and then adding
all the required arguments the argparseDecorator supplies a custom decorator_
to mark functions as a command and to generate the ArgumentParser
from the function signature.

Here is a simple example of a command that reverses the input:

.. code-block:: python

    >>> from argparsedecorator import *
    >>> cli = ArgParseDecorator()

    >>> @cli.command
    ... def reverse(word):
    ...     print(word[::-1])


With this a command can be executed like this

.. code:: python

    >>> cli.execute("reverse foobar")
    raboof


argparseDecorator makes heavy use (and propably misuse) of
`type annotations <https://docs.python.org/3/library/typing.html>`_ to
pass additional information to the ArgumentParser. For example the following
command will add up a list of numbers or, if ``--squared`` is added to the command,
will calculate the sum of the squares.

.. code-block:: python

    @cli.command
    def add(values: OneOrMore[float], squared: Option = False) -> None:
        if squared:
            values = [x*x for x in values]
        print sum(values)


':class:`.annotations.OneOrMore` [float]' tells the decorator, that ``values`` must have at least one value and
that it is accepting only valid numbers (``int`` or ``float``).

``Option = False`` marks ``squared`` as an option (starting with ``--``) and that it has
the the value ``True`` if set on the command line or ``False`` (the default) otherwise.

The ``add`` command can now be used like this

.. code:: python

    >>> cli.execute("add 1 2 3 4")
    10

    >>> cli.execute("add --squared 1 2 3 4")
    30

Take a look at the :mod:`.annotations` API for all supported annotations and more examples.

The argparseDecorator also uses the docstring_ of a decorated function to get a description
of the command that is used for help and some additional meta information about arguments
that can not be easily written as annotations.

.. code-block:: python

    @cli.command
    def add(values: OneOrMore[float], squared: Option = False) -> None:
        """
        Add up a list of numbers.
        :param values: one or more numbers
        :param squared: when present square each number first
        :alias squared: -sq
        """
        if squared:
            values = [x*x for x in values]
        print sum(values)


Now the help command, which is supplied by the argparseDecorator, will output the following information:

.. code:: python

    >>> cli.execute("help add")
    usage:  add [--squared] values [values ...]

    Add up a list of numbers.

    positional arguments:
      values          one or more numbers

    optional arguments:
      --squared, -sq  when present square each number first

See :ref:`Using the argparseDecorator` for more details and examples.

Version history
+++++++++++++++
1.3.0
    - Added support for command aliases

1.2.0
    - Added support for sys.argv argument lists in execute()
    - Using shlex to split commandlines into tokens.
    - Numerous minor bug fixes

1.1.0
    - Added support for execute_async()

1.0.2
    - Added support for quoted input to the execute method

1.0.1
    - first release

.. _argparse: https://docs.python.org/3/library/argparse.html
.. _decorator: https://docs.python.org/3/glossary.html#term-decorator
.. _docstring: https://peps.python.org/pep-0257/
