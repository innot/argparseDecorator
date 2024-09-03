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

The ArgParseDecorator class
---------------------------

To use the argparseDecorator an instance of the :class:`~.argparse_decorator.ArgParseDecorator`
class has to be created.

.. code-block:: python

    cli = ArgParseDecorator()


The two main methods of the *ArgParseDecorator* class are
:meth:`~.argparse_decorator.ArgParseDecorator.command` and
:meth:`~.argparse_decorator.ArgParseDecorator.execute`.

:meth:`~.argparse_decorator.ArgParseDecorator.command` is a Decorator that can mark any function
or method as a command. There can be any number of decorated functions.

.. code-block:: python

    @cli.command
    def foobar(word):
         ...

Any such decorated function is called by :py:`execute(cmdstring)` when the ``cmdstring`` contains the command.

.. note::

    The ``command`` decorator can be used with or without parenthesis.

Arguments
+++++++++

Take a look at the :class:`~argparsedecorator.argparse_decorator.ArgParseDecorator` API to see what optional
arguments can be given when instantiating the class.

Note that any keyword argument that *ArgParseDecorator* does not handle itself
will be passed onto the the underlying :external:class:`argparse.ArgumentParser` class. Some options like
`formatter_class <https://docs.python.org/3/library/argparse.html#formatter-class>`_ or
`allow_abbrev <https://docs.python.org/3/library/argparse.html#allow-abbrev>`_ might be useful in some cases.

However some options of :external:class:`argparse.ArgumentParser` are not useful and should not be used.
Take a look at the :ref:`Limitations` chapter for more info on which options should be avoided.

Help
++++

By default :external:class:`argparse.ArgumentParser` adds a
`-h/--help <https://docs.python.org/3/library/argparse.html#add-help>`_ argument to every command.
This is somewhat ugly for a CLI with many commands and every one having the same, obvious help argument.

Instead the *ArgParseDecorator* by default adds a ``help`` command to the CLI which will provide a list of all
supported commands when called by itself or a detailed command description when supplied with a command name argument.

To override this behaviour and instead use the ``-h/--help`` system of *ArgumentParser* set :py:`helpoption="-h"`
when instantiating the *ArgParseDecorator*

.. code-block:: python

    cli = ArgParseDecorator(helpoption="-h")

If no help is wanted set ``helpoption`` to :py:`None`

.. code-block:: python

    cli = ArgParseDecorator(helpoption=None)

Command Aliases
+++++++++++++++

If needed a command can be assigned one or more aliases. These can easily be added via the decorator:

.. code-block:: python

    @cli.command(aliases=["co"])
    def checkout():
        ...

In this example the short ``co`` can be used instead the more verbose ``checkout`` command.
When using ``help`` aliases are shown in parenthesis.


Subcommands
+++++++++++

Sometimes it makes sense to split commands into multiple subcommands. This is supported by the
argparseDecorator. To define a subcommand just add an underscore between the main command
and the subcommand in the function name.

For example the commands to switch an LED on or off could be implemented like this

.. code-block:: python

    @cli.command
    def led_on():
        ...

    @cli.command
    def led_off():
        ...

With this the argparseDecorator now understands the two commands ``led on`` and ``led off`` and the respective
functions are called.

.. code-block:: python

    cli.execute("led on")

Commands with Hyphens
+++++++++++++++++++++

To create a command containing a hypen ``-``, e.g. ``get-info ...`` a double underscore is used
in the command name, e.g.

.. code-block:: python

    @cli.command
    def get__info():
        ...

    cli.execute("get-info")


Using ArgParseDecorator to Decorate Class Methods
+++++++++++++++++++++++++++++++++++++++++++++++++

When using this library to decorate methods within a class there is one caveat:

.. code-block:: python

    class MyCLI:

        cli = ArgParseDecorator()

        @cli.command
        def cmd(self, arg1, arg2, ...):
            ...

To mark methods as commands the *ArgParseDecorator* must be instantiated as a `class variable`_.
But as a class variable it does not have access to any data from a *MyCLI* instance, especially not to the
:py:`self` reference.

