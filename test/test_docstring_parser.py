import unittest

from argparsedecorator.argparse_decorator import Argument
from argparsedecorator.argparse_decorator import ParserNode


def ignore(*_):
    """Dummy function to mark all args as 'used' to avoid having PyCharm mark them as 'not used'"""
    pass


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
        ignore(foo)

        node = ParserNode("test")
        arg = Argument('foo')
        node.add_argument(arg)

        node.analyse_docstring(self.test_simple_argument)
        self.assertFalse(node.description)
        self.assertEqual("bar", node.arguments['foo'].help)

    def test_multi_arguments(self, foo=None, bar=None):
        """
        Multiple arguments
        :param foo: bar:test
        :param bar: baz:test
        :"""
        ignore(foo, bar)

        node = ParserNode("test")
        foo = Argument('foo')
        bar = Argument('bar')
        node.add_arguments([foo, bar])

        node.analyse_docstring(self.test_multi_arguments)
        self.assertTrue(node.description)
        self.assertEqual("bar:test", node.arguments['foo'].help)
        self.assertEqual("baz:test", node.arguments['bar'].help)

    def test_alias(self):
        """
        :alias foo: --foobar, -f
        :alias foo: --baz
        :"""

        node = ParserNode("test")
        foo = Argument('--foo')
        node.add_argument(foo)

        node.analyse_docstring(self.test_alias)
        self.assertEqual(['--foobar', '-f', '--baz'], node.arguments['--foo'].alias)

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

        node = ParserNode("test")
        m1 = Argument('m1')
        m1.nargs = 1
        node.add_argument(m1)
        with self.assertRaises(ValueError):
            node.analyse_docstring(self.test_metavar)


if __name__ == '__main__':
    unittest.main()
