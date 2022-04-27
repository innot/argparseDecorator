#  This file is part of the ToFiSca application.
#
#  ToFiSca is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ToFiSca is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ToFiSca.  If not, see <http://www.gnu.org/licenses/>.
#
#  Copyright (c) 2022 by Thomas Holland, thomas@innot.de
#

from __future__ import annotations

import inspect
from typing import Literal, get_type_hints

from argparsedecorator.argparse_decorator import *


class Test:

    def test(self,
             p: NumArgs[4],
             foo: Flag | ZeroOrMore[int] = None,
             multi: Literal["foo", "2", 3] = 'foo',
             f: Flag | bool = True,
             g: Flag = 21):

        foo.pop(0)
        p.pop(0)
        multi.strip()
        if f:
            pass
        if g == 42:
            pass
        pass


if __name__ == '__main__':
    t = Test()

    analyse_signature(t.test, ParserNode("test"))

    sig = inspect.signature(t.test)
    par = sig.parameters
    annot = inspect.get_annotations(t.test)
    th = get_type_hints(t.test, include_extras=True)

    foo_th = th['foo']
    foo_para = par['foo']
