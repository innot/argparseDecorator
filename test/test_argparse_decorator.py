# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file
# or go to <https://opensource.org/licenses/MIT>.

# pylint: skip-file

from __future__ import annotations

import argparse
import io
import unittest
from typing import Literal

from argparsedecorator import NonExitingArgumentParser
from argparsedecorator.annotations import *
from argparsedecorator.argparse_decorator import *


class TestSync(unittest.TestCase):

    def test_init(self):
        apd = ArgParseDecorator()
        self.assertIsNotNone(apd)

        apd = ArgParseDecorator(argparser_class=argparse.ArgumentParser)
        self.assertEqual(argparse.ArgumentParser, apd.rootnode.argparser_class)

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            _ = ArgParseDecorator(argparser_class=str)

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
        def cmd(foo: Flag = False, bar: Flag = False, baz: Flag = True, bang: Flag = True) -> Tuple:
            return foo, bar, baz, bang

        node = apd.rootnode.get_node('cmd')

        args = node.arguments
        self.assertEqual("store_true", args["-foo"].action)
        self.assertEqual("store_true", args["-bar"].action)
        self.assertEqual("store_false", args["-baz"].action)
        self.assertEqual("store_false", args["-bang"].action)

        f1, f2, f3, f4 = apd.execute("cmd -foo -baz")
        self.assertTrue(f1)
        self.assertFalse(f2)
        self.assertFalse(f3)
        self.assertTrue(f4)

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
            apd.execute("cmd foobar", error_handler=None)

    def test_with_deco_argument(self):
        apd = ArgParseDecorator()

        @apd.command()
        @apd.add_argument("foo")
        @apd.add_argument("bar")
        def cmd(*args: str, **kwargs: Any) -> tuple[tuple[str, ...], dict[str, Any]]:
            return args, kwargs

        result, _ = apd.execute("cmd foo bar")
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

        with self.assertRaises(ValueError):
            self.parser.execute("foobar 101", None)

        with self.assertRaises(ValueError):
            self.parser.execute("foobar 101")

    def test_output_redirect(self):
        parser = ArgParseDecorator()

        @parser.command
        def echo(text: str):
            print(text)

        stdout = io.StringIO()
        stderr = io.StringIO()
        parser.execute("echo foobar", stdout=stdout, stderr=stderr)
        self.assertTrue(stdout.getvalue().startswith("foobar"))  # ignore any cr/lf

        stdout = io.StringIO()
        stderr = io.StringIO()
        parser.execute("help echo", stdout=stdout, stderr=stderr)
        self.assertTrue(len(stdout.getvalue()) > 10)  # more than a line feed

        stdout = io.StringIO()
        stderr = io.StringIO()
        parser.execute("invalid", stdout=stdout,
                       stderr=stderr)  # missing argument should cause an error
        self.assertTrue(len(stderr.getvalue()) > 10)

    def test_input_redirect(self):
        parser = ArgParseDecorator()

        @parser.command
        def inp():
            text = input()
            print(text)

        stdin = io.StringIO("foobar\n")
        stdout = io.StringIO()

        parser.execute("inp", stdin=stdin, stdout=stdout)
        self.assertTrue(stdout.getvalue().startswith("foobar"))

    def test_split_commandline(self):
        # string cmdline
        self.assertEqual(["foo", "bar", "baz"], split_commandline("foo bar baz"))
        self.assertEqual(["foo", "bar", "baz"], split_commandline("  foo  bar  baz  "))
        self.assertEqual(["foo", "bar baz"], split_commandline('foo "bar baz"'))
        self.assertEqual(['cmd', "'foo bar'"], split_commandline('cmd "\'foo bar\'"'))
        # check correct whitespace split
        self.assertEqual(["foo", "-f", "--v"], split_commandline("foo -f --v"))

        # list commandline
        self.assertEqual(["foo", "bar", "baz"], split_commandline(["foo", "bar", "baz"]))
        self.assertEqual(["foo", "bar baz"], split_commandline(["foo", "bar baz"]))
        self.assertEqual(["foo", "bar baz"], split_commandline([str(Path("some/path/foo")), "bar baz"]))
        self.assertEqual(["foo", "'bar baz'"], split_commandline([str(Path("some/path/foo.py")), "\'bar baz\'"]))

        # iterator commandline
        lexer = shlex("foo bar baz")
        self.assertEqual(["foo", "bar", "baz"], split_commandline(lexer))

        # invalid commandline
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            split_commandline(123)

    def test_suppress_option(self):
        cli = ArgParseDecorator()

        @cli.command
        def test(debug: Option | bool = False, foo: Option = False):
            """
            Test suppressed arguments.
            :param debug: SUPPRESS Turn on debugging
            :param foo: unsuppressed help
            """
            return debug, foo

        stdout = io.StringIO()
        stderr = io.StringIO()
        cli.execute("help test", stdout=stdout, stderr=stderr)
        helptext = stdout.getvalue()
        self.assertFalse("debug" in helptext)

    def test_argparse_help_argparse(self):
        cli = ArgParseDecorator(helpoption="-h")

        @cli.command
        def test(foobar):
            """
            Test -h help argument.
            :param foobar: some value
            """
            return foobar

        stdout = io.StringIO()
        stderr = io.StringIO()
        cli.execute("test -h", stdout=stdout, stderr=stderr)
        helptext = stdout.getvalue()
        self.assertTrue("foobar" in helptext)

    def test_argparse_help_none(self):
        cli = ArgParseDecorator(helpoption=None)

        @cli.command
        def test(foobar):
            """
            Test -h help argument.
            :param foobar: some value
            """
            return foobar

        stdout = io.StringIO()
        stderr = io.StringIO()
        cli.execute("test -h foobar", stdout=stdout, stderr=stderr)
        errtext = stderr.getvalue()
        self.assertTrue("-h" in errtext)
        stdout.flush()
        stderr.flush()
        cli.execute("help test", stdout=stdout, stderr=stderr)
        errtext = stderr.getvalue()
        self.assertTrue("help" in errtext)

        # test invalid helpoption
        with self.assertRaises(ValueError):
            _ = ArgParseDecorator(helpoption="foobar")

    def test_custom_argparser(self):
        class TestParser(argparse.ArgumentParser):
            pass

        cli = ArgParseDecorator(argparser_class=None)
        self.assertEqual(NonExitingArgumentParser, cli.argumentparser.__class__)

        cli = ArgParseDecorator(argparser_class=TestParser)
        self.assertEqual(TestParser, cli.argumentparser.__class__)

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            cli = ArgParseDecorator(argparser_class=str)
            print(cli.argumentparser.__class__)  # should not get here

    def test_argumentparser_property(self):
        cli = ArgParseDecorator()
        self.assertTrue(isinstance(cli.argumentparser, ArgumentParser))

    def test_command_dict(self):
        cli = ArgParseDecorator()

        @cli.command
        def cmd_on():
            pass

        @cli.command
        def cmd_off():
            pass

        cmds = cli.command_dict
        self.assertIsNotNone(cmds)
        self.assertDictEqual({"help": None, "cmd": {"on": None, "off": None}}, cmds)

    def test_command_aliases(self):
        cli = ArgParseDecorator()

        @cli.command(aliases=["foo", "bar"])
        def foobar(arg1: int) -> int:
            return arg1

        result = cli.execute("foobar 100")
        self.assertEqual(100, result)

        result = cli.execute("foo 101")
        self.assertEqual(101, result)

        result = cli.execute("bar 102")
        self.assertEqual(102, result)

        @cli.command(aliases="test2")  # check single alias
        def test1(arg1: int) -> int:
            return arg1

        result = cli.execute("test1 100")
        self.assertEqual(100, result)
        result = cli.execute("test2 101")
        self.assertEqual(101, result)

        # test invalid aliases
        with self.assertRaises(ValueError):
            @cli.command(aliases=["good", 100])
            def test2() -> None:
                pass

        with self.assertRaises(ValueError):
            @cli.command(aliases=100)
            def test3() -> None:
                pass


