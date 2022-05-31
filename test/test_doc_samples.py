#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or go to <https://opensource.org/licenses/MIT>.
#

# pylint: skip-file

from __future__ import annotations

import io
import unittest
from argparse import ArgumentError

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

    def inner_function(self):
        parser = ArgParseDecorator()
        self.parser = parser

        @parser.command
        def cmd(arg):
            return arg, self.parser

    def test_inner_function(self):
        self.inner_function()  # set up parser
        result1, result2 = self.parser.execute("cmd foo")
        self.assertEqual("foo", result1)
        self.assertEqual(self.parser, result2)

    def test_error_handler(self):
        stdout = io.StringIO()

        def my_error_handler(err: ArgumentError):
            print(str(err))  # output the error message to stdout instead of stderr

        cli = ArgParseDecorator()

        cli.execute("command", error_handler=my_error_handler, stdout=stdout)
        self.assertTrue(len(stdout.getvalue()) > 10)

    def test_input_redirect(self):
        cli = ArgParseDecorator()
        my_stdin = io.StringIO("yes")
        stdout = io.StringIO()

        @cli.command
        def delete():
            print("type 'yes' to confirm that you want to delete everything")
            result = input()
            if result == "yes":
                print("you have chosen 'yes'")

        cli.execute("delete", stdin=my_stdin, stdout=stdout)
        self.assertEqual("you have chosen 'yes'", stdout.getvalue().splitlines()[1])


if __name__ == '__main__':
    unittest.main()
