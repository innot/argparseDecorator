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

Here is an example for using ArgParseDecorator to create a hypothetical 'ls' command:

.. code-block:: python

    from __future__ import annotations      # required for Python 3.7 - 3.9. Not required for Python 3.10+
    from argparsedecorator import *         # import the ArgParseDecorator API

    parser = ArgParseDecorator()

    @parser.command
    def ls(
           files: ZeroOrMore[str],
           a: Flag = False,  # create '-a' flag that is 'False' if '-a' is not in the command line.
           ignore: Option | Exactly1[str] = "",  # create optional '--ignore PATTERN' argument
           columns: Option | int | Choices[Literal["range(1,5)"]] = 1,  # valid input for '--columns' is 1 to 4
           sort: Option | Choices[Literal["fwd", "rev"]] = "fwd",  # '--sort {fwd,rev}' with default 'fwd'
           ):
        """
        List information about files (the current directory by default).
        :param files: List of files, may be empty.

        :param a: do not ignore entries strating with '.'
        :alias a: --all

        :param ignore: do not list entries matching PATTERN
        :metavar ignore: PATTERN

        :param columns: number of output columns, must be between 1 and 4. Default is 1
        :alias columns: -c

        :param sort: alphabetic direction of output, either 'fwd' (default) or 'rev'
        :alias sort: -s
        """
        # for demonstration just return all input back to the caller, i.e. parser.execute(...)
        return {"files": files, "a": a, "ignore": ignore, "columns": columns, "sort": sort}

This example shows how annotations are used to add some metadata to the arguments which will be used by
the argparse library to interpret the command line input.
Take a look at the documentation_ to learn more about the supported annotations.

Now a command line can be parsed and executed like this:

.. code-block:: python

        result = parser.execute("ls -a -c 2 --sort rev --ignore *.log")

ArgParseDecorator uses the docstring of the decorated function to get a help string for the command
and it also parses Sphinx_ style directives to provide help strings for arguments as well as additional
metadata that can not be written as annotations.

The information provided by the docstring is used by the built-in help command:

.. code:: python

    parser.execute("help ls")

.. code:: output

    usage:  ls [-a] [--ignore PATTERN] [--columns {1,2,3,4}] [--sort {fwd,rev}] [files ...]

    List information about files (the current directory by default).

    positional arguments:
      files                 List of files, may be empty.

    options:
      -a, --all             do not ignore entries strating with '.'
      --ignore PATTERN      do not list entries matching PATTERN
      --columns {1,2,3,4}, -c {1,2,3,4}
                            number of output columns, must be between 1 and 4
      --sort {fwd,rev}, -s {fwd,rev}
                            alphabetic direction of output, either 'fwd' (default) or 'rev'


Requirements
============
* Works best with Python 3.10 or higher
    - the new type unions with '|' make the annotations much more readable
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

.. _documentation: https://argparsedecorator.readthedocs.io/en/latest/
.. _argparse: https://docs.python.org/3/library/argparse.html
.. _decorator: https://docs.python.org/3/glossary.html#term-decorator
.. _type_annotations: https://docs.python.org/3/library/typing.html
.. _docstring: https://peps.python.org/pep-0257/
.. _Sphinx: https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html