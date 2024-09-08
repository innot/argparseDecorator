# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file or go to <https://opensource.org/licenses/MIT>.

# import Literal right away as it is used by the Choices annotation.

from typing import Literal

from .annotations import *
from .argparse_decorator import ArgParseDecorator
from .nonexiting_argumentparser import NonExitingArgumentParser

_ = Literal[""]  # just to keep the type checker from complaining abaout am unused import

# all annotation classes
__api_classes__ = [Flag, RequiredFlag, Option, RequiredOption, OneOrMore, ZeroOrMore, ZeroOrOne,
                   Exactly1, Exactly2, Exactly3, Exactly4, Exactly5,
                   Exactly6, Exactly7, Exactly8, Exactly9,
                   StoreAction, CustomAction, StoreConstAction, StoreTrueAction, StoreFalseAction,
                   AppendAction, ExtendAction, CountAction, Choices]

# all others
__api_classes__.extend([ArgParseDecorator, NonExitingArgumentParser])

# define the public API
__all__ = [c.__name__ for c in __api_classes__]