class TestAsync(unittest.IsolatedAsyncioTestCase):

    async def test_async_execute(self):
        cli = ArgParseDecorator()

        # first test a synchronous function
        @cli.command
        def test1() -> int:
            return 42

        result = await cli.execute_async("test1")
        self.assertEqual(42, result)

        # and now an asynchronous function
        @cli.command
        async def test2() -> int:
            return 43

        result = await cli.execute_async("test2")
        self.assertEqual(43, result)

    async def test_async_redirect(self):
        cli = ArgParseDecorator()

        @cli.command
        async def test() -> None:
            result = input()
            print(result)
            sys.stderr.write("stderrtest")

        stdin = io.StringIO("stdintest")
        stdout = io.StringIO()
        stderr = io.StringIO()

        await cli.execute_async("test", stdin=stdin, stdout=stdout, stderr=stderr)
        self.assertEqual(stdout.getvalue().strip(), stdin.getvalue().strip())
        self.assertTrue("stderrtest" in stderr.getvalue())

    async def test_errorhandler(self):
        cli = ArgParseDecorator()
        self.err = ""

        @cli.command
        async def test(foo: int) -> int:
            return foo

        def myerrorhandler(err: ArgumentError):
            self.err = err

        await cli.execute_async("test foobar", error_handler=lambda x: myerrorhandler(x))
        self.assertTrue(isinstance(self.err, ArgumentError))

        with self.assertRaises(ArgumentError):
            await cli.execute_async("test foobar", error_handler=None)

    parser = ArgParseDecorator()

    @parser.command
    async def foobar(self, arg1: int = 42) -> int:
        self.foobar_arg1 = arg1
        return arg1

    async def test_classmethod(self):
        node = self.parser.rootnode.get_node("foobar")
        self.assertIsNotNone(node)
        args = node.arguments
        self.assertTrue("arg1" in args)
        arg1 = args['arg1']
        self.assertEqual(int, arg1.type)
        self.assertEqual(42, arg1.default)

        result = await self.parser.execute_async("foobar 101", self)
        self.assertEqual(101, result)
        self.assertEqual(101, self.foobar_arg1)

        with self.assertRaises(ValueError):
            await self.parser.execute_async("foobar 101", None)

        with self.assertRaises(ValueError):
            await self.parser.execute_async("foobar 101")


if __name__ == '__main__':
    unittest.main()
