#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or go to <https://opensource.org/licenses/MIT>.
#

# pylint: skip-file

from __future__ import annotations

import unittest

from argparsedecorator import *


class MyTestCase(unittest.TestCase):

    def test_readme_example_1(self):
        parser = ArgParseDecorator()

        @parser.command
        def ls(files: ZeroOrMore[str],
               a: Flag = True,
               ignore: Option | Exactly1[str] = "",
               columns: Option | int | Choices[Literal["range(1,5)"]] = 1,
               sort: Option | Choices[Literal["fwd", "rev"]] = "fwd",
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

        # parser.execute("help ls")
        result = parser.execute("ls -a -c 2 --sort rev --ignore *.log")
        self.assertTrue(result['a'])
        self.assertEqual(2, result['columns'])
        self.assertEqual("rev", result['sort'])
        self.assertEqual(["*.log"], result['ignore'])

    def test_annotations_flag(self):
        parser = ArgParseDecorator()

        @parser.command
        def cmd(f: Flag = False):
            return f

        self.assertTrue(parser.execute("cmd -f"))
        self.assertFalse(parser.execute("cmd"))

    def test_annotations_option(self):
        parser = ArgParseDecorator()

        @parser.command
        def cmd(foo: Option = False):
            return foo

        self.assertTrue(parser.execute("cmd --foo"))
        self.assertFalse(parser.execute("cmd"))


if __name__ == '__main__':
    unittest.main()
