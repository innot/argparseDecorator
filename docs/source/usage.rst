Using the argparseDecorator
===========================

.. role:: py(code)
    :language: python

Install
-------

The easiest way to install argparseDecorator is with pip:

.. code-block:: console

    $ pip import argparseDecorator

Alternativly the sources can be downloaded directly from the
`Github <https://github.com/innot/argparseDecorator>`_ page.


Once argparseDecorator has been installed it can be used like this.

Importing argparseDecorator
---------------------------

First, if you are using a python version previous to 3.10 it is a good idea to add

.. code-block:: python

    from __future__ import annotations

at the top of your file. This ensures that the annotations used by the argparseDecorator are handled as
strings and not as Python Types. This is not only faster, but some uses of annotations by the decorator
will cause errors otherwise.

Next the argparseDecorator is imported. The best way is to

.. code-block:: python

    from argparsedecorator import *

to import all required types, including the annotation objects. Take a look at the
`__init__.py <https://github.com/innot/argparseDecorator/blob/master/argparsedecorator/__init__.py>`_ file to
see which names are pulled into the namespace

Simple example
--------------

Now the decorator can be instantiated and its command decorator can be used to mark a function as a command.
In this short example the command ``reverse`` is created, which takes a single argument named ``word``:

.. code-block:: python

    cli = ArgParseDecorator()

    @cli.command
    def reverse(word):
         print(word[::-1])


With this a command can be executed like this:

.. code-block:: python

    cli.execute("reverse foobar")

    raboof


.. include:: usage_argparsedecorator_class.rst

.. include:: usage_function_signature.rst

.. include:: usage_docstring.rst

.. include:: usage_executing_command_line.rst

.. _docstring: https://peps.python.org/pep-0257/
.. _sys.stderr: https://docs.python.org/3/library/sys.html#sys.stderr
.. _sys.stdout: https://docs.python.org/3/library/sys.html#sys.stdout
.. _sys.stdin: https://docs.python.org/3/library/sys.html#sys.stdin
