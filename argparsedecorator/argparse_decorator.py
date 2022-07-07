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

    When :meth:`.execute` is called the :class:`~.parsernode.ParserNode` tree is converted to an
    :class:`argparse.ArgumentParser` object, which is then used to analyse the given command line.
    The result from the :external:meth:`argparse.ArgumentParser.parse_args`
    call is then converted to arguments of the decorated function and finally the function
    is called with the arguments and its (optional) return value is passed on to the caller of
    :meth:`.execute`.

    The only other public method of this Class is the :meth:`~ArgParseDecorator.add_argument`
    decorator, which can be used to pass arguments directly to the underlying :code:`ArgumentParser` in
    case some special functionality of the argparse library is needed.
"""

import asyncio
import sys
from argparse import ArgumentParser, Namespace, ArgumentError
from typing import List, Union, Callable, Any, Type, Optional, Dict, Tuple, TextIO

from .annotations import ZeroOrMore  # for the builtin help command
from .argument import Argument
from .parsernode import ParserNode


def default_error_handler(exc: ArgumentError):
    """Default error handler that just prints the error message to stderr."""
    sys.stderr.write(str(exc))


class ArgParseDecorator:
    """
    Build python :external:class:`argparse.ArgumentParser` from decorated functions.

    It uses the signature and the annotations of the decorated class to determine all arguments
    and their types.
    It also uses the docstring for the command description, the help strings for all arguments
    and some additional metadata that can not be expressed via annotations.

    :param helpoption: Either

        *  :code:`"help"` to automatically create a help command, or
        *  :code:`"-h"` to automatically add a :code:`-h/--help` argument to each command (argparse library default), or
        *  :code:`None` to disable any automatically generated help.

        Defaults to :code:`"help"`
    :param hyph_replace: string to be replaced by :code:`-` in command names,
        defaults to :code:`__` (two underscores)
    :param argparser_class: Class to be used for ArgumentParser,
        defaults to :class:`~.nonexiting_argumentparser.NonExitingArgumentParser`
    :type argparser_class: :external:class:`argparse.ArgumentParser` or subclass thereof.
    :param kwargs: Other arguments to be passed to the ArgumentParser,
        e.g. :code:`description` or :code:`allow_abbrev`
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

        self._rootnode: ParserNode = ParserNode(None, **kwargs)

        if argparser_class:
            if isinstance(argparser_class, ArgumentParser):
                self._rootnode.argparser_class = argparser_class
            else:
                raise TypeError("argparser_class not a subclass of ArgumentParser")

        if helpoption == "help":
            # add the help command as a node to the tree
            node: ParserNode = self._rootnode.get_node("help")
            node.function = self.help

        if helpoption == "None":
            self._rootnode.add_help = False

    @property
    def argumentparser(self) -> ArgumentParser:
        """
        The generated :external:class:`argparse.ArgumentParser` object.

        This property is read only
        """
        argparser: ArgumentParser = self._rootnode.argumentparser
        if argparser is None:
            self._rootnode.generate_parser(None)
            argparser = self._rootnode.argumentparser

        return argparser

    @property
    def rootnode(self) -> ParserNode:
        """
        The root node of the :class:`~.parsernode.ParserNode` tree of commands.
        While the tree can be modified care must be taken to regenerate it after modifications by
        calling :meth:`~.parsernode.ParserNode.generate_parser` before calling :meth:`execute`.
        
        This property is read only.

        :return: The root node of the :code:`ParserNode` tree.
        """
        return self._rootnode

    #    @doublewrap
    #    def command(self, f: Callable):
    def command(self, *args: Union[str, Callable], **kwargs: Any) -> Callable:
        """
        Decorator to mark a method as an executable command.

        This takes the name of the decorated function and adds it to the internal command list.
        It also analyses the signature and the docstring of the decorated function to gather
        information about its arguments.

        :param args: Optional arguments that are passed directly to the
            :external:meth:`~argparse.ArgumentParser.add_subparsers` method of the underlying *ArgumentParser*.
        :param kwargs: Optional keyword arguments that are passed directly to the
            :external:meth:`~argparse.ArgumentParser.add_subparsers` method of the underlying *ArgumentParser*.
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
        """
        Decorator to add an argument to the command.

        This is an alternative way to add arguments to a function.
        While its use is usually not required there might be some situations where
        the function signature and its annotations are not sufficient to accurately
        describe an argument. In this case the :meth:`.add_argument` decorator can be used.
        Any pararmeter to this decorator is passed directly to
        :external:meth:`~argparse.ArgumentParser.add_argument` method of the underlying *ArgumentParser*

        The decorated function must have an argument of the same name or use :code:`*args` and :code:`**kwargs`
        arguments to retrieve the value of these arguments.

        Example::

            @parser.command
            @parser.add_argument('dest_file', type=argparse.FileType('r', encoding='latin-1'))
            @parser.add_argument('--foo', '-f')
            def write(*args, **kwargs):
                dest_file = args[0]
                foo = kwargs['foo']

        :param args: Optional arguments that are passed directly to the
            :code:`ArgumentParser.add_argument()` method.
        :param kwargs: Optional keyword arguments that are passed directly to the
            :code:`ArgumentParser.add_argument()` method.
        :return: The decorator function

        """

        def decorator(func) -> Callable:
            node: ParserNode = self._node_from_func(func)
            arg = Argument.argument_from_args(*args, **kwargs)
            node.add_argument(arg)
            return func

        return decorator

    def execute(self, commandline: str, base: Optional = None,
                error_handler=default_error_handler,
                stdout: TextIO = None,
                stderr: TextIO = None,
                stdin: TextIO = None) -> Optional:
        """
        Parse a command line and execute it.

        .. note::

            The :code:`base` must be supplied if the method implementing the command is a bound method,
            i.e. having :code:`self` as the first argument. It is not required if the command is
            implemented as a function (unbound) or an inner function (already bound).

        :param commandline: A string with a command and arguments (e.g. :code:`"command --flag arg"`)
        :param base: an object that is passed to commands as the :code:`self` argument.
            Required if any command method has :code:`self`, not required otherwise.
        :param error_handler: callback function to handle errors when parsing the command line.
            The handler takes a single argument with a :code:`ArgumentError` exception.
            The default is a function that just prints the error the :code:`stderr`.\n
            If set to :code:`None` parsing errors will result in an exception.
        :param stdout: Set to redirect the output of *ArgumentParser* (e.g. help texts) and the
            called command function to a different output, e.g a ssh stream.\n
            Optional, default is :code:`sys.stdout`
        :param stderr: Set to redirect error messages from the *ArgumentParser* and the
            called command function to a different output, e.g a ssh stream.\n
            Optional, default is :code:`sys.stderr`
        :param stdin: Set to redirect the input of the called command function to
            an input other than the current terminal, e.g a ssh stream.\n
            Optional, default is :code:`sys.stdin`

        :return: anything the command function/method returns.
        :raises ValueError: if the command function requires a :code:`self` parameter, but no :code:`base`
            argument was supplied.
        :raises ArgumentError: if the given command line contains errors and the :code:`error_handler`
            is set to :code:`None`.
        """
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        result = None

        try:
            # redirect input and output if required
            if stdin:
                sys.stdin = stdin
            if stdout:
                sys.stdout = stdout
            if stderr:
                sys.stderr = stderr

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

        except ArgumentError as err:
            if error_handler:
                error_handler(err)
            else:
                raise err  # just pass the exception to the caller
        finally:
            # restore in- and output
            sys.stdin = old_stdin
            sys.stdout = old_stdout
            sys.stderr = old_stderr

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
        node = self._rootnode
        if command:
            if self._rootnode.has_node(command):
                node = self._rootnode.get_node(command)
        argparser = node.argumentparser
        argparser.print_help()

    def _node_from_func(self, func: Callable) -> ParserNode:
        """
        Get the :class:'~.parsernode.ParserNode' for the given function or method.
        If the Node does not exist it will be created.
        :param func: a callable
        :return: a ParserNode
        """
        fullcmd = func.__name__
        fullcmd = fullcmd.replace(self.hyphen_replacement, '-')
        parts = fullcmd.split('_')
        node: ParserNode = self._rootnode.get_node(parts)
        return node


def get_arguments_from_namespace(
        args: Namespace,
        node: ParserNode) -> Tuple[List[str], Dict[str, Any]]:
    """
    Convert the Namespace object returned by :code:`parse_args()` into a (:code:`*args`, :code:`**kwargs`) tuple.
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
