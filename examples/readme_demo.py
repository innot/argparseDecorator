#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or go to <https://opensource.org/licenses/MIT>.
#
from typing import Union

from argparsedecorator import *

parser = ArgParseDecorator()


@parser.command
def multi(text: ZeroOrMore[str], n: Union[Flag, int] = 2):
    """
    Print the given text multiple times.
    :param text: the text to be repeated
    :param n: number of times to repeat the text, default is 2
    """
    txt = " ".join(text)
    for i in range(0, n):
        print(txt)


# parser.execute("multi -n 5 this is a test")


@parser.command
def add(values: OneOrMore[float], squared: Option = True) -> None:
    """
    Add up a list of numbers.
    :param values: one or more numbers
    :param squared: when present square each number first
    :alias squared: -sq
    """
    if squared:
        values = [x * x for x in values]
    print(sum(values))


parser.execute("help add")
