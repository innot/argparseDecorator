# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file or go to <https://opensource.org/licenses/MIT>.

from __future__ import annotations

import argparse
import time
from typing import Union

from argparsedecorator import *


class DemoCLI:
    desc = "A small demo app for the ArgParseDecorator library"
    cli = ArgParseDecorator(description=desc)

    def __init__(self):
        self.switch = False

    # simple command without par
    @cli.command
    def exit(self) -> str:
        """Exit the CLI."""
        confirm = input("Confirm you want to stop the CLI? ([y]es / [n]o): ")
        if confirm.startswith('y'):
            print("CLI stopping")
            return "exit"
        print("ok, not exiting")

    # simple command with a parameter
    @cli.command()
    def echo(self, text: ZeroOrMore[str]) -> None:
        """
        Print the given text.
        :param text: the text to be printed
        """
        txt = " ".join(text)
        print(txt)

    # multiple arguments
    @cli.command()
    def multi(self, text: ZeroOrMore[str], num: Union[Flag, int] = 2) -> None:
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
    @cli.command
    def switch(self):
        """
        Set the switch to on or off. If called without parameters then show the current switch position.
        """
        if self.switch:
            print("Switch is on")
        else:
            print("Switch is off")

    @cli.command()
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

    @cli.command()
    def switch_off(self):
        """
        switch off
        """
        print("switching off")
        self.switch = False

    # argument in decorator
    @cli.command
    @cli.add_argument("--foo", "-f", action="store_true", help="The foo flag")
    @cli.add_argument("--bar", "-b", type=int, help="The bar value (integer)")
    def test__arg(self, **kwargs):
        """
        Test decorator argument.
        """
        print(f"test-arg called with flag foo {kwargs['foo']} and a bar value of {kwargs['bar']}")

    def execute(self, commandline: str) -> object:
        # execute the command line, giving the static ArgParseDecorator a reference to this instance.
        return self.cli.execute(commandline, base=self)


if __name__ == "__main__":
    cli = DemoCLI()
    running = True
    while running:
        cmd = input("\n# ")
        try:
            result = cli.execute(cmd)
            if result == "exit":
                running = False
        except argparse.ArgumentError as exc:
            print("Exception")
            pass
    print("simple-cli.py has finished")
