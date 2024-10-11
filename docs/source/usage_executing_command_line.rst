
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

