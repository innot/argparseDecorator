# This file is part of the ArgParseDecorator library.
#
# Copyright (c) 2022 Thomas Holland
#
# This work is licensed under the terms of the MIT license.
# For a copy, see the accompaning LICENSE.txt.txt file
# or go to <https://opensource.org/licenses/MIT>.

"""
ParserNode is a class to store one command and all of its arguments and keeps a list
of child ParserNodes for subsommands.

This class also has all the code to parse a function signature and the docstring associated
with that function.
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import re
import sys
from argparse import ArgumentParser
from typing import Union, Dict, Callable, Type, Any, Iterable, Optional, Mapping

from .annotations import *
from .argument import Argument
from .nonexiting_argumentparser import NonExitingArgumentParser


class ParserNode:
    """
    Single Node of the parser tree.

    A tree of nodes is used to represent the complete command hierarchy.
    The root node is generated automatically by the :class:`~.argparse_decorator.ArgParseDecorator`.

    The children are added by successive calls from the :meth:`~.argparse_decorator.ArgParseDecorator.command`
    decorator method.
    Once the tree is finished, the actual :external:class:`argparse.ArgumentParser` representing all commands and
    their arguments of this node can be accessed by the :meth:`argumentparser` property.

    Each *ParserNode* has a :meth:`root` property to get the root node.

    :param title: The name of the command, :code:`None` for the root node
    :param parent:  The parent node for this node. Defaults to :code:'None' for a root node.
    :param kwargs:  Other arguments for :external:class:`argparse.ArgumentParser` (for the root node) or
                    for :external:meth:`argparse.ArgumentParser.add_subparsers` (all other nodes)
    """

    def __init__(self,
                 title: Optional[str],
                 parent: 'ParserNode' = None,
                 **kwargs):

        super().__init__()

        self._prog: str = ""  # Name of the programm. Usually empty for CLIs.
        self._title: Optional[str] = title
        self._parent: ParserNode = parent
        self._kwargs: dict = kwargs

        # The sub commands as a dictionary with the name of the subcommand and its ParserNode.
        self._children: Dict[str, ParserNode] = {}

        self.description: str = ""

        self._arguments: Dict[str, Argument] = {}
        """Registry for all arguments of this node"""

        self.positional_args: List[str] = []
        """List of all positional (args) arguments of this node."""

        self.optional_args: List[str] = []
        """List of all optional (kwargs) arguments of this node."""

        self._func: Callable[..., Any] = self.no_command
        self._func_globals: Dict[str, Any] = {}
        self._func_has_self: bool = False
        self._func_coroutine: bool = False

        self._parser: Union[ArgumentParser, None] = None
        self._subparser: Union[object, None] = None

        # The argumentparser class to use. Defaults to the provided NonExitingArgumentParser
        # but can be changed via the argparse_class property to use a custom subclass.
        self._argparser_class: Union[Type[ArgumentParser], None] = NonExitingArgumentParser

        # default is to inhibit the [-h] option and to use the "help" command
        # provided by the ArgParseDecorator
        self._add_help = False

    @property
    def title(self) -> str:
        """The name of the command represented by this node."""
        return self._title

    @property
    def root(self) -> 'ParserNode':
        """The root node of the ParserNode hierarchy."""
        if self._parent:
            # traverse toward the root
            return self._parent.root
        # This node is the root.
        return self

    @property
    def argumentparser(self) -> ArgumentParser:
        """
        Get the ArgumentParser representing this Node.

        When read the returned object represents the current state of the Node.
        In case of any change to this Node or to the Tree this :external:class:`argparse.ArgumentParser`
        is regenerated.
        """
        if not self._parser:
            # need to generate it first, starting at the root node
            self.root.generate_parser(None)
        return self._parser

    @property
    def argparser_class(self) -> Type[ArgumentParser]:
        """
        The class to use for building the parser.

        Default is the :class:`~.nonexiting_argumentparser.NonExitingArgumentParser` class, a subclass of
        :external:class:`argparse.ArgumentParser` that does not call sys.exit().
        It can be changed to subclass of ArgumentParser.
        Only relevant for the root Node. If changed on any other child node the class will be
        passed to the root node and, if the parser has already been generated, the whole parser
        will be regenerated.
        """
        rootnode = self.root
        return rootnode._argparser_class

    @argparser_class.setter
    def argparser_class(self, new_class: Type[ArgumentParser]):
        rootnode = self.root
        rootnode._argparser_class = new_class
        if rootnode._parser:  # has been generated before
            # regenerate parser
            rootnode.generate_parser(None)

    @property
    def function(self) -> Callable[[Dict[str, Any]], Any]:
        """
        The function that implements the command.

        When set extract all available information from the function signature
        and from the function docstring.
        """
        return self._func

    @function.setter
    def function(self, function: Callable[[Dict[str, Any]], Any]):
        if not callable(function):
            raise ValueError(f"'function' must be a callable function. Was a {type(function)}")
        self._func = function
        if hasattr(function, '__globals__'):
            self._func_globals = function.__globals__  # type: ignore
        if hasattr(function, '__self__'):
            self._func_has_self = True
        if asyncio.iscoroutinefunction(function):
            self._func_coroutine = True

        self.analyse_signature(function)
        self.analyse_docstring(function)

    @property
    def function_globals(self) -> Dict[str, Any]:
        """
        Get the globals from the command function.

        Autmatically retrieved when the :meth:`function` property is set to a function.

        This property is read only.
        """
        if self._func_globals:
            return self._func_globals
        else:
            return globals()

    if 'unittest' in sys.modules:
        # make the property writable for unit tests to avoid creating a function for every test.
        @function_globals.setter
        def function_globals(self, value: Dict[str, Any]) -> None:
            self._func_globals = value

    @property
    def bound_method(self):
        """
        Is :code:`True` when the command function is a bound method,
        i.e. if it requires a :code:`self` argument.

        This property is read only.
        """
        return self._func_has_self

    @property
    def coroutine(self):
        """
        Is :code:`True` when the command function is a coroutine,
        i.e. if it starts with :code:`async def`.

        This property is read only.
        """
        return self._func_coroutine

    @property
    def arguments(self) -> Dict[str, Argument]:
        """
        A dictionary of all arguments set for this node.

        Read only property.
        """
        return self._arguments

    def get_argument(self, name: str) -> Optional[Argument]:
        """
        Get the argument with the given name for this command.

        If there is no argument with exactly this name then this
        method will append one or two :code:`-` to find a match.

        :param name: name of the argument, e.g. :code:`--foo`
        :return: The :class:`.Argument` object or :code:`None` if no argument with this name.
        """
        for n in [name, '-' + name, '--' + name]:
            if n in self._arguments:
                return self._arguments[n]

        return None

    def add_argument(self, arg: Argument) -> None:
        """
        Add a single :class:`.Argument` to this node.

        The Argument must be unique, i.e. each Argument may be added only once.

        :param arg: single :class:`.Argument` object.
        """
        if self.has_argument(arg):
            # There can be only one
            raise ValueError(f"Argument '{arg.name} declared twice.")
        name = arg.name
        self.arguments[name] = arg

        # Maintain the order of the positional arguments
        # This is used when unpacking the Namespce object returned by parse_args()
        # Strip any leading '-' as this is how they are stored in the Namespace object
        if arg.positional:
            self.positional_args.append(arg.name.lstrip('-'))
        else:
            self.optional_args.append(arg.name.lstrip('-'))

    def add_arguments(self, args: Iterable[Argument]) -> None:
        for arg in args:
            self.add_argument(arg)

    def has_argument(self, arg: Argument) -> bool:
        return arg.name in self.arguments

    @property
    def add_help(self) -> bool:
        """
        :code:`True` if the help system of ArgumentParser is active (i.e. [-h] flag for all commands).

        If :code:`False` this is inhibited. This is useful if the caller supplies its own help system.

        This property is valid for this node and all of its children.

        Default is :code:`False`.
        """
        return self._add_help

    @add_help.setter
    def add_help(self, value: bool) -> None:
        old_addhelp = self._add_help
        self._add_help = value
        if value != old_addhelp and self._parser:
            # if the value has changed and the parser has already been generated
            # regenerate the whole parser
            self.root.generate_parser(None)

    def generate_parser(self, parentparser) -> None:
        """
        Build the actual :external:class:`argparse.ArgumentParser` object for this Node.

        If it is not the root Node then the *ArgumentParser* from the parent
        must be supplied to add the parser representing this node.
        If this Node has children then they will be generated as well.
        Normally this method should only be called once for the root Node.

        :param parentparser: The *ArgumentParser* to add this Parser to.
        :type parentparser: :external:class:`argparse.ArgumentParser` or subclass thereof
        """
        if not self._parent:
            # root node is special. It generates the ArgumentParser starting point
            parser_cls = self.argparser_class
            self._parser = parser_cls(prog=self._prog,
                                      description=self.description,
                                      add_help=self.add_help)
        else:
            self._parser = parentparser.add_parser(name=self.title,
                                                   help=self.description,
                                                   description=self.description,
                                                   add_help=self.add_help)

        # Add arguments
        if self.arguments:
            for entry in self.arguments.values():
                args, kwargs = entry.get_command_line()
                self._parser.add_argument(*args, **kwargs)

        # Add callback
        if self._func:
            self._parser.set_defaults(func=self._func, node=self)

        if self._children:
            self._subparser = self._parser.add_subparsers()
            for child in self._children.values():
                child.generate_parser(self._subparser)

    def get_node(self, command: Union[str, List[str]]) -> 'ParserNode':
        """
        Get the ParserNode representing the given command.

        The command can be either a single name or a list with a command and subcommand names.
        A new node will be created if no node for a command / subcommand exists.
        Should be used on the root node to make the command global.

        :param command: single command name or list of hierachical names.
        """

        names: List[str] = [command] if isinstance(command, str) else command.copy()

        if not names:
            # empty or None: this is the node the caller was looking for
            return self

        name = names.pop(0)
        # check if there is a child with this name already
        node = self._children.get(name)
        if not node:
            # node does not exist. Create it
            node = ParserNode(name, self)
            node.add_help = self.add_help
            self._children[name] = node
            self.root._parser = None  # invalidate any previously created ArgumentParsers

        return node.get_node(names)

    def has_node(self, command: Union[str, List[str]]) -> bool:
        """
        Check if a Node for the given command exists in the Tree.

        Best if used on the rootnode to check the whole tree.

        :param command: single command name or list of command names (for subcommands)
        :return: :code:`True` if node exists
        """
        names: List[str] = [command] if isinstance(command, str) else command.copy()
        if not names:  # empty list
            return False

        if names[0] == self._title:  # name match,
            if len(names) == 1:  # no further subcommand names
                return True
            else:
                names.pop(0)  # remove this name and continue with the children

        # check if there is a child with this name exists
        node = self._children.get(names[0])
        if node:
            return node.has_node(names)
        else:
            return False

    def get_command_dict(self) -> Dict[str, Optional[Dict]]:
        """
        Get a dictionary with all commands in a form suitable for the
        `Python Prompt Toolkit <https://python-prompt-toolkit.readthedocs.io/en/master/>`_
        autocompleter function.

        See `Nested completion
        <https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#nested-completion>`_
        for details.

        :returns: dict
        """

        sub_dicts = {}
        for child in self._children.values():
            sub_dicts.update(child.get_command_dict())

        if self.title is None:  # root node has only sub-commands but is not a command itself
            return sub_dicts

        if sub_dicts:
            # at least one sub command
            return {self.title: sub_dicts}
        else:
            return {self.title: None}

    def no_command(self, **_) -> None:
        # do nothing
        pass

    def analyse_signature(self, func: Callable):
        signature = inspect.signature(func)
        parameters: Mapping[str, inspect.Parameter] = signature.parameters
        for name, para in parameters.items():
            # ignore *args and **kwargs
            if str(para).startswith("*args") or str(para).startswith("**kwargs"):
                continue

            # if first parameter is self this is a bound method
            if str(para) == "self":
                self._func_has_self = True
                continue

            # check if the name already exists in the argument registry
            # if yes use the previously generated one.
            # this is required as the add_argument decorator may have created the argument
            # before we look at the signature
            arg = self.get_argument(name)
            if not arg:
                # does not exist - create a new one
                arg: Argument = Argument(name, self.function_globals)

            p = parameters[name]

            # check if annotation or default are empty (check against 'signature.empty')
            annotation = p.annotation if p.annotation != signature.empty else ""
            default = p.default if p.default != signature.empty else None

            # now analyse the complete annotation.
            self.analyse_annotation(annotation, arg)

            # handle some special cases
            if arg.optional and default is False:
                # This seems counter-intuitive, but if a flag is absent on the command line
                # nothing is returned from the parse_arg() call and the default of 'False'
                # is assigned to the argument.
                arg.action = "store_true"  # -f: Flag = False
                arg.type = None  # store_true implies bool
            if arg.optional and default is True:
                arg.action = "store_false"  # -f: Flag = True
                arg.type = None  # store_true implies bool
            if arg.action == "store_const" or arg.action == "append_const":
                arg.const = default  # -f: Flag | AppendConst = 42
            else:
                arg.default = default

            # check that the default for a 'choices' argument is actually one of the choices.
            if arg.choices and arg.default:
                if arg.default not in arg.choices:
                    raise ValueError(f"Default value {arg.default} must be in list of choices.")

            self.add_argument(arg)

    def analyse_annotation(self, annotation: Union[Type, str], arg: Argument) -> None:
        # do nothing if there is no annotation
        if not annotation:
            return

        # At this point the annotation can be either
        #  -    a string (Python 3.10+ or Python 3.7+ with from __future__ import annotations), or
        #  -    a Type or Class (Python 3.5 - Python 3.9)
        # convert everything non-stringy into a string for further parsing
        if inspect.isclass(annotation):
            a_str = fullname(annotation)
        else:
            a_str = str(annotation)

        # from here we only deal with string annotation, regardless of the Python version
        # This makes it compatible with versions older than 3.8 (which has methods for
        # analyzing types)

        # check if 3.10 style Union (seperated by bars) or pre 3.10 (Union[...])
        old_style_parser = re.compile(r".*Union\[(.*)]")  # parse "Union[foo, bar]" to "foo, bar"
        m = old_style_parser.match(a_str)
        if m:
            # Union[...] used
            union_group = m.group(1)
            # now split by comma, but not bracketed commas
            annotation_parts = split_union(union_group)
        else:
            # bar separation (or just a single type)
            annotation_parts = a_str.split('|')

        if annotation_parts:
            # at least one part present
            # now parse each part of the union annotation (or the single part if not a union)
            for part in annotation_parts:
                part = part.strip()
                if part:  # could be empty
                    self.analyse_annotation_part(part, arg)

    def analyse_annotation_part(self, part: str, arg: Argument) -> None:
        if is_type_key(Flag, part):
            check_explicit_type(part, arg)
            arg.name = '-' + arg.name

        elif is_type_key(Option, part):
            check_explicit_type(part, arg)
            arg.name = '--' + arg.name

        elif is_type_key(OneOrMore, part):
            check_explicit_type(part, arg)
            arg.nargs = "+"

        elif is_type_key(ZeroOrMore, part):
            check_explicit_type(part, arg)
            arg.nargs = "*"

        elif is_type_key(ZeroOrOne, part):
            check_explicit_type(part, arg)
            arg.nargs = "?"

        elif is_type_key(Exactly1, part):
            check_explicit_type(part, arg)
            arg.nargs = 1
        elif is_type_key(Exactly2, part):
            check_explicit_type(part, arg)
            arg.nargs = 2
        elif is_type_key(Exactly3, part):
            check_explicit_type(part, arg)
            arg.nargs = 3
        elif is_type_key(Exactly4, part):
            check_explicit_type(part, arg)
            arg.nargs = 4
        elif is_type_key(Exactly5, part):
            check_explicit_type(part, arg)
            arg.nargs = 5
        elif is_type_key(Exactly6, part):
            check_explicit_type(part, arg)
            arg.nargs = 6
        elif is_type_key(Exactly7, part):
            check_explicit_type(part, arg)
            arg.nargs = 7
        elif is_type_key(Exactly8, part):
            check_explicit_type(part, arg)
            arg.nargs = 8
        elif is_type_key(Exactly9, part):
            check_explicit_type(part, arg)
            arg.nargs = 9

        elif is_type_key(Choices, part):
            expression = get_bracket_content(part)
            expression = resolve_literals(expression)
            choices = eval(expression, self.function_globals)
            arg.choices = choices

        elif is_type_key(StoreAction, part):
            arg.action = "store"

        elif is_type_key(StoreConstAction, part):
            arg.action = "store_const"

        elif is_type_key(StoreTrueAction, part):
            arg.action = "store_true"

        elif is_type_key(StoreFalseAction, part):
            arg.action = "store_false"

        elif is_type_key(AppendAction, part):
            arg.action = "append"

        # AppendConstAction is not supported by ArgParseDecorator
        # elif is_type_key(AppendConstAction, part):
        #     arg.action = "append_const"

        elif is_type_key(CountAction, part):
            arg.action = "count"
            if arg.type == int:
                # the count action implies an int type and does not like explicit type declarations
                arg.type = None
            elif arg.type:
                # raise an exception if any type other than int has been set
                raise TypeError("'Count' implies type int and does not accept any other type.")

        elif is_type_key(ExtendAction, part):
            arg.action = "extend"

        elif is_type_key(CustomAction, part):
            expression = get_bracket_content(part)
            expression = resolve_literals(expression)
            if not expression:
                raise ValueError(f"CustomAction requires a parameter, CustomAction[...]")
            actionclass = eval(expression, self.function_globals)
            if not callable(actionclass):
                raise ValueError(
                    f"CustomAction requires a callable as parameter, was {str(actionclass)}")
            arg.action = actionclass

        # None of the predefined keywords matches, therefore it is propably a type
        else:
            if part:
                if part != "typing.Any":  # Any does not imply anything so ignore it.
                    # convert string of type back to type
                    arg.type = eval(part, self.function_globals)

        return

    def analyse_docstring(self, func: Callable) -> None:
        """
        Parse the docstring to extract the description (anything before the first metadata) and any metadata.
        """

        description: List[str] = []
        docstring = func.__doc__
        if not docstring:
            # nothing to do if there is no docstring.
            return
        lines = docstring.splitlines()

        in_description = True

        for line in lines:
            line = line.strip()
            if line.startswith(':param'):
                # :param name: help text
                in_description = False
                self.parse_param(line[len(':param'):].strip())

            elif line.startswith(':alias'):
                # :alias name: alias1, alias2, ...
                in_description = False
                self.parse_alias(line[len(':alias'):].strip())

            elif line.startswith(":choices"):
                in_description = False
                self.parse_choices(line[len(':choices'):].strip())

            elif line.startswith(":metavar"):
                in_description = False
                self.parse_metavar(line[len(':metavar'):].strip())

            elif in_description and line:
                description.append(line)
            else:
                # ignore anything else
                pass

        self.description = ' '.join(description)
        return

    def parse_param(self, line: str) -> None:
        # split into name and description
        tmp = line.split(':', maxsplit=1)
        arg_name = tmp[0].strip()
        arg = self.get_argument(arg_name)
        if not arg:
            # The parameter does not exist
            raise NameError(f":param {arg_name}: No parameter with the name {arg_name}")
        if len(tmp) > 1:
            arg_help = tmp[1].strip()
            if arg_help.startswith("SUPPRESS"):
                arg_help = argparse.SUPPRESS
        else:
            arg_help = ""
        arg.help = arg_help

    def parse_alias(self, line: str) -> None:
        # split into name and list of aliases
        tmp = line.split(':', maxsplit=1)
        arg_name = tmp[0].strip()
        if len(tmp) > 1:
            arg_aliases = tmp[1].split(',')
            arg_aliases = [s.strip() for s in arg_aliases]
        else:
            raise ValueError(":alias: directive requires at least one alias.")

        # aliases only work for flag (-f) or optional (--foo)
        arg = self.get_argument(arg_name)
        if not arg or not arg.name.startswith('-'):
            raise NameError(
                f":alias {arg_name}: Can't find a Flag or Optional with the name {arg_name}")

        for alias in arg_aliases:
            arg.add_alias(alias)

    def parse_choices(self, line: str) -> None:
        # split into name and the coices
        tmp = line.split(':', maxsplit=1)
        arg_name = tmp.pop(0).strip()
        if not tmp or not tmp[0]:
            raise ValueError(":choices ...: must have some actual choices.")
        arg = self.get_argument(arg_name)
        if not arg:
            raise NameError(f":choices {arg_name}: Can't find an argument names {arg_name}")

        choices = eval(tmp[0], self.function_globals)
        # choices must be iterable. Check this
        try:
            _ = iter(choices)
            arg.choices = choices
        except TypeError:
            raise ValueError(f"Value of :choices {arg_name}: is not a sequence.")

    def parse_metavar(self, line: str) -> None:
        # split into name and the coices
        tmp = line.split(':', maxsplit=1)
        arg_name = tmp.pop(0).strip()
        if not tmp or not tmp[0]:
            raise ValueError(":metavar ...: requires at least one metavar name.")
        arg = self.get_argument(arg_name)
        if not arg:
            raise NameError(f":metavar {arg_name}: Can't find an argument named {arg_name}")

        metas = split_strip(tmp[0])
        metas = [m.strip('"\'') for m in metas]
        arg.metavar = metas

    def __str__(self, level: int = 0):
        args = ','.join([str(arg) for arg in self.arguments])
        result = f"{self.title}({args}) : {self.description}"
        if self._children:
            for name in self._children.keys():
                childstr = str(self._children[name])
                # indent by one tab
                chlstrlist = [f"\t{val}" for val in childstr.splitlines()]
                childstr = "\n".join(chlstrlist)
                result = f"{result}\n{childstr}"
        return result


def split_strip(string: str, sep: str = ',') -> List[str]:
    """Split a string and remove all whitespaces."""
    splitted = string.split(sep)
    return [s.strip() for s in splitted]


def resolve_literals(string: str) -> str:
    # replace Literal[...] with a tuple (...)
    matches = ("typing.Literal[", "Literal[")
    start = exp_start = -1
    for match in matches:
        start = string.find(match)
        if start >= 0:
            exp_start = start + len(match)
            break

    exp_index = exp_start
    if exp_index >= 0:
        # find matching closing bracket
        bracket_counter = 1
        while exp_index < len(string):
            c = string[exp_index]
            if c == '[':
                bracket_counter += 1
            if c == ']':
                bracket_counter -= 1
                if bracket_counter == 0:
                    # found the matching closing bracket
                    break
            exp_index += 1
    else:
        # No 'Literal' found
        return string

    resolved = string[:start] + " (" + string[exp_start:exp_index] + ")"
    if exp_index + 1 < len(string):
        resolved = resolved + string[exp_index + 1:]

    return resolve_literals(resolved)  # recursive call in case there are more embedded Literals


def is_type_key(targettype: Type, part: str) -> bool:
    part = part.split('[')[0]  # if the type has an optional [...] discard it
    if part == targettype.__name__:
        return True
    elif part == fullname(targettype):
        return True
    else:
        return False


def fullname(o):
    module = o.__module__
    if module == 'builtins':
        return o.__name__  # avoid outputs like '__builtin__.str'
    return module + '.' + o.__qualname__


def check_explicit_type(part: str, arg: Argument):
    part_type = get_bracket_content(part)
    if part_type:
        arg.type = part_type


def get_bracket_content(string: str) -> str:
    """
    Find the outermost brackets and return their content.
    For example :code:`foo[bar[baz]]` will return :code:`bar[baz]`

    :param string: any string
    :return: bracket content or empty string if there were no brackets or if they were empty.
    """
    first = string.find('[')
    last = string.rfind(']')
    if -1 < first < last:
        return string[first + 1:last]
    else:
        return ''


def split_union(string: str) -> List[str]:
    result: List[str] = []
    tmp: List[str] = []
    bracket_count = 0
    for char in string:
        if char == "," and bracket_count == 0:
            result.append("".join(tmp).strip())
            tmp = []
        else:
            tmp.append(char)
            if char == "[" or char == "(" or char == "{":
                bracket_count += 1
            if char == "]" or char == ")" or char == "}":
                bracket_count -= 1

    result.append("".join(tmp).strip())
    return result

# unused. Dirty hack used during development.
# Kept here in case I need it some other time.
# def get_caller_globals():
#     """Get the local namespace of the outside caller."""
#     stack = inspect.stack()
#
#     while stack:
#         frameinfo = stack.pop(0)
#         filename = frameinfo.filename
#         if filename.endswith("\\parsernode.py") or filename.endswith("\\argparse_decorator.py"):
#             continue
#         frame = frameinfo[0]
#         return frame.f_globals
#
#     return globals()  # fallback to our own globals
