# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file
# or go to <https://opensource.org/licenses/MIT>.

""" The Annotations for the argparseDecorator.

This module contains a number of classes that can be used as type annotations to give the
decorator more metadata used to describe the argument.

All annotation classes in this module do not contain any code and should not be instantiated.
Some annotation classes are generic types which can encapsulate an optional type, e.g.

.. code-block:: python

    def command(files: OneOrMore[str])

while other annotations are strictly used as markers and may not encapsulate other types.

.. code-block:: python

    def command(verbose: Option | StoreTrueAction)
"""
from typing import TypeVar, List, Generic

# Using custom classes instead of NewType is not very efficient,
# but it allows for Generic Types which can be used to add
# a type to the options, e.g. OneOrMore[int]


T = TypeVar('T')


class Flag:
    """
    Marks the argument as a Flag.

    A Flag starts with a single hyphen :code:`-`.

    If the Flag does not require any arguments (just present or not present) add a :code:`= False` as its
    default or add a :class:`StoreTrueAction` annotation.

    .. code-block::

        def cmd(f: Flag = False):
            return f

        result = parser.execute("cmd -f")  # result = True
        result = parser.execute("cmd")     # result = False  (the default)

    See `argparse: name-or-flags <https://docs.python.org/3/library/argparse.html#name-or-flags>`_
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class RequiredFlag:
    """
    Marks the argument as a Flag that must be supplied.

    A Flag starts with a single hyphen :code:`-`.

    .. note::
        While this is not enforced, required flags should have at least one argument.

    .. code-block::

        def cmd(f: RequiredFlag|OneOrMore[int]):
            return f

        result = parser.execute("cmd -f 100")  # result = [100]
        result = parser.execute("cmd")         # results in an Error

    See `argparse: required <https://docs.python.org/3/library/argparse.html#required>`_
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Option:
    """
    Marks the argument as an Option.

    An Option starts with a double hyphen :code:`--`.

    If the Option does not require any arguments (just present or not present) add a :code:`= False`
    as its default or add a :class:`StoreTrueAction` annotation.

    .. code-block::

        def cmd(foo: Option = False):
            return foo

        result = parser.execute("cmd --foo")    # result = True
        result = parser.execute("cmd")          # result = False  (the default)

    See `argparse: name-or-flags <https://docs.python.org/3/library/argparse.html#name-or-flags>`_
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class RequiredOption:
    """
    Marks the argument as an Option that must be supplied.

    An Option starts with a double hyphen :code:`--`.

    .. note::
        While this is not enforced, required options should have at least one argument.

    .. code-block::

        def cmd(foo: RequiredOption|OneOrMore[int]):
            return foo

        result = parser.execute("cmd --foo 100")    # result = [100]
        result = parser.execute("cmd")              # results in an Error

    See `argparse: required <https://docs.python.org/3/library/argparse.html#required>`_
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class OneOrMore(List[T]):
    """
    Tells the decorator that this argument requires one or more values.

    Internally this will add the :code:`nargs='?'` option to the argument.

    OneOrMore may specify a Type like :code:`int` in square brackets to tell the decorator what
    values are acceptable.

    On the Python side this will set the type of the argument to
    a generic :code:`List` with an optional type as required (default is :code:`str`)

    .. code-block::

        def cmd(values: OneOrMore[int])
            for n in values:
                ...

        parser.execute("cmd 1 2 3 4")

    See `argparse: -nargs <https://docs.python.org/3/library/argparse.html#nargs>`_
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class ZeroOrMore(List[T]):
    """
    Tells the decorator that this argument can have any number of entries, including zero entries.

    Internally this will add the :code:`nargs='*'` option to the argument.

    ZeroOrMore may specify a Type like :code:`int` in square brackets to tell the decorator what
    values are acceptable.

    On the Python side this will set the type of the argument to
    a generic :code:`List` with an optional type as required (default is :code:`str`)

    .. code-block::

        def cmd(values: ZeroOrMore[float])
            for n in values:
                ...

        parser.execute("cmd 1 2 3 4")

    See `argparse: -nargs <https://docs.python.org/3/library/argparse.html#nargs>`__
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class ZeroOrOne(Generic[T]):
    """
    Tells the decorator that this argument can have either one or zero entries

    Internally this will add the :code:`nargs='?'` option to the argument.

    ZeroOrMore may specify a Type like :code:`int` in square brackets to tell the
    decorator what values are acceptable.

    .. code-block::

        def cmd(value: ZeroOrOne[float])
            value.as_integer_ratio()

        parser.execute("cmd 1.5")

    See `argparse: -nargs <https://docs.python.org/3/library/argparse.html#nargs>`__
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly1(Generic[T]):
    """
    Tells the decorator that this argument has exactly one entry

    Internally this will add the :code:`nargs=1` option to the argument.

    :code:`Exactly1` may specify a Type like :code:`int` in square brackets to tell the
    decorator what value is acceptable.

    On the Python side this will set the type of the argument to
    a generic :code:`List` with an optional type as required (default is :code:`str`)

    .. code-block::

        @cli.command
        def cmd(value: Exactly1[float])
            value.as_integer_ratio()

        parser.execute("cmd 1.5")       # OK
        parser.execute("cmd 1.5 2.5")   # causes an error

    See `argparse: -nargs <https://docs.python.org/3/library/argparse.html#nargs>`__
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly2(List[T]):
    """The same as :class:`Exactly1`, except it expects 2 arguments.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly3(List[T]):
    """The same as :class:`Exactly1`, except it expects 3 arguments.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly4(List[T]):
    """The same as :class:`Exactly1`, except it expects 4 arguments.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly5(List[T]):
    """The same as :class:`Exactly1`, except it expects 5 arguments.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly6(List[T]):
    """The same as :class:`Exactly1`, except it expects 6 arguments.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly7(List[T]):
    """The same as :class:`Exactly1`, except it expects 7 arguments.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly8(List[T]):
    """The same as :class:`Exactly1`, except it expects 8 arguments.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Exactly9(List[T]):
    """The same as :class:`Exactly1`, except it expects 9 arguments.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class StoreAction:
    """
    Tells the *ArgumentParser* to just store the command line value in the annotated variable.

    This is the default action for an argument and is therefore usually not required.

    Internally this will add the :code:`action="store"` option to the argument.

    See `argparse: action <https://docs.python.org/3/library/argparse.html#action>`__
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class CustomAction(Generic[T]):
    """
    Tells the *ArgumentParser* to use a custom *Action* to process the command line value for this argument.

    *CustomAction* requires the name of a callable in square brackets. This callable can be either a subclass of
    `argparse.Action <https://docs.python.org/3/library/argparse.html#action-classes>`_ or a function with the
    same signature as the *Action* class.

    .. code-block:: python

        class MyAction(argparse.Action):
            def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None,
                         required=False, help=None, metavar=None)
                ...

        @cli.command
        def command(arg: CustomAction[MyAction]):
            ...

    Internally this will add the :code:`action=MyAction` option to the argument.

    Refer to `argument actions <https://docs.python.org/3/library/argparse.html#action>`_ and
    `action classes <https://docs.python.org/3/library/argparse.html#action-classes>`_ for more details
    on how to implement a custom action.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class StoreConstAction:
    """
    Tells the *ArgumentParser* to assign the given default value to the argument whenever it
    is present on the command line.

    This is similar to :class:`StoreTrueAction` but with a generic constant instead of the fixed :code:`True`.

    .. code-block::

        @cli.command
        def cmd(foo: Option | StoreConstAction = 42)
            return foo

        parser.execute("cmd --foo")         # returns 42
        parser.execute("cmd")               # returns None
        parser.execute("cmd --foo 100")     # causes unrecognized argument error

    .. note::
        This is not the same as just assigning a default value.

        .. code-block::

            @cli.command
            def cmd(foo: Option = 42):
                return foo

            cli.execute("cmd --foo")        # causes missing argument error
            cli.execute("cmd")              # returns 42
            cli.execute("cmd --foo 100")    # returns 100


    Internally this will add the :code:`action="store_const"` option to the argument and take the given default and
    set it as the :code:`const=...` option.

    See `argparse: action <https://docs.python.org/3/library/argparse.html#action>`__
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class StoreTrueAction:
    """
    Tells the *ArgumentParser* to set the argument to :code:`True` whenever it is present on the command line
    (and :code:`False` if it is absent).


    This is a special case of :class:`StoreConstAction` with a constant value of :code:`True`.

    .. code-block::

        @cli.command
        def cmd(foo: Option | StoreTrueAction)
            return foo

        parser.execute("cmd --foo")         # returns True
        parser.execute("cmd")               # returns False

    .. note::

        Instead of using :class:`StoreTrueAction` any :class:`Option` or :class:`Flag` can just be given a default of
        :code:`False`. Internally this is converted to a :class:`StoreTrueAction`.

        .. code-block::

            @cli.command
            def cmd(foo: Option = False)
                return foo

            parser.execute("cmd --foo")         # returns True
            parser.execute("cmd")               # returns False


    Internally this will add the :code:`action="store_true"` option to the argument.

    See `argparse: action <https://docs.python.org/3/library/argparse.html#action>`_
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class StoreFalseAction:
    """
    Tells the *ArgumentParser* to set the argument to :code:`False` whenever it is present on the command line
    (and :code:`True` if it is absent).

    This is a special case of :class:`StoreConstAction` with a constant value of :code:`False`.

    .. code-block::

        @cli.command
        def cmd(foo: Option | StoreFalseAction)
            return foo

        parser.execute("cmd --foo")         # returns False
        parser.execute("cmd")               # returns True

    .. note::

        Instead of using :class:`StoreFalseAction` any :class:`Option` or :class:`Flag` can just be given a default of
        :code:`True`. Internally this is converted to a :class:`StoreFalseAction`.

        .. code-block::

            @cli.command
            def cmd(foo: Option = True)
                return foo

            parser.execute("cmd --foo")         # returns False
            parser.execute("cmd")               # returns True

    Internally this will add the :code:`action="store_false"` option to the argument.

    See `argparse: action <https://docs.python.org/3/library/argparse.html#action>`_
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class AppendAction(List[T]):
    """
    Tells the *ArgumentParser* to append the command line value to a list.

    With this annotation an argument can be specified multiple times on the command line.

    .. code-block::

        @cli.command
        def cmd(foo: Option | AppendAction | int)
            return foo

        parser.execute("cmd --foo 1 --foo 2")  # returns [1, 2]

    Internally this will add the :code:`action = "append"` option to the argument.

    See `argparse: action <https://docs.python.org/3/library/argparse.html#action>`_ for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


