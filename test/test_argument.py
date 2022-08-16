import argparse
import unittest

from argparsedecorator.argparse_decorator import Argument


class MyTestCase(unittest.TestCase):
    def test_properties(self):
        arg = Argument("test")
        self.assertEqual("test", arg.name)
        arg.name = "--foo"
        self.assertEqual("--foo", arg.name)

        with self.assertRaises(ValueError):
            arg.name = "1foobar"

    def test_alias(self):
        arg = Argument("--alias")
        self.assertFalse(arg.alias)
        arg.add_alias('--foo')
        self.assertEqual(['--foo'], arg.alias)
        arg.add_alias('-bar')
        self.assertEqual(['--foo', '-bar'], arg.alias)
        with self.assertRaises(ValueError):
            arg.add_alias('baz')  # does not start with '-'
        self.assertEqual(["--alias", "--foo", "-bar"], arg.get_command_line()[0])
        arg = Argument("notflag")
        with self.assertRaises(ValueError):
            arg.add_alias("--notflag")

    def test_action(self):
        arg = Argument("action")
        arg.action = "store_true"
        self.assertEqual("store_true", arg.get_command_line()[1]["action"])

        try:
            arg = Argument("action")
            arg.action = argparse.BooleanOptionalAction
            self.assertEqual(argparse.BooleanOptionalAction, arg.get_command_line()[1]["action"])
        except AttributeError:
            # argparse.BooleanOptionalAction only in python 3.9 +
            pass

        arg = Argument("action")
        arg.action = "store_true"
        with self.assertRaises(ValueError):
            arg.action = "store_false"  # already set to Boolean
        with self.assertRaises(TypeError):
            Argument("action").action = 42

    def test_nargs(self):
        arg = Argument("nargs")
        arg.nargs = 10
        self.assertEqual(10, arg.get_command_line()[1]["nargs"])

        for s in ['?', '*', '+']:
            arg = Argument("nargs")
            arg.nargs = s
            self.assertEqual(s, arg.get_command_line()[1]["nargs"])

        with self.assertRaises(ValueError):
            Argument("nargs").nargs = 0
        with self.assertRaises(ValueError):
            Argument("nargs").nargs = "foo"
        with self.assertRaises(ValueError):
            Argument("nargs").nargs = 4.3
        with self.assertRaises(ValueError):
            arg = Argument("nargs")
            arg.nargs = '?'
            arg.nargs = 2

    def test_type(self):
        arg = Argument("type")
        arg.type = "int"
        self.assertEqual(int, arg.type)
        self.assertEqual(int, arg.get_command_line()[1]["type"])

        arg = Argument("type")
        arg.type = float
        self.assertEqual(float, arg.get_command_line()[1]["type"])

        arg = Argument("type", globals())
        arg.type = "argparse.FileType('w')"
        self.assertEqual(type(argparse.FileType('w')), type(arg.get_command_line()[1]['type']))

        arg = Argument("type")
        with self.assertRaises(ValueError):
            arg.type = 42
        with self.assertRaises(ValueError):
            arg.type = int
            arg.type = float

    def test_const(self):
        arg = Argument("const")
        arg.const = "foobar"
        self.assertEqual("foobar", arg.const)
        with self.assertRaises(ValueError):
            arg.const = 123

    def test_default(self):
        arg = Argument("default")
        arg.default = "foobar"
        self.assertEqual("foobar", arg.default)
        with self.assertRaises(ValueError):
            arg.default = 123

    def test_choices(self):
        arg = Argument("choices")
        arg.choices = "10, 20, 30"
        self.assertEqual((10, 20, 30), arg.get_command_line()[1]["choices"])

        arg = Argument("choices")
        arg.choices = "'foo', 'bar', 42"
        self.assertEqual(('foo', 'bar', 42), arg.get_command_line()[1]["choices"])

        arg = Argument("choices")
        arg.choices = "range(1,4)"
        self.assertEqual(range(1, 4), arg.get_command_line()[1]["choices"])

        arg = Argument("choices")
        arg.choices = range(2, 5)
        self.assertEqual(range(2, 5), arg.get_command_line()[1]["choices"])

        arg = Argument("choices")
        with self.assertRaises(ValueError):
            arg.choices = "10"
        with self.assertRaises(ValueError):
            arg.choices = "foo$&bar"
        arg.choices = "1,2,3"
        with self.assertRaises(ValueError):
            arg.choices = "'a','b','c'"

    def test_required(self):
        arg = Argument("required")
        arg.required = True
        self.assertTrue(arg.get_command_line()[1]["required"])
        arg.required = False  # is default
        self.assertFalse("required" in arg.get_command_line()[1])
        with self.assertRaises(ValueError):
            arg.required = 42

    def test_help(self):
        arg = Argument("help")
        arg.help = "foobar baz"
        self.assertEqual("foobar baz", arg.get_command_line()[1]["help"])
        arg.help = 123
        self.assertEqual("123", arg.help)

    def test_metavar(self):
        arg = Argument("metavar")
        arg.metavar = "foo"
        self.assertEqual("foo", arg.get_command_line()[1]["metavar"])

        arg = Argument("metavar")
        arg.nargs = 3
        arg.metavar = "foo, bar, baz"
        _, kwargs = arg.get_command_line()
        self.assertEqual(("foo", "bar", "baz"), arg.get_command_line()[1]["metavar"])

        with self.assertRaises(ValueError):
            arg.metavar = "foo, bar"  # missing metavar for the third argument

    def test_positional(self):
        arg = Argument("tests")
        self.assertTrue(arg.positional)
        self.assertFalse(arg.optional)

        arg = Argument("--tests")
        self.assertTrue(arg.optional)
        self.assertFalse(arg.positional)

    def test_dest(self):
        arg = Argument("dest")
        self.assertIsNone(arg.dest)

        arg = Argument("--option")
        arg.add_alias("-o")
        _, kwargs = arg.get_command_line()
        self.assertEqual("option", arg.get_command_line()[1]["dest"])

        with self.assertRaises(NotImplementedError):
            arg.dest = "foobar"

    def test_argument_from_args(self):

        arg = Argument.argument_from_args("foo", action="action", nargs=1, const="const", default="default",
                                          type=str, choices=("1", "2"), required=True, help="help",
                                          metavar="metavar")
        self.assertEqual("foo", arg.name)
        self.assertEqual("action", arg.action)
        self.assertEqual(1, arg.nargs)
        self.assertEqual("const", arg.const)
        self.assertEqual("default", arg.default)
        self.assertTrue(arg.type is str)
        self.assertCountEqual(("1", "2"), arg.choices)
        self.assertTrue(arg.required)
        self.assertEqual("help", arg.help)
        self.assertEqual("metavar", arg.metavar)

        arg: Argument = Argument.argument_from_args("-f", "--foo", "--foobar")
        self.assertEqual("--foo", arg.name)
        self.assertCountEqual(["-f", "--foobar"], arg.alias)

        arg = Argument.argument_from_args("-f", "-flag")
        self.assertEqual("-f", arg.name)
        self.assertEqual(["-flag"], arg.alias)

        with self.assertRaises(ValueError):
            Argument.argument_from_args(action="foobar")  # no name
        with self.assertRaises(ValueError):
            Argument.argument_from_args("foo", "-bar")  # mix of positional and optional

    def test_str(self):
        arg = Argument.argument_from_args("--option", "-o", action="action", nargs=1, const="const", default="default",
                                          type=str, choices=("1", "2"), required=True, help="help",
                                          metavar="metavar")
        argstr = str(arg)
        self.assertTrue("option" in argstr)
        self.assertTrue("action=" in argstr)
        self.assertTrue("nargs=1" in argstr)
        self.assertTrue("const=const" in argstr)
        self.assertTrue("default=default" in argstr)
        self.assertTrue("type="
                        "" in argstr)
        self.assertTrue("choices=" in argstr)
        self.assertTrue("required=True" in argstr)
        self.assertTrue("help=" in argstr)
        self.assertTrue("metavar=" in argstr)
        self.assertTrue("dest=option" in argstr)


if __name__ == '__main__':
    unittest.main()
