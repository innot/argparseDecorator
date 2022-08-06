#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or
#  go to <https://opensource.org/licenses/MIT>.
#
import sys

from argparsedecorator import *

# use helpoption='-h' as the "help" option does not work when parsing script arguments.
argparser = ArgParseDecorator(helpoption="-h")


@argparser.command
def sysargv(v: Flag = False):  # must be the same name as the script.
    """Sample to show script argument parsing.
    :param v: switch on verbose mode.
    :alias v: --verbose
    """
    if v:
        print("chatty mode activated")


if __name__ == "__main__":
    argparser.execute(sys.argv)
