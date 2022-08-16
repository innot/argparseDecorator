#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or
#  go to <https://opensource.org/licenses/MIT>.
#

import unittest

from argparsedecorator import *


class MyTestCase(unittest.TestCase):
    def test_annotations(self):
        # working hard to get to 100% coverage.

        with self.assertRaises(TypeError):
            _ = Flag()
        with self.assertRaises(TypeError):
            _ = Option()
        with self.assertRaises(TypeError):
            _ = OneOrMore()
        with self.assertRaises(TypeError):
            _ = ZeroOrMore()
        with self.assertRaises(TypeError):
            _ = ZeroOrOne()
        with self.assertRaises(TypeError):
            _ = Exactly1()
        with self.assertRaises(TypeError):
            _ = Exactly2()
        with self.assertRaises(TypeError):
            _ = Exactly3()
        with self.assertRaises(TypeError):
            _ = Exactly4()
        with self.assertRaises(TypeError):
            _ = Exactly5()
        with self.assertRaises(TypeError):
            _ = Exactly6()
        with self.assertRaises(TypeError):
            _ = Exactly7()
        with self.assertRaises(TypeError):
            _ = Exactly8()
        with self.assertRaises(TypeError):
            _ = Exactly9()
        with self.assertRaises(TypeError):
            _ = StoreAction()
        with self.assertRaises(TypeError):
            _ = StoreConstAction()
        with self.assertRaises(TypeError):
            _ = StoreTrueAction()
        with self.assertRaises(TypeError):
            _ = StoreFalseAction()
        with self.assertRaises(TypeError):
            _ = CustomAction()
        with self.assertRaises(TypeError):
            _ = AppendAction()
        with self.assertRaises(TypeError):
            _ = CountAction()
        with self.assertRaises(TypeError):
            _ = ExtendAction()
        with self.assertRaises(TypeError):
            _ = Choices()


if __name__ == '__main__':
    unittest.main()
