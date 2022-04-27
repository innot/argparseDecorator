# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt file or go to <https://opensource.org/licenses/MIT>.

import argparse
import builtins
import re
from typing import Tuple, List, Final, Dict, Union

from argparse_decorator.utils import T_Arg


def analyse_docstring(docstring: str) -> Tuple[str, List[T_Arg]]:
    """

    :param docstring:
    :return: Tuple with the description string and a list of arguments
    """
    state_desc: Final = 1
    state_args: Final = 2
    state = state_desc

    description: List[str] = []
    args: List[T_Arg] = []

    lines = docstring.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("arguments::"):
            state = state_args
            continue
        if not line:  # disregard empty lines
            continue

        if state == state_desc:
            description.append(line)
        elif state == state_args:
            args.append(analyse_argstring(line))

    return ''.join(description), args


def analyse_argstring(argstring: str) -> T_Arg:
    args: List[str] = []  # actully a tuple, but we convert at the end
    kwargs: Dict[str, Union[str, int, List]] = {}
    is_flag = None
    arg_type = None
    next_is_const = False
    nargs_positional = 0
    nargs_optional = 0

    subparts = argstring.split('::')
    arg_part = subparts.pop(0).strip()
    if subparts:
        kwargs['help'] = subparts[0].strip()

    token_spec = [
        ('FLAG', r"\-+\w+"),  # Flags like -f or --foo
        ('TYPE', r"(?<=:)\w+"),
        ('DEFAULT', r"(?<==)\w+"),
        ('MULTI', r"(?<=\()[\w|]+"),
        ('OPTIONAL', r"(?<=\[)\w+"),
        ('POSITIONAL', r"(\w+)"),
        ('MANY', r"\[\.{3}\]")
    ]

    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)

    if arg_part.startswith('-'):
        is_flag = True

    line_start = 0
    for mo in re.finditer(tok_regex, arg_part):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start

        if kind == 'FLAG':
            if is_flag:
                args.append(value)
            else:
                raise ValueError(f"FLag in named argument not allowed at column {column}")

        if kind == 'POSITIONAL':
            nargs_positional += 1
            if not is_flag:
                args.append(value)

        if kind == 'OPTIONAL':
            nargs_optional += 1
            if not is_flag:
                args.append(value)

        if kind == 'TYPE':
            if value.lower() == 'true':
                kwargs['action'] = "store_true"
            elif value.lower() == 'false':
                kwargs['action'] = "store_false"
            elif value.lower() == 'const':
                kwargs['action'] = "store_const"
                next_is_const = True
            else:
                # arg_type is a builtin like 'str', 'int' etc.
                # Convert the arg_type to a callable suitable for the ArgumentParser
                dtype = getattr(builtins, value)
                if arg_type:
                    if arg_type != dtype:
                        raise ValueError(f"Multiple type attribute error in column {column}")
                kwargs['type'] = dtype
                arg_type = dtype

        if kind == 'DEFAULT':
            if next_is_const:
                next_is_const = False
                kwargs['const'] = value
            else:
                if value.lower() == "suppress":
                    value = argparse.SUPPRESS
                kwargs['default'] = value

        if kind == 'MULTI':
            choices = value.split('|')
            # if type is defined we need to convert to that type
            # see https://docs.python.org/3/library/argparse.html#choices
            if arg_type:
                choices = list(map(arg_type, choices))

            kwargs['choices'] = choices

        if kind == 'MANY':
            if not is_flag and nargs_positional == 0:
                raise ValueError("Multi-arguments require at least one positional argument")
            nargs_optional += 2

    if nargs_optional == 1 and nargs_positional == 0:
        kwargs['nargs'] = '?'
    elif nargs_optional > 1 and nargs_positional == 0:
        kwargs['nargs'] = '*'
    elif nargs_positional > 0 and nargs_optional == 0:
        kwargs['nargs'] = nargs_positional
    elif nargs_positional > 0 and nargs_optional > 0:
        kwargs['nargs'] = '+'

    result: T_Arg = (tuple(args), kwargs)
    return result