To correctly call the ``cmd`` function from :meth:`~.argparse_decorator.ArgParseDecorator.execute`
a reference to :py:`self` must be given, e.g. like this:

.. code-block:: python

    class MyCLI:

        cli = ArgParseDecorator()

        @cli.command
        def cmd(self, arg1, arg2, ...):
            ...

        def execute(self, cmdline):
            cli.execute(cmdline, self)

Note how :py:`cli.execute()` is wrapped in a method and how it passes a reference
to *self* to the *ArgParseDecorator*.

An alternative method would be the use of inner functions like this:

.. code-block:: python

    class MyCLI:

        def __init__(self):
            self.setup_cli()

        def setup_cli(self):

            cli = ArgParseDecorator()
            self.cli = cli              # store as instance variable

            @cli.command
            def cmd(arg1, arg2, ...)
                self.do_something_with(arg1)

        def execute(self, cmdline)
            self.cli.execute(cmdline)


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

If an *Flag* or *Option* should have multiple names, e.g. a long Option name like ``--foobar`` and a short
*Flag* name like ``-f`` an ``:alias --foobar: -f`` must be added to the docstring of the command function.
See :ref:`Aliases` below for details.

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

Docstring
---------

The argparseDecorator also uses the docstring_ of a decorated function to get a description
of the command that is used for help and some additional meta information about arguments
that can not be easily written as annotations.

argparseDecorator uses the docstring of a decorated function for description of the command and its arguments,
as well as some additional data that can not be set via the signature and its annotations.

Command Description
+++++++++++++++++++

If a decorated function has a docstring its content is used as the help text for the command:

.. code-block:: python

    @cli.command
    def foo(bar):
        """The foo command will foo a bar."""
        ...

    cli.execute("help foo")


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

    @cli.command
    def foo(bar):
        """
        The foo command will foo a bar.
        :param bar: Which bar to foo
        """
        ...

    cli.execute("help foo")

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

    :alias argname: -name1, --name2

Here is an example on how this can be used:

.. code-block:: python

    @cli.command
    def foobar(flag: Option = False):
        """
        :alias flag: -f
        """
        print(flag)

    cli.execute("foobar --flag")
    cli.execute("foobar -f")

the last two lines are identical and will print :py:`True`.

.. note::

    While the argname given to ``:alias`` will work with or without leading hyphens, the actual alias(es) must have
    either one or two leading hyphens.

Choices
+++++++

ArgParseDecorator supports the ``Choices[]`` annotation in the signature to restrict the value of an argument
to a list of predefined values. As the syntax somewhat ugly for a list of strings (they have to be encapsuled
in a ``Literal[]`` annotation to keep type checkers happy) there is an alternative using a docstring with
the format:

.. code::

    :choices argname: opt1, opt2, ...

Example:

.. code-block:: python

    @cli.command
    def foobar(value):
        """
        Only allow values foo, bar, 1 or 2
        :choices value: 'foo', 'bar', 1, 2
        """
        print(flag)

    cli.execute("foobar foo")
    cli.execute("foobar 2")
    cli.execute("foobar baz")    # this will raise an Exception

.. note::
    The list of choices is parsed using the python :external:func:`eval` function.
    It can be anything that returns a sequence of items, e.g. :py:`range(1,4)` would be a valid value for choices.

Metavar
+++++++

When ArgumentParser generates help messages, it needs some way to refer to each expected argument.
By default, ArgumentParser objects use name of the argument as the ``name`` of each object.
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


Executing a Command Line
------------------------

Once the :class:`~.argparse_decorator.ArgParseDecorator` has been set up with all decorated
functions or methods it can be used to execute arbitrary command lines.

This is done by calling the :meth:`~.argparse_decorator.ArgParseDecorator.execute` method
with a command line string. The command line can come directly from the prompt like in the example below, or it
could come for example from a ssh connection.

.. code-block:: python

    cli = ArgParseDecorator()

    ...

    cmdline = input()
    cli.execute(cmdline)


