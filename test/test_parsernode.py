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
from argparsedecorator.parsernode import resolve_literals, split_union


def ignore(*_):
    """Dummy function to mark all args as 'used' to avoid having PyCharm mark them as 'not used'"""
    pass


class MyTestCase(unittest.TestCase):

    def test_properies(self):
        node = ParserNode("test")
        self.assertEqual("test", node.title)
        with self.assertRaises(AttributeError):
            node.title = "foobar"  # read only property
            self.fail()

        tmpnode = node
        for i in range(5):
            tmpnode = tmpnode.get_node(f"{i}")
        self.assertEqual(node, tmpnode.root)
        with self.assertRaises(AttributeError):
            node.root = tmpnode  # read only property
            self.fail()

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
        self.assertTrue(hasattr(argparser, "parse_args"))  # children have _SubParserAction instead of ArgumentParser

        # function
        def test(arg1=None, arg2=None):
            ignore(arg1, arg2)

        testnode = node.get_node("test")
        testnode.function = test
        self.assertEqual(test, testnode.function)
        self.assertCountEqual(globals(), testnode.function_globals)
        testnode.function_globals = {"foo": 1}
        self.assertEqual({"foo": 1}, testnode.function_globals)

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

    def test_arguments(self):
        node = ParserNode("test")
        node.add_argument(Argument("a"))
        node.add_argument(Argument("b"))
        node.add_arguments([Argument("c"), Argument("d")])
        self.assertCountEqual(["a", "b", "c", "d"], node.arguments.keys())

        self.assertIsNotNone(node.get_argument("a"))
        self.assertIsNone(node.get_argument("foo"))

    def test_resolve_literals(self):
        self.assertEqual("", resolve_literals(""))
        self.assertEqual("foobar", resolve_literals("foobar"))

        self.assertCountEqual(["foo", "bar"], eval(resolve_literals("'foo','bar'")))
        self.assertCountEqual([1, 2, 3], eval(resolve_literals("1,2,3")))
        self.assertCountEqual(range(1, 4), eval(resolve_literals("range(1,4)")))

        foo = Literal["foo"]
        bar = Literal["bar"]
        foobar = Literal[foo, bar]
        self.assertCountEqual(["foo", "bar"], eval(resolve_literals(str(foobar)), globals()))
        self.assertCountEqual(["foo", "bar", "baz"], eval(resolve_literals("'foo', Literal['bar'], 'baz'")))

    def test_split_union(self):
        self.assertListEqual(["foo"], split_union("foo"))
        self.assertListEqual(["foo", "bar"], split_union("foo, bar"))
        self.assertListEqual(["bar(1,2,3)"], split_union("bar(1,2,3)"))
        self.assertListEqual(["foo", "bar(1,2,3)"], split_union("foo, bar(1,2,3)"))
        self.assertListEqual(["foo", "bar(1,2,3, baz['test'])"], split_union("foo, bar(1,2,3, baz['test'])"))
        self.assertListEqual(["bar{1,2,3}", "baz['test'])"], split_union("bar{1,2,3} , baz['test'])"))
