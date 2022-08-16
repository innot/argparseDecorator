#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or
#  go to <https://opensource.org/licenses/MIT>.
#
import argparse
import unittest

from argparsedecorator import NonExitingArgumentParser


class MyTestCase(unittest.TestCase):
    def test_exit(self):
        parser = NonExitingArgumentParser()
        with self.assertRaises(argparse.ArgumentError):
            parser.exit(1, "test")

    def test_error(self):
        parser = NonExitingArgumentParser()
        with self.assertRaises(argparse.ArgumentError):
            parser.error("test")


if __name__ == '__main__':
    unittest.main()
