# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt file or go to <https://opensource.org/licenses/MIT>.

import asyncio
from argparse import ArgumentParser, Namespace
from typing import List, Union, Callable, Any, Type, Optional, Dict, Tuple

from . import OneOrMore     # for the builtin help command
from .argument import Argument
from .parsernode import ParserNode

"""

    
    .. attribute 
    ..warning::
        Be advised, if the ArguementParserBuilder is used as a static class variable like in the example above,
        then it is required to pass a reference of the class instance to the :method:'execute()'
        and :method:'execute_async()' calls. e.g.::

            class CLI:
                parser = ArgParseDecorator()
                
                @parser.command
                ...
                
                def execute(self, commandline):
                    self.parser.execute(commandline, self)

"""


class ArgParseDecorator:
    """
    Build python :class:'ArgumentParser' from decorated functions.

    It uses the signature and the annotations of the decorated class to determine all arguments
    and their types.
    It also uses the docstring to for the command description, the help strings for all arguments and
    some additional metadata that can not be expressed via annotations.


    :param helpoption:  Either 'help' to automatically create a help command, or
                        '-h' to automatically add a -h/--help argument to each command, or
                        'none' to disable any automatically generated help.
                        Defaults to 'help'
    :type helpoption:   str
    :param hyph_replace string to be replaced by '-' in command names, defaults to '__'
    :type hyph_replace  str
    :param argparser_class: Class to be used for ArgumentParser, defaults to :class:'NonExitingArgumentParser'
    :type argparser_class: :class:'argparse.ArgumentParser' or subclass thereof.
    :param kwargs:      Other arguments to be passed to the ArgumentParser, e.g. 'description' or 'allow_abbrev'
    """

    def __init__(self,
                 helpoption: Optional[str] = "help",
                 hyph_replace: str = "__",
                 argparser_class: Type[ArgumentParser] = None,
                 **kwargs):

        if helpoption == "-h" or helpoption == "help" or helpoption is None:
            self.helptype = helpoption
        else:
            raise ValueError(f"help argument may only be 'help', '-h' or None. Was {str(helpoption)}")

        self.hyphen_replacement = hyph_replace

        self.rootnode: ParserNode = ParserNode(None, **kwargs)
        if argparser_class:
            if isinstance(argparser_class, ArgumentParser):
                self.rootnode.argparser_class = argparser_class
            else:
                raise TypeError("argparser_class not a subclass of ArgumentParser")

        if helpoption == "help":
            # add the help command as a node to the tree
            node: ParserNode = self.rootnode.get_node("help")
            node.function = self.help

        if helpoption == "None":
            self.rootnode.add_help = False

    def help(self, command: OneOrMore[str]) -> None:
        """
        Prints help for the given command.
        :param command: Name of the command to get help for
        :type command: list
        """
        if self.rootnode.has_node(command):
            node = self.rootnode.get_node(command)
        else:
            node = self.rootnode
        argparser = node.argumentparser
        argparser.print_help()

    def build(self):
        # now generate all Argumentparsers
        self.rootnode.generate_parser(None)
        self._parser: Union[ArgumentParser, None] = None

    def execute(self, commandline: Union[str, List[str]], base=None) -> Any:
        """
        Parse a command line and execute it.

        The 'base' should be supplied if the method implementing the command is a bound method,
        i.e. having 'self' as the first argument. It is not required if the command is implemented
        with a function (unbound) or an inner function (already bound).

        :param commandline: A string with a command and its arguments (e.g. 'command --flag argument') or
                            a list with the command name and its arguments as items
                            (e.g. ['command', '--flag', 'argument'])
        :type commandline: String or list of stings
        :param base: an object that is passed to commands as the 'self' argument, defaults to 'None'
        :type base: the object the commands are bound to.
        :return: anything the command function/method returns.
        """
        argparser: ArgumentParser = self.argumentparser
        named_args = argparser.parse_args(commandline.split())
        func: Callable = named_args.func
        node: ParserNode = named_args.node
        args, kwargs = get_arguments_from_namespace(named_args, node)

        if node.bound_method and func != self.help:
            result = func(base, *args, **kwargs)
        else:
            result = func(*args, **kwargs)

        return result

    async def execute_async(self, commandline: str) -> object:
        argparser: ArgumentParser = self.argumentparser
        args = argparser.parse_args(commandline.split())
        func = args.func
        if asyncio.iscoroutinefunction(func):
            # todo handle unbound methods / functions
            result = await func(args)
        else:
            result = func(args)

        return result

    @property
    def argumentparser(self) -> ArgumentParser:
        """
        The generated :class:'AttributeParser' object.
        The property is read only
        """
        argparser: ArgumentParser = self.rootnode.argumentparser
        if argparser is None:
            self.build()
            argparser = self.rootnode.argumentparser

        return argparser

    #    @doublewrap
    #    def command(self, f: Callable):
    def command(self, *args: Union[str, Callable], **kwargs: Any) -> Callable:
        """
        Decorator to mark a method as an executable command.
        :param args:
        :param kwargs:
        :return:
        """

        #        @functools.wraps(f)
        def decorator(func: Callable) -> Callable:
            node: ParserNode = self._node_from_func(func)
            if not (len(args) == 1 and len(kwargs) == 0 and callable(args[0])):
                # save arguments of decorator
                node.parser_args = (args, kwargs)
            node.function = func
            return func

        # if command is used without (), then args is the decorated function and
        # we need to call the decorator ourself.
        # otherwise, i.e. command(...) is used, the args contain a tuble of all arguments
        # and we need to return the decorator function to be called later.
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return decorator(args[0])
        else:
            return decorator

    def add_argument(self, *args: str, **kwargs: Any) -> Callable:

        def decorator(func) -> Callable:
            node: ParserNode = self._node_from_func(func)
            arg = Argument.argument_from_args(*args, **kwargs)
            node.add_argument(arg)
            return func

        return decorator

    def _node_from_func(self, func: Callable) -> ParserNode:
        """
        Get the :class:'ParserNode' for the given function or method.
        If the Node does not exist it will be created.
        :param func: a callable
        :return: a ParserNode
        """
        fullcmd = func.__name__
        fullcmd = fullcmd.replace(self.hyphen_replacement, '-')
        parts = fullcmd.split('_')
        node: ParserNode = self.rootnode.get_node(parts)
        return node


def get_arguments_from_namespace(args: Namespace, node: ParserNode) -> Tuple[List[str], Dict[str, Any]]:
    """Convert the Namespace object returned by parse_args() into  *args, **kwargs objects."""
    all_args = vars(args)

    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

    # first get all positional args in the order they were added to this node
    for name in node.positional_args:
        if name in all_args:
            arg = all_args.pop(name)
            args.append(arg)

    # and now extract all known keyword args. This ensures that any arg that entered the namespace,
    # e.g. our 'func' argument with the callback, do not get passed to the callback.
    for name in node.optional_args:
        if name in all_args:
            arg = all_args.pop(name)
            kwargs[name] = arg

    return args, kwargs
