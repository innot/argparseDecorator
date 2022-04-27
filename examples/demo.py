# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt file or go to <https://opensource.org/licenses/MIT>.

from __future__ import annotations

import argparse
import time
from typing import Union

from argparsedecorator import *


class DemoCLI:
    desc = "A small demo app for the ArgParseDecorator library"
    parser = ArgParseDecorator(description=desc)

    def __init__(self):
        # This is important as the ArgParseDecorator is a class variable and does not
        # know 'self'. We need to tell it what self is so it can be passed on to the
        # decorated command functions.
        self.parser.caller = self
        self.switch = False

    # simple command without par
    @parser.command
    def exit(self) -> str:
        """Exit the CLI."""
        print("CLI stopping")
        return "exit"

    # simple command with a parameter
    @parser.command()
    def echo(self, text: ZeroOrMore[str]):
        """
        Print the given text.
        :param text: the text to be printed
        """
        txt = " ".join(text)
        print(txt)

    # multiple arguments
    @parser.command()
    def multi(self, text: ZeroOrMore[str], num: Union[Flag, int] = 2):
        """
        Print the given text multiple times.
        :param text: the text to be repeated
        :param num: number of times to repeat the text, default is 2
        :alias num: -n
        """
        txt = " ".join(text)
        for i in range(0, num):
            print(txt)

    # subcommands
    @parser.command
    def switch(self):
        """
        Set the switch to on or off. If called without parameters then show the current switch position.
        """
        if self.switch:
            print("Switch is on")
        else:
            print("Switch is off")

    @parser.command()
    def switch_on(self, duration: Union[Option, int]):
        """
        Switch on
        :param duration: On time in milliseconds
        :alias duration: -d
        """
        if duration:
            print(f"switching on for {duration}ms")
            time.sleep(duration / 1000)
            print(f"switching off")
            self.switch = False
        else:
            print(f"switching on")
            self.switch = True

    @parser.command()
    def switch_off(self):
        """
        switch off
        """
        print("switching off")
        self.switch = False

    # argument in decorator
    @parser.command
    @parser.add_argument("--foo", "-f", action="store_true", help="The foo flag")
    @parser.add_argument("--bar", "-b", type=int, help="The bar value")
    def test__arg(self, *args, **kwargs):
        """
        Test decorator argument.
        """
        print(f"test-arg called with flag foo {kwargs['foo']} and a bar value of {kwargs['bar']}")

    def execute(self, commandline: str) -> object:
        # execute the command line, giving the static ArgParseDecorator a reference to this instance.
        return self.parser.execute(commandline, base=self)


if __name__ == "__main__":
    cli = DemoCLI()
    while True:
        cmd = input("# ")
        try:
            result = cli.execute(cmd)
            if result == "exit":
                break
        except argparse.ArgumentError as exc:
            # ignore invalid commands
            pass
