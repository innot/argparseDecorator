Using the Docstring
===================

*argparseDecorator* uses the docstring of a decorated function for description of the command and its arguments,
as well as some additional data that can not be set via the signature and its annotations.

Command Description
-------------------

If a decorated function has a docstring its content is used as the help text for the command:

.. code:: python

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

The docstring can be used add small help strings to arguments. For this
