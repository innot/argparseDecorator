
Function Signature
------------------

argparseDecorator makes heavy use of `type annotaions <https://docs.python.org/3/library/typing.html>`_
to pass additional information to the ArgumentParser. This includes a number of custom types which are used to
provide additional information about the arguments.

For example the following
command will add up a list of numbers or, if ``--squared`` is added to the command,
will calculate the sum of the squares.

.. code:: python

    @cli.command
    def add(values: OneOrMore[float], squared: Option = False) -> None:
        if squared:
            values = [x*x for x in values]
        print sum(values)


:py:`OneOrMore[float]` tells the decorator, that ``values`` must have at least one value and
that it is accepting only valid numbers (int or float). :py:`Option = False` marks ``squared``
as an option (starting with ``--``) and that it has the the value :py:`True` if set on the
command line (overriding the default) or :py:`False` (the default) otherwise.

The ``add`` command can now be used like this

.. code:: python

    cli.execute("add 1 2 3 4")

    10

    cli.execute("add --squared 1 2 3 4")

    30

Take a look at the :mod:`~argparsedecorator.annotations` API for all supported annotations and more examples.


Flags and Options
+++++++++++++++++

The argparse library only destinguishes between position arguments and flags. Flags are
all arguments starting with either a single or a double hyphen ``-``.

As python identifiers must not start with a hyphen there must be a way to tell the argparseDecorator
that the argument of a command is a flag.

This is done with the ``Flag`` and ``Option`` annotations. The ``Flag`` tells the the decorator
to internally add a single ``-`` to the argument. ``Option`` does the same, but with a double hyphen ``--``.

If an ``Flag`` or ``Option`` should have multiple names, e.g. a long Option name like ``--foobar`` and a short
``Flag`` name like ``-f`` an ``:alias --foobar: -f`` must be added to the docstring of the command function.
See :ref:`Aliases` below for details.

Normally a ``Flag`` or ``Option`` is optional, i.e. it may be left out of the command line.
In case there is a need to require the presence of the Flag/Option on the command line the
``RequiredFlag`` or ``RequiredOption`` annotations can be used instead to enforce the presence of
the Flag/Option on the command line.
Depending on the :ref:`Error Hander <Error Handling>` a missing, required Flag/Option will either generate
an error message on ``sys.stderr`` (default) or
raise an `ArgumentError <https://docs.python.org/3/library/argparse.html#exceptions>`_ (``errorhandler=None``)


Argument Type
+++++++++++++

The :external:class:`argparse.ArgumentParser` reads command-line arguments as simple strings. However it is often
usefull to interpret the input as another type, such as :external:class:`int` or :external:class:`float`.

This can be done by just annotating the argument with the required type in the normal Python fashion:

.. code-block:: python

    @cli.command
    def add(value1: float, value2: float):
        print(value1 + value2)

    @cli.execute("add 1 2.5")   # output "3.5"
    @cli.execute("add apple banana) # causes ValueError

Some of the special annotations of argparseDecorator can also specify the type in brackets to make the code more
readable:

.. code-block:: python

    @cli.command
    def sum(values: OneOrMore[float]):
        print(sum(values)

is almost equivalent to

.. code-block:: python

    @cli.command
    def sum(values: float | OneOrMore):
        print(sum(values)

but it is nicer to read and it also tells any type-checker that ``values`` is a :external:class:`~typing.List`
of *floats* and not a union of a *float* and a generic *List*.

Internally, when analyzing the annotations, the *argparseDecorator* will take anything that is not one of the built-in
:mod:`.annotations`, call :external:func:`eval` on it and uses the result as the type.

Take a look at the `argparse <https://docs.python.org/3/library/argparse.html#type>`_ documentation for more info
what types are possible and how to implement custom types.

Number of Values
++++++++++++++++

:mod:`.annotations` has a number of Annotation Types to tell the *ArgParseDecorator* (and the
*arparse.ArgumentParser*) how many values a command argument expects.
If nothing is specified a single value is expected for the argument.

These annotations are supported:

    * :class:`~.annotations.Exactly1` up to :class:`~.annotations.Exactly9`
    * :class:`~.annotations.ZeroOrOne`
    * :class:`~.annotations.ZeroOrMore`
    * :class:`~.annotations.OneOrMore`

add_argument Decorator
++++++++++++++++++++++

While its use is usually not required there might be some situations where
the function signature and its annotations are not sufficient to accurately
describe an argument. In this case the :meth:`~.argparse_decorator.ArgParseDecorator.add_argument` decorator can be used.
Any parameter to this decorator is passed directly to the
:external:meth:`~argparse.ArgumentParser.add_argument` method of the underlying *ArgumentParser*

The decorated function must have an argument of the same name and in the same order or use
:code:`*args` and :code:`**kwargs` arguments to retrieve the value of these arguments.

.. code-block:: python

    @cli.command
    @cli.add_argument('sourcefile', type=argparse.FileType('r', encoding='latin-1'))
    @cli.add_argument('--flag', '-f')
    def read(sourcefile, flag):
        ...

    def read(*args, **kwargs):
        sourcefile = args[0]
        flag = kwargs['flag']


.. warning::
    When using add_argument the order of the arguments is important. Unless using the
    ``*args/**kwargs`` style, the arguments of the function must be in the same order as the
    ``@cli.add_argument`` decorators **and** Flags and Options **must** be after any positional arguments.
    This is due to the fact, that Flags and Options are passed as keyword arguments to the function.

.. note::
    While it is possible to combine the *add_argument* decorator with annotations this should be used carefully
    to not cause ambiguities. While *argparseDecorator* will usually catch contradictory inputs and raise an
    Exception this is not guaranteed as not all possible combinations are tested.

When using some Callable as the type via ``add_argument``, you may want to annotated the function argument with
the type returned by the Callable to make a type checkers happy. By default this would cause a
:external:class:`TypeError` due to the mismatch in types.

In this case the :code:`ignore_annotations` flag can be set in the @command decorator to tell
*argparseDecorator* to disregard all annotations in the function signature.

.. code-block:: python

    @cli.command(ignore_annotations=True)
    @cli.add_argument('--flag', type=argparse.FileType('r', encoding='latin-1'))
    def read(flag: typing.TextIOWrapper):
        ...

