from typing import NewType, Any, List, TypeVar, Generic

Flag = NewType('Flag', Any)
"""Declare that this argument is a flag that will be prefixed by a single '-'."""

Optional = NewType('Optional', Any)
"""Declare that this argument is an optional argument that will be prefixed by a double '--'."""

OneOrMore = NewType('OneOrMore', list)

ZeroOrMore = NewType('ZeroOrMore', list)

ZeroOrOne = NewType('ZeroOrOne', Any)

# NumArgs = NewType('NumArgs', list)

Int = TypeVar('Int', bound=int)
T = TypeVar('T')


class NumArgs(Generic[Int, T], List[T]):
    pass


StoreAction = NewType('StoreAction', Any)
StoreConstAction = NewType('StoreConstAction', Any)
StoreTrueAction = NewType('StoreTrueAction', Any)
StoreFalseAction = NewType('StoreFalseAction', Any)
AppendAction = NewType('AppendAction', list)
AppendConstAction = NewType('AppendConstAction', list)
CountAction = NewType('CountAction', int)
ExtendAction = NewType('ExtendAction', list)
