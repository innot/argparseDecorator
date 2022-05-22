# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file or
# go to <https://opensource.org/licenses/MIT>.

"""
    This module contains one Class, the :class:`.ArgParseDecorator`.

    It is the main Class for the *argparseDecorator* library and usually the only one needed
    to use the library.

    It contains the :meth:`.command` decorator to mark functions/methods as commands and the
    :meth:`.execute`/:meth:`.execute_async` methods to execute a command line string.

    Internally it generates a :class:`~.parsernode.ParserNode` element for each decorated
    function or method, defining the command and all associated data, and organises them in a tree
    of commands and sub-commands.
    The nodes have a reference to the decorated function which is used later to execute the command.

    When :meth:`execute` is called the *ParserNode* tree is converted to an
    `ArgumentParser <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_
    object, which is then used to analyse the given command line.
    The result from the
    `ArgumentParser.parse_args() <https://docs.python.org/3/library/argparse.html#the-parse-args-method>`_
    call is then converted to arguments of the decorated function and finally the function
    is called with the arguments and its (optional) return value is passed on to the caller of
    :meth:`.execute`.

    The only other public method of this Class is the :meth:`~ArgParseDecorator.add_argument`
    decorator, which can be used to pass arguments directly to the underlying *ArgumentParser* in
    case some special functionality of the argparse library is needed.
"""

import asyncio
from argparse import ArgumentParser, Namespace
from typing import List, Union, Callable, Any, Type, Optional, Dict, Tuple

from .annotations import ZeroOrMore  # for the builtin help command
from .argument import Argument
from .parsernode import ParserNode


class ArgParseDecorator:
    """
    Build python
    `ArgumentParser <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_
    from decorated functions.

    It uses the signature and the annotations of the decorated class to determine all arguments
    and their types.
    It also uses the docstring for the command description, the help strings for all arguments
    and some additional metadata that can not be expressed via annotations.

    :param helpoption: Either

        *  *"help"* to automatically create a help command, or
        *  *"-h"* to automatically add a *-h/--help* argument to each command (argparse library default), or
        *  *None* to disable any automatically generated help.

        Defaults to *"help"*
    :param hyph_replace: string to be replaced by *-* in command names,
        defaults to *__* (two underscores)
    :param argparser_class: Class to be used for ArgumentParser,
        defaults to :class:`~argparsedecorator.nonexiting_argumentparser.NonExitingArgumentParser`
    :type argparser_class: `ArgumentParser <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_
        or subclass thereof.
    :param kwargs: Other arguments to be passed to the ArgumentParser,
        e.g. *descriptio* or *allow_abbrev*
    """

    def __init__(self,
                 helpoption: Optional[str] = "help",
                 hyph_replace: str = "__",
                 argparser_class: Type[ArgumentParser] = None,
                 **kwargs):

        if helpoption == "-h" or helpoption == "help" or helpoption is None:
            self.helptype = helpoption
        else:
            raise ValueError(
                f"help argument may only be 'help', '-h' or None. Was {str(helpoption)}")

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

    @property
    def argumentparser(self) -> ArgumentParser:
        """
        The generated
        `ArgumentParser <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_
        object.

        This property is read only
        """
        argparser: ArgumentParser = self.rootnode.argumentparser
        if argparser is None:
            self.rootnode.generate_parser(None)
            argparser = self.rootnode.argumentparser

        return argparser

    #    @doublewrap
    #    def command(self, f: Callable):
    def command(self, *args: Union[str, Callable], **kwargs: Any) -> Callable:
        """
        Decorator to mark a method as an executable command.

        This takes the name of the decorated function and adds it to the internal command list.
        It also analyses the signature and the docstring of the decorated function to gather
        information about its arguments.

        :param args: Optional arguments that are passed directly to the
            `ArgumentParser.add_subparser() <https://docs.python.org/3/library/argparse.html#sub-commands>`_
            method.
        :param kwargs: Optional keyword arguments that are passed directly to the
            `ArgumentParser.add_subparser() <https://docs.python.org/3/library/argparse.html#sub-commands>`_
            method.
        :return: The decorator function
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
        return decorator

    def add_argument(self, *args: str, **kwargs: Any) -> Callable:
        r"""
        Decorator to add an argument to the command.

        This is an alternative way to add arguments to a function.
        While its use is usually not required there might be some situations where
        the function signature and its annotations are not sufficient to accurately
        describe an argument. In this case the :meth:`.add_argument` decorator can be used.
        Any pararmeter to this decorator is passed directly to
        `argparse.add_argument() <https://docs.python.org/3/library/argparse.html#the-add-argument-method>`_

        The decorated function must have an argument of the same name or use \*args and \*\*kwargs
        arguments to retrieve the value of these arguments.

        Example::

            @parser.command
            @parser.add_argument('dest_file', type=argparse.FileType('r', encoding='latin-1'))
            @parser.add_argument('--foo', '-f')
            def write(*args, **kwargs):
                dest_file = args[0]
                foo = kwargs['foo']

        :param args: Optional arguments that are passed directly to the
            ArgumentParser.add_argument() method.
        :param kwargs: Optional keyword arguments that are passed directly to the
            ArgumentParser.add_argument() method.
        :return: The decorator function

        """

        def decorator(func) -> Callable:
            node: ParserNode = self._node_from_func(func)
            arg = Argument.argument_from_args(*args, **kwargs)
            node.add_argument(arg)
            return func

        return decorator

    def execute(self, commandline: str, base=None) -> Any:
        """
        Parse a command line and execute it.

        .. note::

            The *base* must be supplied if the method implementing the command is a bound method,
            i.e. having *self* as the first argument. It is not required if the command is
            implemented as a function (unbound) or an inner function (already bound).

        :param commandline: A string with a command and arguments (e.g. *"command --flag arg"*)
        :param base: an object that is passed to commands as the *self* argument,
            defaults to *None*
        :return: anything the command function/method returns.
        :raises ValueError: if the command function requires a *self* parameter, but no *base*
            argument was supplied.
        :raises SyntaxError: if the given command line contains errors.
        """
        argparser: ArgumentParser = self.argumentparser
        named_args = argparser.parse_args(commandline.split())
        func: Callable = named_args.func
        node: ParserNode = named_args.node
        args, kwargs = get_arguments_from_namespace(named_args, node)

        if node.bound_method and func != self.help:
            if base is None:
                # do not pass None as self - this will propably cause errors further
                # down. Fail cleanly instead.
                raise ValueError(
                    f"Method {func.__name__} is a bound method and requires the "
                    f"'base' (self) parameter to be set.")
            result = func(base, *args, **kwargs)
        else:
            result = func(*args, **kwargs)

        return result

    async def execute_async(self, commandline: str) -> object:
        """
        Not yet working, do not use.

        :param commandline:
        :return:
        """
        argparser: ArgumentParser = self.argumentparser
        args = argparser.parse_args(commandline.split())
        func = args.func
        if asyncio.iscoroutinefunction(func):
            # todo handle unbound methods / functions
            result = await func(args)
        else:
            result = func(args)

        return result

    def help(self, command: ZeroOrMore[str]) -> None:
        """
        Prints help for the given command.

        :param command: Name of the command to get help for
        :type command: list
        """
        node = self.rootnode
        if command:
            if self.rootnode.has_node(command):
                node = self.rootnode.get_node(command)
        argparser = node.argumentparser
        argparser.print_help()

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


def get_arguments_from_namespace(
        args: Namespace,
        node: ParserNode) -> Tuple[List[str], Dict[str, Any]]:
    r"""
    Convert the Namespace object returned by parse_args() into  \*args, \**kwargs objects.
    """
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
