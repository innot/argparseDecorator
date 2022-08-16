# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file
# or go to <https://opensource.org/licenses/MIT>.


import argparse
import sys
from typing import NoReturn


class NonExitingArgumentParser(argparse.ArgumentParser):
    """
    Slightly modified version of the default
    `ArgumentParser <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_
    to make it more suitable for a self-contained command line interpreter.

    It overrides the :meth:`exit` and :meth:`error` methods and removes the *sys.exit* calls,
    instead raising an ``ArgumentError`` upon errors.

    (Pyhton 3.9+) It also sets the *exit_on_error* flag to a default of *False* so that
    internal argument errors are not caught and routed through :meth:`error` but passed on
    to the caller directly.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "exit_on_error" not in kwargs:
            # Python 3.9+: let errors throw an ArgumentException directly instead of going
            # through self.error(). This retains more information about the error.
            self.exit_on_error = False

    def exit(self, status=0, message=None):
        """
        Overriden to not call `sys.exit() <https://docs.python.org/3/library/sys.html#sys.exit>`_.
        Instead an ``ArgumentError`` is raised if the status is not zero.
        """
        self._print_message(message, sys.stderr)

        if status != 0:
            raise argparse.ArgumentError(None, message)

    def error(self, message) -> NoReturn:
        """
        Error parsing the command line.

        This overrides the default behaviour of ArgumentParser (print usage and exit) to just pass
        the error message to the caller as an ``ArgumentParser.ArgumentError``

        :param message: The error message
        :raises: ArgumentError with the error message
        """
        raise argparse.ArgumentError(None, message)
