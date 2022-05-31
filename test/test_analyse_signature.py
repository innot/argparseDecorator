from __future__ import annotations

import argparse
import unittest
from argparse import FileType
from typing import Union, Literal

from argparsedecorator.annotations import *
from argparsedecorator.argparse_decorator import Argument
from argparsedecorator.argparse_decorator import ParserNode


class MyAction(argparse.Action):
    pass


class TestSignatureParser(unittest.TestCase):

    def test_analyse_signature_simple(self):
        def test1(arg1):
            return arg1

        node = ParserNode("test")
        node.analyse_signature(test1)
        arg: Argument = node.arguments['arg1']
        self.assertEqual('arg1', arg.name)
        self.assertIsNone(arg.type)

    def test_analyse_signature_flag_option(self):
        def test(arg1: Flag = True, arg2: Option = False):
            return arg1, arg2

        node = ParserNode("test")
        node.analyse_signature(test)
        arg: Argument = node.arguments['-arg1']
        self.assertEqual("store_false", arg.action)
        arg: Argument = node.arguments['--arg2']
        self.assertEqual("store_true", arg.action)

    def test_analyse_signature_actions(self):
        def test1(arg1: Union[Exactly3[int], StoreConstAction] = 1,
                  arg2: AppendAction = "foo"):
            return arg1, arg2

        node = ParserNode("test")
        node.analyse_signature(test1)
        arg: Argument = node.arguments['arg1']
        self.assertEqual(int, arg.type)
        self.assertEqual(3, arg.nargs)
        self.assertEqual("store_const", arg.action)
        self.assertEqual(1, arg.const)

        arg: Argument = node.arguments['arg2']
        self.assertEqual("append", arg.action)

        def test2(arg1: CustomAction[MyAction]):
            return arg1

        node = ParserNode("test")
        node.function = test2  # instead of analyse_signature to make MyAction known to the node
        arg: Argument = node.arguments['arg1']
        self.assertEqual(MyAction, arg.action)

    def test_analyse_signature_choices(self):
        def test1(arg1: Choices[Literal["foo", "bar"]] = "foo"):
            return arg1

        node = ParserNode("test")
        node.analyse_signature(test1)
        arg: Argument = node.arguments['arg1']
        self.assertEqual(("foo", "bar"), arg.choices)
        self.assertEqual("foo", arg.default)

        def test2(arg1: Choices[1, 2, 3, 4] = 5):
            return arg1

        node = ParserNode("test")
        with self.assertRaises(ValueError):
            node.analyse_signature(test2)

    def test_analyse_annotation(self):
        node = ParserNode("test")
        arg = Argument("test1")
        node.analyse_annotation("", arg)
        self.assertEqual({}, arg.get_command_line()[1])
        node.analyse_annotation("int", arg)
        self.assertEqual({"type": int}, arg.get_command_line()[1])

        arg = Argument("test2")
        node.analyse_annotation("int | OneOrMore[int]", arg)
        self.assertCountEqual({"type": int, "nargs": '+'}, arg.get_command_line()[1])

        arg = Argument("test3")
        node.analyse_annotation("int | Choices[range(1,4)] | Flag", arg)
        self.assertEqual("-test3", arg.name)
        self.assertCountEqual({"type": int, "choices": range(1, 4)}, arg.get_command_line()[1])

        arg = Argument("test4")
        node.analyse_annotation("Option | CountAction", arg)
        self.assertEqual("--test4", arg.name)
        self.assertCountEqual({"action": "count"}, arg.get_command_line()[1])

        arg = Argument("test5")
        node.analyse_annotation(" Union[float, AppendAction, ZeroOrMore] ", arg)
        self.assertEqual(float, arg.type)
        self.assertEqual('*', arg.nargs)
        self.assertEqual('append', arg.action)

        # test multiple type failures
        arg = Argument("test6")
        with self.assertRaises(ValueError):
            node.analyse_annotation("Union[int, ZeroOrOne[float]]", arg)
            self.fail()

    def test_analyse_annotation_part(self):
        node = ParserNode("test")
        node.function_globals = globals()

        arg = Argument("test1")
        node.analyse_annotation_part("int", arg)
        self.assertEqual(int, arg.type)

        arg = Argument("test2")
        node.analyse_annotation_part("float", arg)
        self.assertEqual(float, arg.type)

        arg = Argument("test3")  # add globals so Argument can eval 'FileType'
        node.analyse_annotation_part("FileType('w')", arg)
        self.assertEqual(type(FileType('w')), type(arg.type))

        # Use the class.__name__ in case the annotation classes get refactored

        arg = Argument("foo1")
        node.analyse_annotation_part(Flag.__name__, arg)
        self.assertEqual("-foo1", arg.name)

        arg = Argument("foo2")
        node.analyse_annotation_part(Option.__name__, arg)
        self.assertEqual("--foo2", arg.name)

        arg = Argument("test3")
        node.analyse_annotation_part(OneOrMore.__name__, arg)
        self.assertEqual("+", arg.nargs)

        arg = Argument("test4")
        node.analyse_annotation_part(f"{OneOrMore.__name__}[]", arg)
        self.assertEqual("+", arg.nargs)
        self.assertIsNone(arg.type)

        arg = Argument("test5")
        node.analyse_annotation_part(f"{OneOrMore.__name__}[int]", arg)
        self.assertEqual("+", arg.nargs)
        self.assertEqual(int, arg.type)

        arg = Argument("test6")
        node.analyse_annotation_part(f"{ZeroOrMore.__name__}[float]", arg)
        self.assertEqual("*", arg.nargs)
        self.assertEqual(float, arg.type)

        arg = Argument("test7")
        node.analyse_annotation_part(f"{ZeroOrOne.__name__}[ascii]", arg)
        self.assertEqual("?", arg.nargs)
        self.assertEqual(ascii, arg.type)

        arg = Argument("test8_1")
        node.analyse_annotation_part(f"{Exactly1.__name__}", arg)
        self.assertEqual(1, arg.nargs)
        self.assertIsNone(arg.type)
        arg = Argument("test8_2")
        node.analyse_annotation_part(f"{Exactly2.__name__}[int]", arg)
        self.assertEqual(2, arg.nargs)
        self.assertEqual(int, arg.type)
        arg = Argument("test8_3")
        node.analyse_annotation_part(f"{Exactly3.__name__}[float]", arg)
        self.assertEqual(3, arg.nargs)
        self.assertEqual(float, arg.type)
        arg = Argument("test8_4")
        node.analyse_annotation_part(f"{Exactly4.__name__}[]", arg)
        self.assertEqual(4, arg.nargs)
        self.assertIsNone(arg.type)
        arg = Argument("test8_5")
        node.analyse_annotation_part(f"{Exactly5.__name__}", arg)
        self.assertEqual(5, arg.nargs)
        arg = Argument("test8_6")
        node.analyse_annotation_part(f"{Exactly6.__name__}[]", arg)
        self.assertEqual(6, arg.nargs)
        arg = Argument("test8_7")
        node.analyse_annotation_part(f"{Exactly7.__name__}[]", arg)
        self.assertEqual(7, arg.nargs)
        arg = Argument("test8_8")
        node.analyse_annotation_part(f"{Exactly8.__name__}[]", arg)
        self.assertEqual(8, arg.nargs)
        arg = Argument("test8_9")
        node.analyse_annotation_part(f"{Exactly9.__name__}[]", arg)
        self.assertEqual(9, arg.nargs)

        arg = Argument("test10")
        node.analyse_annotation_part("Choices[Literal['foo', 'bar']]", arg)
        self.assertCountEqual(['foo', 'bar'], arg.choices)

        arg = Argument("test11")
        node.analyse_annotation_part("Choices[10, 20, 30]", arg)
        self.assertCountEqual([10, 20, 30], arg.choices)

        arg = Argument("test12")
        node.analyse_annotation_part("Choices[range(1,4)]", arg)
        self.assertEqual(range(1, 4), arg.choices)

        arg = Argument("test13")
        node.analyse_annotation_part(StoreAction.__name__, arg)
        self.assertEqual("store", arg.action)

        arg = Argument("test14")
        node.analyse_annotation_part(StoreConstAction.__name__, arg)
        self.assertEqual("store_const", arg.action)

        arg = Argument("test15")
        node.analyse_annotation_part(StoreTrueAction.__name__, arg)
        self.assertEqual("store_true", arg.action)

        arg = Argument("test16")
        node.analyse_annotation_part(StoreFalseAction.__name__, arg)
        self.assertEqual("store_false", arg.action)

        arg = Argument("test17")
        node.analyse_annotation_part(AppendAction.__name__, arg)
        self.assertEqual("append", arg.action)

        #        arg = Argument("test18")
        #        node.analyse_annotation_part(AppendConstAction.__name__, arg)
        #        self.assertEqual("append_const", arg.action)

        arg = Argument("test19")
        node.analyse_annotation_part(CountAction.__name__, arg)
        self.assertEqual("count", arg.action)
        self.assertIsNone(arg.type)
        # must be None because argparse implies this and does not like explicit type.

        arg = Argument("test20")
        node.analyse_annotation_part(ExtendAction.__name__, arg)
        self.assertEqual("extend", arg.action)

        arg = Argument("test21")
        node.analyse_annotation_part(f"{CustomAction.__name__}[MyAction]", arg)
        self.assertEqual(MyAction, arg.action)


if __name__ == '__main__':
    unittest.main()
