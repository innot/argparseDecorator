
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

.. _class variable: https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables
