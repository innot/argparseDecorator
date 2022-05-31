Limitations
===========

While the :class:`~argparsedecorator.argparse_decorator.ArgParseDecorator` tries to make as much functionallity of
the argparse_ library available in a decorator there are some limitations.

Some options of argparse_ could not be implemented in an elegant way using annotations.
However, if these options are really required they can still be used by using the
:meth:`~argparsedecorator.argparse_decorator.ArgParseDecorator.add_argument` decorator
instead of using annotations.

#. Using the `dest <https://docs.python.org/3/library/argparse.html#dest>` option

    `dest` changes the name of an argument to some other internal value. Using Annotations the `dest` of an
    argument must always be the default, that is the name of the annotated variable,
    otherwise the mapping of the return values from
    `ArgumentParser.parse_args <https://docs.python.org/3/library/argparse.html#the-parse-args-method>`_
    to the variable names of the decorated python command function will get messed up.
    Therefore the 'dest' argument option is not supported by the *ArgParseDecorator* library.

    This affects the following other option, which only work by setting `dest` and are therefore also not
    directly supported as annotations:

    * `append_const <https://docs.python.org/3/library/argparse.html#action>`_ actions.

#. Action classes

    Action classes can be used for highly customized validation and processing of the argument values. However



.. _argparse: https://docs.python.org/3/library/argparse.html