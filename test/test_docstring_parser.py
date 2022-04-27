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


if __name__ == '__main__':
    unittest.main()
