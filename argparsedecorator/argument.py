from argparse import Action
from typing import Union, Any, Type, List, Tuple, Dict, Callable, TypeVar, Sequence

T = TypeVar('T')


class Argument:
    def __init__(self, name: str, eval_globals: Dict[str, any] = None):
        self.name = name
        self._globals = eval_globals if eval_globals else globals()
        self._alias: List[str] = list()
        self._action: Union[str, Action, None] = None
        self._nargs: Union[str, int, None] = None
        self._const: T = None
        self._default: Any = None
        self._type: Union[Type, None] = None
        self._choices: Union[list, None] = None
        self._required: bool = False
        self._help: str = ""
        self._metavar: Tuple[str] = tuple()
        self._dest: Union[str, None] = None

    @property
    def name(self) -> str:
        """
        The name of this argument. Unique for the associated command.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.lstrip('-').isidentifier():
            raise ValueError(f"name '{value}' is not a valid name for an argument.")
        self._name = value

    @property
    def alias(self) -> List[str]:
        """
        Other names. Only valid for Flags / Options (starting with '-' / '--')
        This property is read only; new aliases can be added with :meth:'add_alias()'
        :return: List of other names for this argument
        """
        return self._alias

    def add_alias(self, alias: str):
        if self.positional:
            raise ValueError(
                "Alias names can only be added to flags or options, i.e. arguments starting with '-'")
        if not alias.startswith('-'):
            raise ValueError("An alias name must start with a '-'")
        self._alias.append(alias)

    @property
    def action(self) -> Union[str, Action]:
        """
        The Action to perform for this argument.
        If this property has been set once it will raise an Exception
        if set to a different action.
        """
        return self._action

    @action.setter
    def action(self, new_action: Union[str, Type[Action]]):
        if not isinstance(new_action, str) and not issubclass(new_action, Action):
            raise TypeError("Action must be a string or a subtype of argparse.Action")
        if self._action:
            if self._action != new_action:
                raise ValueError(f"new action does not match previously set action")
        self._action = new_action

    @property
    def nargs(self) -> Union[str, int]:
        """Number of additional parameters for this Argument.
        Either an integer for a fixed number or one of '?', '*' or '+' for
        one or zero, zero or more, and one or more parameters.
        If set once any further attempts to change to a different value
        will raise an exception.
        """
        return self._nargs

    @nargs.setter
    def nargs(self, number: Union[str, int]) -> None:
        if isinstance(number, int):
            if number < 1:
                raise ValueError(f"Number of arguments must be 1 or greater, was {number}.")
            new_value = number
        else:
            if number not in ['?', '*', '+']:
                raise ValueError(
                    f"Number of arguments must be an int or either of '?', '*', '+', was f{number}")
            new_value = number

        if self._nargs:
            if self._nargs != new_value:
                raise ValueError("New nargs does not match previously set nargs")

        self._nargs = new_value

    @property
    def const(self) -> T:
        """Optional const value.
        If set once any further attempts to change to a different value
        will raise an exception.
        """
        return self._const

    @const.setter
    def const(self, value: T) -> None:
        if self._const:
            if self._const != value:
                raise ValueError("New const does not match previously set const")
        self._const = value

    @property
    def default(self) -> T:
        """Optional default value.
        If set once any further attempts to change to a different value
        will raise an exception.
        """
        return self._default

    @default.setter
    def default(self, value: T) -> None:
        if self._default:
            if self._default != value:
                raise ValueError("New default does not match previously set default")
        self._default = value

    @property
    def type(self) -> callable:
        """The type of the Argument. Can be any callable type.
        Can be a string with the name of the callable.

        .. warning::
            As the conversion is done by calling :func:'eval()' which is
            a security issue. Do not set this property to any arbitrary
            user input.

        If set once any further attempts to change to a different type
        will raise an exception.
        """
        return self._type

    @type.setter
    def type(self, argtype: Union[str, Type, Callable]) -> None:

        if isinstance(argtype, str):
            argtype = argtype.replace("builtins.",
                                      "")  # remove the "builtin." prefix as it causes errors
            new_type: Callable = eval(argtype, self._globals)
        else:  # not a str
            if not callable(argtype):
                raise ValueError(f"{argtype} is not callable")
            new_type: Callable = argtype

        # if type has been set previously check that the new type is identical.
        # changes of type / multiple different types are not allowed
        if self._type:
            if self._type.__name__ != new_type.__name__:
                raise ValueError(f"type has already been set to {self._type.__name__}")

        self._type = new_type

    @property
    def choices(self) -> Sequence:
        return self._choices

    @choices.setter
    def choices(self, values: Union[str, Sequence]) -> None:
        if isinstance(values, str):
            try:
                values = eval(values, self._globals)
            except SyntaxError as se:
                raise ValueError("Cannot parse the choices.", se)
        try:
            iter(values)
        except TypeError:
            raise ValueError(f"{values} is not a Sequence")

        if self._choices:
            raise ValueError(
                f"choices can be set only once. New values: {values}, old values: {self._choices}")

        self._choices = values

    @property
    def required(self) -> bool:
        return self._required

    @required.setter
    def required(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError(f"required must be either 'True' or 'False', was {value}")
        self._required = value

    @property
    def help(self) -> str:
        return self._help

    @help.setter
    def help(self, text: str) -> None:
        if not isinstance(text, str):
            text = str(text)
        self._help = text

    @property
    def metavar(self) -> Union[str, Tuple, None]:
        """
        Metavar is a name or a tuple of names for the pararmeters of this Argument.
        :return:
        """
        if len(self._metavar) == 0:
            return None
        if len(self._metavar) > 1:
            return self._metavar
        else:
            return self._metavar[0]

    @metavar.setter
    def metavar(self, value: Union[str, Sequence]) -> None:
        if isinstance(value, str):
            values = value.split(',')
            values = tuple(map(str.strip, values))
        else:
            values = tuple(value)

        num = len(values)
        if num > 1 and num != self.nargs:
            raise ValueError(
                f"List of metavar entries ({num}) must match number of arguments in nargs ({self.nargs})")
        self._metavar = values

    @property
    def dest(self) -> Union[str, None]:
        """Get the dest argument.
        Usually 'None', but if any aliases have been set the dest is automatically set
        to the Argument name,  but without any '-' at the beginning.
        This is to override the argparse default to use the longest optional name."""
        if not self.alias:
            return None
        else:
            return self.name.lstrip('-')

    @dest.setter
    def dest(self, value: str) -> None:
        raise NotImplementedError("Setting dest is currently not implemented")

    @property
    def positional(self) -> bool:
        """'True' if this argument is a positional argument, i.e. does not start with a hyphen '-'."""
        return not self._name.startswith('-')

    @property
    def optional(self) -> bool:
        """'True' if this argument is an optional argument, i.e. starts with a hyphen '-'."""
        return self._name.startswith('-')

    def get_command_line(self) -> Tuple[List[str], Dict[str, Any]]:
        args: List[str] = list()
        args.append(self.name)
        args.extend(self._alias)
        kwargs = {}
        if self._action:
            kwargs['action'] = self.action
        if self._nargs:
            kwargs['nargs'] = self.nargs
        if self._const:
            kwargs['const'] = self.const
        if self._default is not None:
            kwargs['default'] = self.default
        if self._type:
            kwargs['type'] = self.type
        if self._choices:
            kwargs['choices'] = self.choices
        if self._required:
            kwargs['required'] = self.required
        if self._help:
            kwargs['help'] = self.help
        if self._metavar:
            kwargs['metavar'] = self.metavar
        if self._dest:
            kwargs['dest'] = self.dest

        return args, kwargs

    @staticmethod
    def argument_from_args(*args: str, **kwargs: Any):

        # split args into name and -optional- aliases
        if len(args) > 1:
            # flags / optionals.
            # Name is the first optional ('--') or the first flag '-' if no optional. All others are aliases
            optional = []
            flags = []
            for name in args:
                if name.startswith('--'):
                    optional.append(name)
                elif name.startswith('-'):
                    flags.append(name)
                else:
                    raise ValueError("Optional or Flag must start with a '-'")
            if optional:
                name = optional.pop(0)
            else:
                name = flags.pop(0)

            argument = Argument(name)

            for alias in optional:
                argument.add_alias(alias)
            for alias in flags:
                argument.add_alias(alias)
        elif len(args) == 1:
            argument = Argument(args[0])
        else:
            raise ValueError("Name of the argument is missing.")

        # copy all other kwargs to the argument.
        for key, value in kwargs.items():
            if hasattr(argument, key):
                setattr(argument, key, value)

        return argument

    def __str__(self):
        args, kwargs = self.get_command_line()
        argstr = ",".join(list(args))
        kwargstr = ",".join(f"{key}={value}" for key, value in kwargs)
        result = argstr + ", " + kwargstr if kwargstr else argstr
        return result
