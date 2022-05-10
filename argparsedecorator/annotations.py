from typing import TypeVar, List, Generic

# Using custom classes instead of NewType is not very efficient,
# but it allows for Generic Types which can be used to add
# a type to the options, e.g. OneOrMore[int]


T = TypeVar('T')


class Flag:
    """
    Marks the argument as a Flag.
    A Flag starts with a single hyphen ´-´.
    If the Flag does not require any arguments (just present or not present) add a ´=True` as its
    default or add a `StoreTrue´ annotation.

    .. code::
        def cmd(someflag: Flag = True):
        ...

    See 'argparse Docs https://docs.python.org/3/library/argparse.html#name-or-flags'_
    """
    pass


class Option:
    pass


class OneOrMore(List[T]):
    pass


class ZeroOrMore(List[T]):
    pass


class ZeroOrOne(Generic[T]):
    pass


class Exactly1(Generic[T]):
    pass


class Exactly2(List[T]):
    pass


class Exactly3(List[T]):
    pass


class Exactly4(List[T]):
    pass


class Exactly5(List[T]):
    pass


class Exactly6(List[T]):
    pass


class Exactly7(List[T]):
    pass


class Exactly8(List[T]):
    pass


class Exactly9(List[T]):
    pass


class StoreAction:
    pass


class StoreConstAction:
    pass


class StoreTrueAction:
    pass


class StoreFalseAction:
    pass


class AppendAction(List[T]):
    pass


class AppendConstAction(List[T]):
    pass


class CountAction(int):
    pass


class ExtendAction(List[T]):
    pass


class Choices(Generic[T]):
    pass
