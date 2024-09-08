# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file or go to <https://opensource.org/licenses/MIT>.
import argparse
import unittest
from typing import Literal

from argparsedecorator import NonExitingArgumentParser
from argparsedecorator.argparse_decorator import Argument
from argparsedecorator.argparse_decorator import ParserNode
from argparsedecorator.parsernode import resolve_literals, split_union, fullname
from argparsedecorator.annotations import *


class MyTestCase(unittest.TestCase):

    def test_properies(self):
        node = ParserNode("test")
        self.assertEqual("test", node.title)
        with self.assertRaises(AttributeError):
            # noinspection PyPropertyAccess
            node.title = "foobar"  # read only property

        tmpnode = node
        for i in range(5):
            tmpnode = tmpnode.get_node(f"{i}")
            self.assertEqual(node, tmpnode.root)
        with self.assertRaises(AttributeError):
            # noinspection PyPropertyAccess
            node.root = tmpnode  # read only property

        self.assertTrue(type(tmpnode.argparser_class) is type(NonExitingArgumentParser))  # default
        tmpnode.argparser_class = argparse.ArgumentParser
        # can't use AssertIsInstance because NonExitingArgumentParser is an instance of ArgumentParser
        self.assertTrue(node.argparser_class is argparse.ArgumentParser)

        # root
        argparser = node.argumentparser
        self.assertIsNotNone(argparser)
        self.assertTrue(type(argparser) is argparse.ArgumentParser)

        # child
        argparser = tmpnode.argumentparser
        self.assertIsNotNone(argparser)
        self.assertTrue(hasattr(argparser,
                                "parse_args"))  # children have _SubParserAction instead of ArgumentParser

        # function
        def test(arg1=None, arg2=None):
            return arg1, arg2

        testnode = node.get_node("test")
        testnode.function = test
        self.assertEqual(test, testnode.function)
        self.assertCountEqual(globals(), testnode.function_globals)
        testnode.function_globals = {"foo": 1}
        self.assertEqual({"foo": 1}, testnode.function_globals)
        with self.assertRaises(ValueError):
            testnode.function = "string is not callable"

        # setting a new parser
        rootnode = testnode.root
        rootnode.generate_parser(None)  # generate the parser to check that it is regenerated upon setting a new parser
        self.assertEqual(type(NonExitingArgumentParser), type(rootnode.argparser_class))

        testnode.argparser_class = argparse.ArgumentParser
        self.assertEqual(type(argparse.ArgumentParser), type(rootnode.argparser_class))

    def test_add_help(self):
        node = ParserNode("test")
        self.assertEqual(False, node.add_help)  # default no ArgumentParser help (help by ArgParseDecorator)
        node.add_help = True
        self.assertEqual(True, node.add_help)
        node.generate_parser(None)

        # change add_help on a subnode and see if the parser is regenerated
        childnode = node.get_node("helptest")
        self.assertEqual(True, childnode.add_help)
        node.generate_parser(None)
        childnode.add_help = False  # should not propagate upward
        self.assertEqual(True, node.add_help)
        childnode.add_help = True  # but should propagate downward
        subchildnode = node.get_node(["helptest", "helptest2"])
        self.assertEqual(True, subchildnode.add_help)

    def test_coroutine(self):
        root = ParserNode(None)

        def test1():
            pass

        node = root.get_node("test1")
        node.function = test1
        self.assertFalse(node.coroutine)

        async def test2():
            pass

        node = root.get_node("test2")
        node.function = test2
        self.assertTrue(node.coroutine)

        class Testclass:
            async def test3(self):
                pass

        node = root.get_node("test3")
        node.function = Testclass.test3
        self.assertTrue(node.coroutine)

    def test_has_node(self):
        root = ParserNode(None)
        # add a few nodes
        root.get_node('command1')
        root.get_node(['command2', 'sub1'])
        root.get_node(['command2', 'sub2'])

        self.assertTrue(root.has_node('command1'))
        self.assertTrue(root.has_node('command2'))
        self.assertTrue(root.get_node(['command2', 'sub1']))
        self.assertTrue(root.get_node(['command2', 'sub2']))

        self.assertFalse(root.has_node('foo'))
        self.assertFalse(root.has_node(['foo', 'sub1']))
        self.assertFalse(root.has_node(['command1', 'sub1']))
        self.assertFalse(root.has_node(['command2', 'foo']))

        self.assertFalse(root.has_node([]))  # empty list

    def test_arguments(self):
        node = ParserNode("test")
        node.add_argument(Argument("a"))
        node.add_argument(Argument("b"))
        node.add_arguments([Argument("c"), Argument("d")])
        self.assertCountEqual(["a", "b", "c", "d"], node.arguments.keys())

        self.assertIsNotNone(node.get_argument("a"))
        self.assertIsNone(node.get_argument("foo"))

    def test_get_argument(self):
        node = ParserNode("test")
        node.add_argument(Argument("a"))
        node.add_argument(Argument("-b"))
        node.add_argument(Argument("--c"))
        self.assertEqual("a", node.get_argument('a').name)
        self.assertEqual("-b", node.get_argument('b').name)
        self.assertEqual("--c", node.get_argument('c').name)
        self.assertIsNone(node.get_argument('d'))

    def test_resolve_literals(self):
        self.assertEqual("", resolve_literals(""))
        self.assertEqual("foobar", resolve_literals("foobar"))

        self.assertCountEqual(["foo", "bar"], eval(resolve_literals("'foo','bar'")))
        self.assertCountEqual([1, 2, 3], eval(resolve_literals("1,2,3")))
        self.assertCountEqual(range(1, 4), eval(resolve_literals("range(1,4)")))

        # Nested Literals
        foo = Literal["foo"]
        bar = Literal["bar"]
        foobar = Literal[foo, bar]
        self.assertCountEqual(["foo", "bar"], eval(resolve_literals(str(foobar))))
        self.assertCountEqual(["foo", "bar", "baz"],
                              eval(resolve_literals("'foo', Literal['bar'], 'baz'")))

        # Literal with List
        self.assertCountEqual([1, 2, 3], eval(resolve_literals("Literal[[1, 2, 3]]")))

    def test_split_union(self):
        self.assertListEqual(["foo"], split_union("foo"))
        self.assertListEqual(["foo", "bar"], split_union("foo, bar"))
        self.assertListEqual(["bar(1,2,3)"], split_union("bar(1,2,3)"))
        self.assertListEqual(["foo", "bar(1,2,3)"], split_union("foo, bar(1,2,3)"))
        self.assertListEqual(["foo", "bar(1,2,3, baz['test'])"],
                             split_union("foo, bar(1,2,3, baz['test'])"))
        self.assertListEqual(["bar{1,2,3}", "baz['test'])"],
                             split_union("bar{1,2,3} , baz['test'])"))

    def test_fullname(self):
        self.assertEqual("str", fullname(str))
        self.assertEqual("argparsedecorator.annotations.Choices", fullname(Choices))
        self.assertEqual("argparsedecorator.annotations.Option", fullname(Option))

    def test_no_command(self):
        # no_command is a dummy placeholder command that does nothing.
        # test is included here just to get coverage to 100%
        node = ParserNode("test")
        self.assertEqual(node.function, node.no_command)
        self.assertIsNone(node.no_command(dummy="foo", arg="bar"))