Internally the command line is first split into separate tokens using the :external:class:`~shlex.shlex` lexer
library (in POSIX mode). These tokens are then passed to the internal
:external:class:`argparse.ArgumentParser` instance and, if there are no errors, the command function
(the first word of the command line) is called with all arguments.

Execute Async Code
++++++++++++++++++

A typical use case for a command line interface is via a remote ssh connection. These are usually implemented
with :external:mod:`asyncio` code. *ArgParseDecorator* supports this with the
:meth:`~.argparse_decorator.ArgParseDecorator.execute_async` method which is functionally equivalent to
:meth:`~.argparse_decorator.ArgParseDecorator.execute`, but is implemented as a coroutine which can be awaited.

To make full use of this the command functions should be
`coroutines <https://docs.python.org/3/library/asyncio-task.html#coroutines>`_ as well. After parsing the given
command line input, :meth:`~.argparse_decorator.ArgParseDecorator.execute_async` will then
`await <https://docs.python.org/3/reference/expressions.html#await>`_ the command coroutine.

Here is a simple example for a sleep command that will pause the cli while other stuff could continue to run:

.. code-block:: python

    import asyncio

    from argparsedecorator import *

    cli = ArgParseDecorator()

    @cli.command
    async def sleep(n: float):
        await asyncio.sleep(n)

    async def runner():
        await cli.execute_async("sleep 1.5")

    if __name__ == "__main__":
        asyncio.run(runner())

Take a look at the `ssh_cli.py <https://github.com/innot/argparseDecorator/blob/master/examples/ssh_cli.py>`_ demo
for a more complex module using *argparseDecorator* in an asyncio application.

Using sys.argv as Input
+++++++++++++++++++++++

Instead of a single string the *execute* and *execute_async* methods can also take a list of strings (or any
string :external:class:`~collections.abc.Iterator`), where the first item is the name of the command and all following items
are the arguments.

