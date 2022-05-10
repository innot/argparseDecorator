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

Using Annotations
-----------------

argparseDecorator makes heavy use (and propably misuse) of type_annotations_ to
pass additional information to the ArgumentParser. For example the following
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

.. code:: python

    @parser.command
    def add(values: OneOrMore[float], squared: Option = True) -> None:
        """
        Add up a list of numbers.
        :param values: one or more numbers
        :param squared: when present square each number first
        :alias squared: -s
        """
        if squared:
            values = [x*x for x in values]
        print sum(values)


Now the help command, which is supplied by the argparseDecorator, can output some
information

.. code:: output

    parser.execute("help add")

    usage:  add [--squared] values [values ...]

    Add up a list of numbers.

    positional arguments:
      values          one or more numbers

    optional arguments:
      --squared, -s   when present square each number first

See the Docstring_ API for more details and examples.


.. _type_annotations: https://docs.python.org/3/library/typing.html
.. _docstring: https://peps.python.org/pep-0257/
