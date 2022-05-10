# (c)

""" The Annotations for the argparseDecorator.

This module contains a number of classes that can be used as type annotations to give the
decorator more metadata used to describe the argument.

All annotation classes in this module do not contain any code and should not be instantiated.
Some annotation classes are generic types which can encapsulate an optional type, e.g.

.. code-block:: python

    def command(files: OneOrMore[str])

while other annotations are strictly used as markers and may not encapsulate other types.

.. code-block:: python

    def commanf(verbose: Option | StoreTrueAction)
"""

from typing import TypeVar, List, Generic

# Using custom classes instead of NewType is not very efficient,
# but it allows for Generic Types which can be used to add
# a type to the options, e.g. OneOrMore[int]


T = TypeVar('T')


class Flag:  # pylint: disable=too-few-public-methods
    """
    Marks the argument as a Flag.

    A Flag starts with a single hyphen ´-´.

    If the Flag does not require any arguments (just present or not present) add a ´=True` as its
    default or add a :class:'StoreTrueAction' annotation.

    .. code-block::

        def cmd(f: Flag = True):
            return f

        result = parser.execute("cmd -f")  # result = True
        result = parser.execute("cmd")       # result = False

    See `argparse: name-or-flags <https://docs.python.org/3/library/argparse.html#name-or-flags>`_
    for details.
    """


class Option:  # pylint: disable=too-few-public-methods
    """
    Marks the argument as an Option.

    A Option starts with a double hyphen ´--´.

    If the Option does not require any arguments (just present or not present) add a ´=True` as its
    default or add a :class:'StoreTrueAction' annotation.

    .. code-block::

        def cmd(foo: Option = True):
            return foo

        result = parser.execute("cmd -foo")  # result = True
        result = parser.execute("cmd")       # result = False

    See `argparse: name-or-flags <https://docs.python.org/3/library/argparse.html#name-or-flags>`_
    for details.
    """


class OneOrMore(List[T]):  # pylint: disable=too-few-public-methods
    """
    Tells the decorator that this argument requires one or more entries.

    Internally this will add the `nargs='?'` option to the argument.

    OneOrMore may specify a Type like `int` in square brackets to tell the decorator what
    values are acceptable.

    On the Python side this will set the type of the argument to
    a generic `List` with an optional type as required (default is `str`)

    .. code-block::

        def cmd(values: OneOrMore[int])
            for n in values:
                ...

        parser.execute("cmd 1 2 3 4")

    See `argparse: -nargs <https://docs.python.org/3/library/argparse.html#nargs>`_
    for details.
    """


class ZeroOrMore(List[T]):  # pylint: disable=too-few-public-methods
    """
    Tells the decorator that this argument can have any number of entries, including zero entries.

    Internally this will add the `nargs='*'` option to the argument.

    ZeroOrMore may specify a Type like `int` in square brackets to tell the decorator what
    values are acceptable.

    On the Python side this will set the type of the argument to
    a generic `List` with an optional type as required (default is `str`)

    .. code-block::

        def cmd(values: ZeroOrMore[float])
            for n in values:
                ...

        parser.execute("cmd 1 2 3 4")

    See `argparse: -nargs <https://docs.python.org/3/library/argparse.html#nargs>`__
    for details.
    """


class ZeroOrOne(Generic[T]):  # pylint: disable=too-few-public-methods
    """
    Tells the decorator that this argument can have either one or zero entries

    Internally this will add the `nargs='?'` option to the argument.

    ZeroOrMore may specify a Type like `int` in square brackets to tell the
    decorator what values are acceptable.

    .. code-block::

        def cmd(value: ZeroOrOne[float])
            value.as_integer_ratio()

        parser.execute("cmd 1.5")

    See `argparse: -nargs <https://docs.python.org/3/library/argparse.html#nargs>`__
    for details.
    """


class Exactly1(Generic[T]):  # pylint: disable=too-few-public-methods
    """
    Tells the decorator that this argument has exactly one entry

    Internally this will add the `nargs=1` option to the argument.

    `Exactly1` may specify a Type like `int` in square brackets to tell the
    decorator what value is acceptable.

    On the Python side this will set the type of the argument to
    a generic `List` with an optional type as required (default is `str`)

    .. code-block::

        def cmd(value: Exactly1[float])
            value.as_integer_ratio()

        parser.execute("cmd 1.5")       # OK
        parser.execute("cmd 1.5 2.5")   # causes an error

    See `argparse: -nargs <https://docs.python.org/3/library/argparse.html#nargs>`__
    for details.
    """


class Exactly2(List[T]):  # pylint: disable=too-few-public-methods
    pass


class Exactly3(List[T]):  # pylint: disable=too-few-public-methods
    pass


class Exactly4(List[T]):  # pylint: disable=too-few-public-methods
    pass


class Exactly5(List[T]):  # pylint: disable=too-few-public-methods
    pass


class Exactly6(List[T]):  # pylint: disable=too-few-public-methods
    pass


class Exactly7(List[T]):  # pylint: disable=too-few-public-methods
    pass


class Exactly8(List[T]):  # pylint: disable=too-few-public-methods
    pass


class Exactly9(List[T]):  # pylint: disable=too-few-public-methods
    pass


class StoreAction:  # pylint: disable=too-few-public-methods
    pass


class StoreConstAction:  # pylint: disable=too-few-public-methods
    pass


class StoreTrueAction:  # pylint: disable=too-few-public-methods
    pass


class StoreFalseAction:  # pylint: disable=too-few-public-methods
    pass


class AppendAction(List[T]):  # pylint: disable=too-few-public-methods
    pass


class AppendConstAction(List[T]):  # pylint: disable=too-few-public-methods
    pass


class CountAction(int):  # pylint: disable=too-few-public-methods
    pass


class ExtendAction(List[T]):  # pylint: disable=too-few-public-methods
    pass


class Choices(Generic[T]):  # pylint: disable=too-few-public-methods
    pass