This is useful if you - instead of implementing a full CLI - just want to parse the command line arguments of a Python
script. A Python script has all its arguments in the system parameter :external:data:`sys.argv` with
:code:`sys.argv[0]` containing the script name. This can be passed directly to *execute*/*execute_async* as the
commandline argument. For example, the following script will implement a :code:`--verbose` argument for the script:

.. code-block:: python

    # testverbose.py

    import sys
    from argparsedecorator import *

    # use helpoption='-h' as the default "help" option does not
    # work when parsing script arguments.
    argparser = ArgParseDecorator(helpoption="-h")

    @argparser.command
    def testverbose(v: Flag = False):  # must be the same name as the script.
        """
        Sample to show script argument parsing.
        :param v: switch on verbose mode.
        :alias v: --verbose
        """
        if v:
            print("chatty mode activated")


    if __name__ == "__main__":
        argparser.execute(sys.argv)


.. code-block:: sh
    :emphasize-lines: 1,4

    # python testverbose.py --verbose
    chatty mode activated

    # python testverbose.py --help
    usage:  testverbose [-h] [-v]

    Sample to show script argument parsing.

    options:
      -h, --help     show this help message and exit
      -v, --verbose  switch on verbose mode.

    Process finished with exit code 0


Using the name of the script as the name of the command function allows for the same script
to behave differently depending on the name of the script, e.g. by using differently named links to the same
Python script.


Using Quotes on the Command Line
++++++++++++++++++++++++++++++++

*ArgParseDecorator* uses the :external:class:`~shlex.shlex` lexer library (in POSIX mode) to split a given
commandline into seperate tokens for the command and the arguments. Arguments containing spaces can be encapsulated
in single or double quotemarks to prevent splitting them into seperate arguments.

However these quotemarks will be removed by *shlex*. If an argument requires quotes to be preserved they need to
be escaped by a backslash character :code:`\\`. If a backslash character is part of an argument it has to be escaped
as well like :code:`\\\\`

For example

.. code-block::

    cli.execute('cmd foo bar')          # -> Split into ['cmd', 'foo', 'bar']
    cli.execute('cmd "foo bar"')        # -> Split into ['cmd', 'foo bar']
    cli.execute('cmd "a \'quote\' "')   # -> Split into ['cmd', "a 'quote' "]
    cli.execute('cmd path\\to\\file')   # -> Split into ['cmd', 'path\to\file']

If this behaviour is not desired, e.g. when working with lots of Windows paths, then the caller can implement its
own lexer (e.g. *shlex* in the default non-POSIX mode) and pass its result to the *execute* method
(note: *shlex* implements the Iterator methods and can be passed to *execute* directly).

See `shlex parsing rules <https://docs.python.org/3/library/shlex.html#parsing-rules>`_ for more details on how
*shlex* works in the different modes.

Error Handling
++++++++++++++

If there is an error parsing the command line (e.g. invalid commands, illegal arguments etc.) an error message is
written to `sys.stderr`_.

If a more involved error handling is required, e.g. to translate the error messages or to
do some formatting on them, a special error handler function can be given to
:meth:`~.argparse_decorator.ArgParseDecorator.execute` that is called
whenever an error occurs.

The error handler function is called with one argument , an :py:`argparse.ArgumentError` exception object.
The string representation of the exception contains the full error message.

.. code-block:: python

    def my_error_handler(err: argparse.ArgumentError):
        print(str(err))     # output the error message to stdout instead of stderr

    cli = ArgParseDecorator()

    cli.execute("command", error_handler=my_error_handler)  # "command" does not exist causing an error message

The error_handler can be explicitly set to :py:`None`. In this case no error message is output but instead an
:py:`argparse.ArgumentError` is raised which can be caught and acted upon.

.. code-block:: python

    while True:
        try:
            cmdline = input()
            cli.execute(cmdline, error_handler=None)
        except ArgumentError as err:
            print(str(err))


Redirecting Output
++++++++++++++++++

When executing a command line all output (e.g. help messages) is written by default to the `sys.stdout`_ stream and
any error message (e.g. invalid syntax) is written to the `sys.stderr`_ stream. These are usually the
*stdout* and *stderr* streams of the shell from where python was started.

As the typical use case for a CLI implemented with *ArgParseDecorator* is some kind of remote connection, for example
a ssh server implementation, there must be a way to redirect the output of the *ArgumentParser* to the
remote connection.

This can be done by passing `TextIO <https://docs.python.org/3/library/io.html#text-i-o>`_ Streams for *stdout* and
*stderr* to the :meth:`~.argparse_decorator.ArgParseDecorator.execute` method.
This method will then redirect :py:`sys.stdout` and :py:`sys.sterr` to the given stream(s) before calling
:external:class:`argparse.ArgumentParser` and the command function. After the command has been called and before
returning to the caller :py:`sys.stdout` and :py:`sys.stderr` are restored to their original values.

.. code-block:: python

    cli = ArgParseDecorator()

    my_stdout = BufferedWriter()

    @cli.command
    def echo(text: str):
        print(text)

    cli.execute("echo foobar", stdout=my_stdout)
    print(stdout.getvalue())    # prints 'foobar'


Redirecting Input
+++++++++++++++++

If any commands require further user input, e.g. for confirmation checks, the
`sys.stdin`_ can also be redirected to a different stream:

.. code-block:: python

    cli = ArgParseDecorator()
    my_stdin = io.StringIO("yes")

    @cli.command
    def delete():
        print("type 'yes' to confirm that you want to delete everything")
        result = input()
        if result == "yes":
            print("you have chosen 'yes'")

    cli.execute("delete", stdin=my_stdin)   # will output "you have chosen 'yes'" immediatly


.. _docstring: https://peps.python.org/pep-0257/
.. _class variable: https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables
.. _sys.stderr: https://docs.python.org/3/library/sys.html#sys.stderr
.. _sys.stdout: https://docs.python.org/3/library/sys.html#sys.stdout
.. _sys.stdin: https://docs.python.org/3/library/sys.html#sys.stdin
