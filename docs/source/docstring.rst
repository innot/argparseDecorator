Using the Docstring
===================

*argparseDecorator* uses the docstring of a decorated function for description of the command and its arguments,
as well as some additional data that can not be set via the signature and its annotations.

Command Description
-------------------

If a decorated function has a docstring its content is used as the help text for the command:

.. code-block:: python

    @parser.command
    def foo(bar):
        """The foo command will foo a bar."""
        ...

    parser.execute("help foo")


will create the output:

.. code:: console

    usage:  foo bar

    The foo command will foo a bar.

    positional arguments:
      bar


Argument Help
-------------

The docstring can be used add small help strings to arguments. For this a line in the format

.. code::

    :param argname: short description

is added to the docstring. Example:

.. code-block:: python

    @parser.command
    def foo(bar):
        """
        The foo command will foo a bar.
        :param bar: Which bar to foo"""
        ...

    parser.execute("help foo")

will generate:

.. code:: console

    ...
    positional arguments:
      bar  Which bar to foo

If the help for an argument starts with ``SUPPRESS``, then this argument is hidden in the help. This might
be usefull to hide some unofficial options used for example for debugging.

Aliases
-------

ArgumentParser allows for flags (arguments starting with ``-`` or ``--``) to have multiple names, e.g.
``--flag`` and ``-f``. To support multiple names for the same argument the ``:alias`` directive can be used
in the docstring. It has the format

.. code::

    :alias argname: -f, --foo

Here is an example on how this can be used:

.. code-block:: python

    @parser.command
    def foobar(flag: Option = True):
        """
        :alias flag: -f
        """
        print(flag)

    parser.execute("foobar --flag")
    parser.execute("foobar -f")

the last two lines are identical and will print ``True``.

.. note::

    While the argname given to ``:alias`` will work with or without leading hypens, the actual alias(es) must have
    either one or two leading hypens.

Choices
-------

ArgParseDecorator supports the ``Choices[]`` annotation in the signature to restrict the value of an argument
to a list of predefined values. As the syntax somewhat ugly for a list of strings (they have to be encapsuled
in a ``Literal[]`` annotation to keep type checkers happy) there is an alternative using a docstring with the format:

.. code::

    :choices argname: opt1, opt2, ...

Example:

.. code-block:: python

    @parser.command
    def foobar(value):
        """
        Only allow values foo, bar, 1 or 2
        :choices value: 'foo', 'bar', 1, 2
        """
        print(flag)

    parser.execute("foobar foo")
    parser.execute("foobar 2")
    parser.execute("foobar baz")    # this will raise an Exception

.. note::
    The list of choices is parsed using the python eval_ function.
    It can be anything that returns a sequence of items, e.g. ``range(1,4)`` would be a valid value for choices.

Metavar
-------

When ArgumentParser generates help messages, it needs some way to refer to each expected argument.
By default, ArgumentParser objects use name of the argument as the "name" of each object.
By default, for positional argument actions, the dest value is used directly, and for
optional argument actions, the dest value is uppercased. For example

.. code-block:: python

    def foobar(datetime: Option | Exactly2[str]):

will have a help output of

.. code-block:: console

    usage:  foobar [--datetime DATETIME DATETIME]
    optional arguments:
      --datetime DATETIME DATETIME

which does look ugly and is not as descriptive. Here the ``:metavar`` directive can be used to assign more
descriptive names to the arguments of ``--datetime``, e.g.:

.. code-block:: python

    def foobar(datetime: Option | Exactly2[str]):
        """
        :metavar datetime: DATE, TIME

will have a help output of

.. code-block:: console

    usage:  foobar [--datetime DATE TIME]
    optional arguments:
      --datetime DATE TIME

.. note::
    The number of metavar names must match the number of parameters an argument takes.


.. _eval: https://docs.python.org/3/library/functions.html#eval