import argparse
import unittest

from argparsedecorator.argparse_decorator import Argument
from argparsedecorator.argparse_decorator import ParserNode


class MyTestCase(unittest.TestCase):
    def test_description_only(self):
        """Just a Description"""
        node = ParserNode("test")
        node.analyse_docstring(self.test_description_only)
        self.assertEqual(self.test_description_only.__doc__, node.description)
        self.assertFalse(node.arguments)

    def test_multiline_description(self):
        """
        foo
        bar
        """
        node = ParserNode("test")
        node.analyse_docstring(self.test_multiline_description)
        self.assertEqual("foo bar", node.description)

    def test_simple_argument(self, foo=None):
        """:param foo: bar"""
        _ = foo

        node = ParserNode("test")
        arg = Argument('foo')
        node.add_argument(arg)

        node.analyse_docstring(self.test_simple_argument)
        self.assertFalse(node.description)
        self.assertEqual("bar", node.arguments['foo'].help)

        # test wrong name
        # noinspection PyUnresolvedReferences
        def test_func():
            """:param bar: baz"""
            pass

        with self.assertRaises(NameError):
            node.analyse_docstring(test_func)

        # test empty description
        def test_func_2(dummy, dummy2):
            """
            :param dummy:
            :param dummy2
            """
            return dummy, dummy2  # not used, just to avoid type checker warning

        node.add_argument(Argument("dummy"))
        node.add_argument(Argument("dummy2"))
        node.analyse_docstring(test_func_2)
        self.assertEqual("", node.arguments['dummy'].help)
        node.analyse_docstring(test_func_2)
        self.assertEqual("", node.arguments['dummy2'].help)

    def test_multi_arguments(self, foo=None, bar=None):
        """
        Multiple arguments
        :param foo: bar:test
        :param bar: baz:test
        :"""
        _ = (foo, bar)  # just to make type checker not complaint about unused value

        node = ParserNode("test")
        foo = Argument('foo')
        bar = Argument('bar')
        node.add_arguments([foo, bar])

        node.analyse_docstring(self.test_multi_arguments)
        self.assertTrue(node.description)
        self.assertEqual("bar:test", node.arguments['foo'].help)
        self.assertEqual("baz:test", node.arguments['bar'].help)

    def test_argument_suppress(self, foo=None):
        """
        :param foo: SUPPRESS this argument
        """
        _ = foo  # just to make type checker not complaint about unused value

        node = ParserNode("test")
        foo = Argument('foo')
        node.add_argument(foo)

        node.analyse_docstring(self.test_argument_suppress)
        self.assertEqual(argparse.SUPPRESS, node.arguments['foo'].help)

    def test_alias(self):
        """
        :alias foo: --foobar, -f
        :alias foo: --baz
        """

        node = ParserNode("test")
        foo = Argument('--foo')
        node.add_argument(foo)

        node.analyse_docstring(self.test_alias)
        self.assertEqual(['--foobar', '-f', '--baz'], node.arguments['--foo'].alias)

        # test failure
        def aliasfail1():
            """:alias foo:"""
            pass

        with self.assertRaises(ValueError):
            node.analyse_docstring(aliasfail1)

        def aliasfail2():
            """:alias foo"""
            pass

        with self.assertRaises(ValueError):
            node.analyse_docstring(aliasfail2)

        def aliasfail3():
            """:alias noarg: -n"""
            pass

        with self.assertRaises(NameError):
            node.analyse_docstring(aliasfail3)

    def test_choices(self):
        """
        :choices c1: 'foo', 'bar', 'baz'
        :choices c2: 1, 2, 3
        :choices c3: range(1,4)
        """
        node = ParserNode("test")
        c1 = Argument('c1')
        node.add_argument(c1)
        c2 = Argument('c2')
        node.add_argument(c2)
        c3 = Argument('c3')
        node.add_argument(c3)

        node.analyse_docstring(self.test_choices)
        self.assertListEqual(['foo', 'bar', 'baz'], list(node.arguments['c1'].choices))
        self.assertListEqual([1, 2, 3], list(node.arguments['c2'].choices))
        self.assertEqual(range(1, 4), node.arguments['c3'].choices)

        # test failures
        def choicesfail():
            """:choices c4:"""
            pass

        node.add_argument(Argument("c4"))
        with self.assertRaises(ValueError):
            node.analyse_docstring(choicesfail)

        def choicesfail2():
            """:choices noarg: 1, 2, 3, 4"""
            pass

        with self.assertRaises(NameError):
            node.analyse_docstring(choicesfail2)

        def choicesfail3():
            """:choices c5: 2+2"""
            pass

        node.add_argument(Argument("c5"))
        with self.assertRaises(ValueError):
            node.analyse_docstring(choicesfail3)

    def test_metavar(self):
        """
        :metavar m1: 'foo', 'bar', 'baz'
        """
        node = ParserNode("test")
        m1 = Argument('m1')
        m1.nargs = 3
        node.add_argument(m1)

        node.analyse_docstring(self.test_metavar)
        self.assertListEqual(['foo', 'bar', 'baz'], list(node.arguments['m1'].metavar))

        # test failures
        def metavarfail():
            """:metavar m2:"""
            pass

        node.add_argument(Argument("m2"))
        with self.assertRaises(ValueError):
            node.analyse_docstring(metavarfail)

        def metavarfail2():
            """:metavar foobar: foo, bar"""
            pass

        with self.assertRaises(NameError):
            node.analyse_docstring(metavarfail2)

    def test_str(self):
        node = ParserNode("root")
        node.add_argument(Argument("arg1"))
        sc1 = node.get_node(["child1", "subchild1"])
        sc1.add_argument(Argument("sc1"))
        sc2 = node.get_node(["child2", "subchild2"])
        sc2.add_argument(Argument("sc2"))

        strrepr = str(node)
        self.assertTrue("root" in strrepr)
        self.assertTrue("child1" in strrepr)
        self.assertTrue("child2" in strrepr)
        self.assertTrue("subchild1" in strrepr)
        self.assertTrue("subchild2" in strrepr)


if __name__ == '__main__':
    unittest.main()
