# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file
# or go to <https://opensource.org/licenses/MIT>.


import argparse
import builtins
from typing import Callable, Optional, IO


class NonExitingArgumentParser(argparse.ArgumentParser):
    """
    Slightly modified version of the default :class:'ArgumentParser' to make it more suitable
    for a self contained command line interpreter.

    1. Inhibit programm exits by
        a. setting the 'exit_on_error' flag to False (works only Pyhton 3.9+) and
        b. overriding the exit() method.
    2. Redirect all output to a user supplied print function instead of stdout/stderr.

    """

    def __init__(self, *args, **kwargs):
        if 'print_func' in kwargs:
            self.print_function: Callable = kwargs.pop('print_func')
        else:
            self.print_function = builtins.print
        super().__init__(*args, **kwargs)
        self.exit_on_error = False

    # Overriding this method as argparse prints to stderr which might
    # not be available depending on the use case.
    def _print_message(self, message: str, file: Optional[IO[str]] = ...) -> None:
        if message:
            self.print_function(message)

    # ArgumentParser has a tendency to exit, even with "exit_on_error" set to False,
    # e.g. after showing a help message.
    # Overriding this method to disregard a normal exit and to raise an Exception for errors.
    def exit(self, status=0, message=None):
        if status != 0:
            raise SyntaxError(message=message)
