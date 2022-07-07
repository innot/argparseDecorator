Limitations
===========

While the :class:`~argparsedecorator.argparse_decorator.ArgParseDecorator` tries to make as much functionality of
the argparse_ library available as possible in a decorator, there are some limitations.

Some options of argparse_ could not be implemented in an elegant way using annotations.
However, if these options are really required they can still be used by using the
:meth:`~argparsedecorator.argparse_decorator.ArgParseDecorator.add_argument` decorator
instead of using annotations.

Other options that are not supported are:

#. Using the `dest <https://docs.python.org/3/library/argparse.html#dest>`_ option

    :code:`dest` changes the name of an argument to some other internal value. Using Annotations the :code:`dest`
    of an argument must always be the default, that is the name of the annotated variable,
    otherwise the mapping of the return values from
    `ArgumentParser.parse_args <https://docs.python.org/3/library/argparse.html#the-parse-args-method>`_
    to the variable names of the decorated python command function will get messed up.
    Therefore the :code:`dest` argument option is not supported by the *ArgParseDecorator* library.

    This affects the following other option, which only work by setting :code:`dest` and is therefore also not
    directly supported as annotations:

    * `append_const <https://docs.python.org/3/library/argparse.html#action>`_ actions.

#. `Argument grouping <https://docs.python.org/3/library/argparse.html#argument-groups>`_

    Grouping of arguments is currently not supported but could possibly be added with a
    docstring option if there is `demand <https://github.com/innot/argparseDecorator/issues>`_ for it.

#. `Mutual exclusion <https://docs.python.org/3/library/argparse.html#mutual-exclusion>`_

    Like the similar argument groups this is not supported yet, but could be if someone needs it.

#. `Partial parsing <https://docs.python.org/3/library/argparse.html#partial-parsing>`_

    Not supported and probably not required.

#. Some options of the `ArgumentParser <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_ class

    The following options should not be used:

    * `prog <https://docs.python.org/3/library/argparse.html#prog>`_: this adds the given program name to
      the help of every command which is probably not very helpful

    * `parents <https://docs.python.org/3/library/argparse.html#parents>`_: *ArgParseDecorator* manages only a
      single command tree and would not know how to call commands functions from other *ArgumentParsers*

    * `prefix_chars <https://docs.python.org/3/library/argparse.html#prefix-chars>`_: Use of :code:`-` and :code:`--` to
      mark :class:`~.annotations.Flag` and :class:`~.annotations.Option`
      is hardwired into the ArgParseDecorator logic and can not be easily changed.

    * `add_help <https://docs.python.org/3/library/argparse.html#add-help>`_: *ArgParseDecorator* has its own
      :ref:`help` system and manages this option itself.

.. _argparse: https://docs.python.org/3/library/argparse.html