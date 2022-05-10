#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or go to <https://opensource.org/licenses/MIT>.
#
from __future__ import annotations

import unittest

from argparsedecorator import *


class MyTestCase(unittest.TestCase):

    def test_readme_example_1(self):
        parser = ArgParseDecorator()

        @parser.command
        def ls(files: ZeroOrMore[str],
               a: Flag = True,  # create '-a' flag argument that is 'True' if '-a' is on the command line.
               ignore: Option | Exactly1[str] = "",  # create optional '--ignore PATTERN' argument
               columns: Option | int | Choices[Literal["range(1,5)"]] = 1,  # valid input for '--columns' is 1 to 4
               sort: Option | Choices[Literal["fwd", "rev"]] = "fwd",  # '--sort {fwd,rev}' with default 'fwd'
               ):
            """
            List information about files (the current directory by default).
            :param files: List of files, may be empty.

            :param a: do not ignore entries strating with '.'
            :alias a: --all

            :param ignore: do not list entries matching PATTERN
            :metavar ignore: PATTERN

            :param columns: number of output columns, must be between 1 and 4
            :alias columns: -c

            :param sort: alphabetic direction of output, either 'fwd' (default) or 'rev'
            :alias sort: -s
            """
            return {"files": files, "a": a, "ignore": ignore, "columns": columns, "sort": sort}

        parser.execute("help ls")
        result = parser.execute("ls -a -c 2 --sort rev --ignore *.log")
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
