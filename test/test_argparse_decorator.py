# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt file or go to <https://opensource.org/licenses/MIT>.
from __future__ import annotations

import unittest
from argparse import ArgumentError
from typing import Literal

from argparsedecorator.annotations import *
from argparsedecorator.argparse_decorator import *


class MyTestCase(unittest.TestCase):

    def test_simple_command(self):
        apd = ArgParseDecorator()

        @apd.command
        def cmd(_):
            pass

        self.assertIsNotNone(apd.rootnode.has_node('cmd'))

        @apd.command()
        def cmd2(_):
            pass

        self.assertIsNotNone(apd.rootnode.has_node('cmd2'))

    def test_description(self):
        apd = ArgParseDecorator()

        @apd.command
        def cmd(_):
            """helpstring"""
            pass

        self.assertEqual('helpstring', apd.rootnode.get_node('cmd').description)

    def test_simple_arguments(self):
        apd = ArgParseDecorator()

        @apd.command
        def cmd(arg1: str, arg2: int):
            self.assertEqual("foobar", arg1)
            self.assertEqual(42, arg2)
            pass

        node = apd.rootnode.get_node('cmd')
        args = node.arguments
        self.assertEqual(2, len(args))
        apd.execute("cmd foobar 42")

    def test_flag(self):
        apd = ArgParseDecorator()

        @apd.command
        def cmd(arg1: Flag, arg2: Union[Flag, int], arg3: Flag) -> Tuple:
            return arg1, arg2, arg3

        node = apd.rootnode.get_node('cmd')
        args = node.arguments
        for name, arg in args.items():
            self.assertTrue(arg.optional)
            self.assertTrue(name.startswith("-"))
            self.assertTrue(arg.name.startswith("-"))

        self.assertEqual(int, args['-arg2'].type)

        a1, a2, a3 = apd.execute("cmd -arg1 foo -arg2 42")
        self.assertEqual("foo", a1)
        self.assertEqual(42, a2)
        self.assertIsNone(a3)

    def test_flag_actions(self):
        apd = ArgParseDecorator()

        @apd.command
        def cmd(foo: Flag = True, bar: Flag = False, baz: Flag = False) -> Tuple:
            return foo, bar, baz

        node = apd.rootnode.get_node('cmd')
        args = node.arguments
        self.assertEqual("store_true", args["-foo"].action)
        self.assertEqual("store_false", args["-bar"].action)
        self.assertEqual("store_false", args["-baz"].action)

        f1, f2, f3 = apd.execute("cmd -foo -bar")
        self.assertTrue(f1)
        self.assertFalse(f2)
        self.assertFalse(f3)

    def test_option(self):
        apd = ArgParseDecorator()

        @apd.command
        def cmd(foo: Option, bar: Union[Option, OneOrMore[int]]) -> Tuple:
            return foo, bar

        node = apd.rootnode.get_node('cmd')
        args = node.arguments
        self.assertIsNotNone(args['--foo'])
        self.assertIsNotNone(args['--bar'])

        f1, f2 = apd.execute("cmd --foo baz --bar 1 2 3")
        self.assertEqual('baz', f1)
        self.assertListEqual([1, 2, 3], f2)

    def test_count_action(self):
        apd = ArgParseDecorator(helpoption=None)

        @apd.command
        def cmd(verbose: Union[Option, CountAction]) -> int:
            """
            :param verbose: Verbosity level
            :alias verbose: -v
            :return: number of verbosity level flags
            """
            return verbose

        node = apd.rootnode.get_node('cmd')
        args = node.arguments
        self.assertEqual("count", args["--verbose"].action)
        self.assertEqual(3, apd.execute("cmd -vvv"))
        self.assertEqual(2, apd.execute("cmd --verbose -v"))

    def test_choices(self):
        apd = ArgParseDecorator()

        @apd.command
        def cmd(arg: Union[str, Choices[Literal["rock", "paper", "scissors"]]]) -> str:
            return arg

        node = apd.rootnode.get_node('cmd')
        args = node.arguments
        self.assertCountEqual(["rock", "paper", "scissors"], args["arg"].choices)
        self.assertEqual("rock", apd.execute("cmd rock"))
        with self.assertRaises(ArgumentError):
            apd.execute("cmd foobar")

    def test_with_deco_argument(self):
        apd = ArgParseDecorator()

        @apd.command()
        @apd.add_argument("foo")
        @apd.add_argument("bar")
        def cmd(*args: str, **kwargs: Any) -> Tuple[str]:
            return args

        result = apd.execute("cmd foo bar")
        self.assertEqual("foo", result[0])
        self.assertEqual("bar", result[1])

    # Test command class methods (having self)

    parser = ArgParseDecorator()

    @parser.command
    def foobar(self, arg1: int = 42) -> int:
        self.foobar_arg1 = arg1
        return arg1

    def test_classmethod(self):
        node = self.parser.rootnode.get_node("foobar")
        self.assertIsNotNone(node)
        args = node.arguments
        self.assertTrue("arg1" in args)
        arg1 = args['arg1']
        self.assertEqual(int, arg1.type)
        self.assertEqual(42, arg1.default)

        result = self.parser.execute("foobar 101", self)
        self.assertEqual(101, result)
        self.assertEqual(101, self.foobar_arg1)


if __name__ == '__main__':
    unittest.main()