# AppendConstAction is not supported.

# class AppendConstAction(List[T]):
#    """


#    Tells the *ArgumentParser* to append the command line value to a list.
#    With this annotation an argument can be specified multiple times on the command line
#
#    .. code-block::
#
#        def cmd(foo: Option | AppendAction | int)
#            return foo
#
#        parser.execute("cmd --foo 1 --foo 2")   # returns [1, 2]
#
#    Internally this will add the `action=append` option to the argument.
#
#    See `argparse: action <https://docs.python.org/3/library/argparse.html#action>`__
#    for details.
#    """

class CountAction(int):
    """
    Tells the *ArgumentParser* to just count the number of occurences of this argument on the command line.

    This action always returns an :code:`int` and can not be set to any type.

    .. code-block::

        @cli.command
        def cmd(v: CountAction)
            return v

        parser.execute("cmd -vvvv")   # returns 4

    Internally this will add the :code:`action="count"` option to the argument.

    See `argparse: action <https://docs.python.org/3/library/argparse.html#action>`_
    for details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class ExtendAction(List[T]):
    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")


class Choices(Generic[T]):
    """
    Tells the *ArgumentParser* that this argument can only accept some specific values.

    These values must be specified in square brackets. This can be either a list of items or
    anything else that returns a container of values.

    In following example the command takes two arguments: the first may be either "foo" or "bar" while the
    second argument accepts any integer between 1 and 4.

    .. code-block:: python

        @cli.command
        def command(arg1: Choices["foo", "bar"], arg2: Choices[range(1,5)] | int):
            ...

    .. note::

        Without `from __future__ import annotations <https://peps.python.org/pep-0563/>`_ Python versions
        prior to 3.10 do not like strings in type annotations. In this case the choices can be wrapped in a
        `Literal <https://docs.python.org/3/library/typing.html#typing.Literal>`_ to tell Python
        (or any type checker) to not evaluate them a load time.

        .. code-block::

            def command(arg1: Choices[Literal["foo", "bar"]], arg2: Choices[Literal[range(1,5)]])

    Internally the bracket content from *Choices* is parsed via
    :external:func:`eval`, so nothing dangerous should be put there - especially no functions of unknown source.
    The result from this is then added as :code:`choices=...` to the argument.

    See `argparse: choices <https://docs.python.org/3/library/argparse.html#choices>`_ for more details.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__name__} is only used for annotations and should not be instantiated,")
