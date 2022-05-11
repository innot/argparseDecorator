Using the argparseDecorator
===========================

Install
-------

.. note::
    argparseDecorator has not yet been uploaded to Pypi. Install by downloading from github instead.


Once argparseDecorator has been installed it can be used like this.

Importing argparseDecorator
---------------------------

First, if you are using a python version previous to 3.10 it is a good idea to first add

.. code:: python

    from __future__ import annotations

to your file. This ensures that the annotations used by the argparseDecorator are handled as strings
and not as Python Types. This is not only faster, but some (mis)uses of annotations by the decorator
do not cause errors.

Next the argparseDecorator is imported. The best way is to

.. code:: python

    from argparseDecorator import *

to import all required types, including the annotation objects. Take a look at the
`__init__.py <https://github.com/innot/argparseDecorator/blob/master/argparsedecorator/__init__.py>`_ file to
see which names are pulled into the namespace

Simple example
--------------

Now the decorator can be instantiated and its command decorator can be used to mark a function as a command.
In this short example the command ``reverse``, which takes a single argument ``word`` is defined.

.. code:: python

    parser = ArgParseDecorator()

    @parser.command
    def reverse(word):
         print(word[::-1])


With this a command can be executed like this

.. code:: python

    parser.execute("reverse foobar")

    raboof

The ArgParseDecorator class
---------------------------

To use the argparseDecorator an instance of the ArgParseDecorator class has to be created.

The two main methods of the ArgParseDecorator class are :meth:'ArgParseDecorator.command' and
:meth:'ArgParseDecorator.execute'.

Command is a Decorator that can mark any function or method as a command. There can be any number
of decorated functions.

Any such decorated function is called by ``execute(cmdstring)`` when the `cmdstring` contains the command.




Subcommands
+++++++++++

Sometimes it makes sense to split commands into multiple subcommands. This is supported by the
argparseDecorator. To define a subcommand just add an underscore between the main command
and the subcommand in the function name.

For example the commands to switch an LED on or off could be implemented like this

.. code-block:: python

    @parser.command
    def led_on():
        ...

    @parser.command
    def led_off():
        ...

With this the argparseDecorator now understands the two commands ``led on`` and ``led off`` and the respective
functions are called.

.. code-block:: python

    parser.execute("led on")

Commands with Hyphens
+++++++++++++++++++++

To create a command containing a hypen `-`, e.g. ``get-info ...`` a double underscore is used in the command name, e.g.

.. code-block:: python

    @parser.command
    def get__info():
        ...

    parser.execute("get-info")




Fuction Signature
-----------------

argparseDecorator makes heavy use of type_annotations_ to pass additional information to the ArgumentParser.
This includes a number of custom Types which are used to provide additional information about the arguments.

For example the following
command will add up a list of numbers or, if `--squared` is added to the command,
will calculate the sum of the squares.

.. code:: python

    @parser.command
    def add(values: OneOrMore[float], squared: Option = False) -> None:
        if squared:
            values = [x*x for x in values]
        print sum(values)


``OneOrMore[float]`` tells the decorator, that ``values`` must have at least one value and
that it is accepting only valid numbers (int or float). ``Option = False`` marks ``squared``
as an option (starting with ``--``) and that it has the the value `True` if set on the
command line (overriding the default) or `False` (the default) otherwise.

The ``add`` command can now be used like this

.. code:: python

    parser.execute("add 1 2 3 4")

    10

    parser.execute("add --squared 1 2 3 4")

    30

Take a look at the Annotations_ API for all supported annotations and more examples.

.. _Annotations: https://argparseDecorator.readthdocs.io/.

Flags and Options
-----------------

The argparse library only destinguishes between position arguments and flags. Flags are
all arguments starting with either a single or a double hyphen '-'.

As python identifiers must not start with a hyphen there must be a way to tell the argparseDecorator
that the argument of a command is a flag.

This is done with the 'Flag' and 'Option' annotations. The 'Flag' tells the the decorator to internally
add a single '-' to the argument. 'Option' does the same, but with a double hyphen '--'

The argparseDecorator also uses the docstring_ of a decorated function to get a description
of the command that is used for help and some additional meta information about arguments
that can not be easily written as annotations.

Docstring
---------

argparseDecorator uses the docstring of a decorated function for description of the command and its arguments,
as well as some additional data that can not be set via the signature and its annotations.

Command Description
+++++++++++++++++++

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
+++++++++++++

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
      bar   Which bar to foo

If the help for an argument starts with ``SUPPRESS``, then this argument is hidden in the help. This might
be usefull to hide some unofficial options used for example for debugging.

Aliases
+++++++

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

    While the argname given to ``:alias`` will work with or without leading hyphens, the actual alias(es) must have
    either one or two leading hyphens.

Choices
+++++++

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
+++++++

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
.. _type_annotations: https://docs.python.org/3/library/typing.html
.. _docstring: https://peps.python.org/pep-0257/
