#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or
#  go to <https://opensource.org/licenses/MIT>.
#

"""
    Example of running a argparseDecorator CLI in an asyncssh server.

    It uses `asyncssh <https://asyncssh.readthedocs.io>`_ to provide an ssh server and
    the `Python prompt toolit <https://python-prompt-toolkit.readthedocs.io>`_ to provide a rich terminal interface with
    code completion, colours and more.

    .. note::

        The ssh server is very basic and will accept any client connection.
        Use either in a closed environment (behind firewall) or add authentification as required.

    This module has three main classes:

    #.  :class:`BaseCLI` contains all the low level code linking an
        `argparseDecorator <https://argparsedecorator.readthedocs.io/>`_ based CLI with the *prompt toolkit*.
        It also implements two commands that are probably useful for all ssh based cli's:

        * :meth:`exit <BaseCLI.exit>` to close the ssh connection from the remote end, and

        * :meth:`shutdown <BaseCLI.shutdown>` to shut down the server from the remote end

        This class can be subclassed to implement more commands without worrying about the details.

    #.  :class:`DemoCLI` is a small example CLI built on top of :class:`BaseCLI` showcasing a few of the possibilities.

    #.  :class:`SshCLIServer` contains all required code to start the SSH Server.

    In addition to those three classes a few helpful functions are implemented to handle formatted output:

    *   :func:`print_html` to use some basic
        `html formatting <https://python-prompt-toolkit.readthedocs.io/en/master/pages/printing_text.html#html>`_.

    *   :func:`print_error`, :func:`print_warn` and :func:`print_info` for color coded status messages.
        The colors used can be changes by modifying the supplied :data:`style` dictionary.


"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from asyncio import Event
from typing import TextIO, Optional, Any, Dict

import asyncssh
from prompt_toolkit import print_formatted_text, PromptSession, HTML
from prompt_toolkit.completion import NestedCompleter, Completer
from prompt_toolkit.contrib.ssh import PromptToolkitSSHServer, PromptToolkitSSHSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import yes_no_dialog, ProgressBar
from prompt_toolkit.styles import Style

from argparsedecorator import ArgParseDecorator, ZeroOrOne

style = Style.from_dict({
    'error': 'red',
    'warn': 'orange',
    'info': 'grey'
})
"""
Some basic styles. 
Styles can be used as html tags, e.g.:

.. code-block:: html

    <error>An error message</error>
    
Useful for the :func:`print_html` function.
"""


def print_html(text: str) -> None:
    """
    Format and print text containing HTML tags.

    .. note::
        The prompt toolkit HTML to ANSI converter supports only a few basic HTML tags.
        See `here <https://python-prompt-toolkit.readthedocs.io/en/master/pages/printing_text.html#html>`_
        for more info.

    :param text: A string that may have html tags.
    """
    print_formatted_text(HTML(text), style=style)


def print_error(text: str) -> None:
    """
    Print an error message.

    By default, this message is printed in red. As the text is printed via :func:`print_html` it can include
    HTML tags for further formatting.

    :param text: The message to be printed.
    """
    print_html(f"<error>{text}</error>")


def print_warn(text: str) -> None:
    """
     Print a warning message.

     By default, this message is printed in orange. As the text is printed via :func:`print_html` it can include
     HTML tags for further formatting.

     :param text: The message to be printed.
     """

    print_html(f"<warn>{text}</warn>")


def print_info(text: str) -> None:
    """
     Print an info message.

     By default, this message is printed in grey. As the text is printed via :func:`print_html` it can include
     HTML tags for further formatting.

     :param text: The message to be printed.
     """

    print_html(f"<info>{text}</info>")


class BaseCLI:
    """
    Basic Command Line Interface for use with the
    `PromptToolkitSSHServer
    <https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/src/prompt_toolkit/contrib/ssh/server.py>`_

    It contains all the low-level stuff to integrate it with a PromptToolkit SSH session (in the :meth:`cmdloop` method)

    To add more commands subclass this base CLI, as shown in the :class:`DemoCLI` class.

    .. note::

        Subclasses must use the *ArgParseDecorator* from *BaseCLI*. Do not create a seperate instance.
        The *BaseCLI* instance is in the :data:`BaseCLI.cli` class variable and can be accessed like this:

        .. code-block:: python

            class MyCLI(BaseCLI):
                cli = BaseCLI.cli
                ...

    The other class variables :data:`BaseCLI.intro` and :data:`BaseCLI.prompt` can be overwritten by subclasses.
    """

    intro = "\nThis is a basic SSH CLI.\nType Ctrl-C to exit.\n"
    """Intro text displayed at the start of a new session. Override as required."""

    prompt = "\n<green># </green>"
    """Prompt text to display. Override as required."""

    cli = ArgParseDecorator()
    """The :class:`~.argparse_decorator.ArgParseDecorator` used to decorate command methods."""

    def __init__(self):
        self.prompt_session = None
        self.stdout: TextIO = sys.stdout
        self.stdin: TextIO = sys.stdin
        self.promptsession = None
        self._server: Optional[asyncssh.SSHAcceptor] = None
        self.completer: Optional[Completer] = None

    @property
    def command_dict(self) -> Dict[str, Optional[Dict]]:
        """
        A dictionary with all supported commands suitable for the PromptToolkit
        `Autocompleter <https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#autocompletion>`_
        """
        # make the command-dict accessible
        return self.cli.command_dict

    @property
    def sshserver(self) -> asyncssh.SSHAcceptor:
        """
        The SSH Server (actually asyncssh.SSHAcceptor) running this session.
        Must be set externally and is used for the :code:`shutdown` command.
        """
        return self._server

    @sshserver.setter
    def sshserver(self, sshserver: asyncssh.SSHAcceptor):
        self._server = sshserver

    #

    # The build in commands
    #

    @cli.command
    def exit(self) -> str:
        """exit closes this ssh connection."""
        return "exit"

    @cli.command
    async def shutdown(self) -> str:
        """shutdown the ssh server. All connections will be disconnected."""
        result = await yes_no_dialog("Shutdown", "Are you shure you want to shutdown the server?").run_async()
        if result:
            return "shutdown"
        return ""

    # noinspection PyMethodMayBeStatic
    def error_handler(self, exc: Exception) -> None:
        """
        Prints any parser error messages in the <error> style (default: red)

        Override this for more elaborate error handling.

        :param exc: Exception containg the error message.
        """
        print_error(str(exc))

    # noinspection PyMethodMayBeStatic
    async def get_prompt_session(self) -> PromptSession:
        """
        Start a new prompt session.

        Called from :meth:`cmdloop` for each new session.

        By default, it will return a simple PromptSession without any argument.
        Override to customize the prompt session.

        :return: a new PromptSession object
        """
        return PromptSession()

    # noinspection PyMethodMayBeStatic
    async def run_prompt(self, prompt_session: PromptSession) -> Any:
        """
        Display a prompt to the remote user and wait for his command.

        The default implementation uses only a comand name completer.
        Override to implement other, more advanced features.

        :return: The command entered by the user
        """
        # inititialize command completion
        # List (actually a dict) of all implemented commands is provided by the ArgparseDecorator and
        # used by the prompt_toolkit
        if not self.completer:
            # create the command dict only once
            all_commands = self.command_dict
            self.completer = NestedCompleter.from_nested_dict(all_commands)

        # The prompt visual
        prompt_formatted = HTML(self.prompt)

        return await prompt_session.prompt_async(prompt_formatted, completer=self.completer)

    async def execute(self, cmdline: str) -> Any:
        """
        Excecute the given command.

        :return: 'exit' to close the current ssh session, 'shutdown' to end the ssh server.
                  All other values are ignored.
        """
        result = await self.cli.execute_async(cmdline, base=self, error_handler=self.error_handler, stdout=self.stdout)
        return result

    async def cmdloop(self, ssh_session: PromptToolkitSSHSession) -> None:
        """
        Handle an incoming SSH connection.

        This is the entry point to start the CLI in the given SSH session.
        It will display a prompt and execute the user input in a loop until the session is closed, either by the
        remote end or by the 'exit' command.

        This will be called from the ssh server for each incoming connection. There is no need to call it directly.

        :param ssh_session: Session object
        """

        self.prompt_session = PromptSession(refresh_interval=0.5)

        # tell the CLI about stdout (if not using the print_formatted_text() function)
        self.stdout = ssh_session.app_session.output
        self.stdin = ssh_session.app_session.input

        print_formatted_text(HTML(self.intro))

        with patch_stdout():
            while True:
                try:
                    command = await self.run_prompt(self.prompt_session)
                    if command:
                        result = await self.execute(command)
                        if result == "exit":
                            # close current connection
                            print_warn("Closing SSH connection")
                            return

                        if result == "shutdown":
                            if self.sshserver:
                                print_warn("SSH Server is shutting down")
                                self.sshserver.close()
                                return
                            print_warn("Could not shut down ssh server: server not set")

                except KeyboardInterrupt:
                    print_warn("SSH connection closed by Ctrl-C")
                    return
                except EOFError:
                    # Ctrl-D : ignore
                    pass


class DemoCLI(BaseCLI):
    """
    Demo some features of the `Python prompt toolkit <https://python-prompt-toolkit.readthedocs.io>`_
    """

    intro = "\nThis is a sample CLI to demonstrate the use of the " \
            "<i>argparseDecorator</i> Library with a SSH Server.\n\n" \
            "Use 'help' for all available commands.\n" \
            "Press <b>Ctrl-C</b> to close connection.\n"
    prompt = "\n<green># </green>"

    # get a reference to the BaseCLI ArgParseDecorator
    cli = BaseCLI.cli

    @cli.command
    async def sleep(self, duration: float) -> None:
        """
        Sleep for some time.
        :param duration: sleep time im duration
        """
        print_info("<info>start sleeping</info>")
        t_start = time.time()
        await asyncio.sleep(duration)
        t_end = time.time()
        print_info(f"woke up after {round(t_end - t_start, 3)} seconds")

    @cli.command
    async def progress(self, ticks: int | ZeroOrOne = 50) -> None:
        """
        Show a progress bar.
        :param ticks: Number of ticks in the progressbar. Default is 50
        """
        # Simple progress bar.
        with ProgressBar() as pb:
            for _ in pb(range(ticks)):
                await asyncio.sleep(0.1)

    @cli.command
    async def input(self) -> None:
        """
        Ask for user input.
        Demo for running a new prompt within commands.
        """
        value = await self.promptsession.prompt_async("Enter some random value: ")
        print_html(f"you have entered a value of {value}")


class SshCLIServer:
    """
    Implementation of the `asyncssh SSHServer <https://asyncssh.readthedocs.io/en/latest/api.html#asyncssh.SSHServer>`_

    :param cli: The CLI to use for incoming ssh connections
    :param port: The port number to use for the server. Defaults to 8222
    :param keyfile: Location of the private key file for the server.
        Defaults to '.ssh_cli_key' in the user home directory.
        A new key will be generated if the keyfile does not exist.
    """

    def __init__(self, cli: BaseCLI, port: int = 8222, keyfile: str = None):
        self.cli = cli
        self.port = port
        self.is_running: Event = asyncio.Event()

        if keyfile:
            self.host_keyfile = keyfile
        else:
            homedir = os.path.expanduser('~')
            self.host_keyfile = os.path.join(homedir, '.ssh_cli_key')

        self._ssh_server = None

    @property
    def ssh_server(self) -> asyncssh.SSHAcceptor:
        return self._ssh_server

    async def close(self):
        self._ssh_server.close()

    def _get_host_key(self) -> asyncssh.SSHKey:
        """
        Load the private key for the SSH server.

        If the key file does not exist or is not a valid key a new private key is generated and
        saved.

        :return: the private key for the ssh server
        """
        try:
            key = asyncssh.read_private_key(self.host_keyfile)
        except (FileNotFoundError, asyncssh.KeyImportError):
            key = asyncssh.generate_private_key('ssh-rsa', 'SSH Server Host Key for ssh_cli_demo')
            try:
                keyfile = open(self.host_keyfile, 'wb')
                keyfile.write(key.export_private_key())
                keyfile.close()
                print(f"SSH Server: New private host key generated and saved as {self.host_keyfile}")
            except Exception as exc:
                print(f"SSH Server: could not write host key to {self.host_keyfile}. Reason: {exc}")

        return key

    async def run_server(self) -> None:
        """
        Start the SSH server and run until the server is shut down.

        :return: Reference to the running server.
        """

        # add something like this to add client authentification:
        # options.authorized_client_keys = ...
        # An alternative would be to subclass PromptToolkitSSHServer and implement the begin_auth() method.

        self._ssh_server: asyncssh.SSHAcceptor = await asyncssh.create_server(
            lambda: PromptToolkitSSHServer(self.cli.cmdloop),
            "",
            self.port,
            server_host_keys=self._get_host_key(),
        )

        # at this point the server is running. Inform interessted listeners.
        self.is_running.set()

        await self._ssh_server.wait_closed()

        self.is_running.clear()


if __name__ == "__main__":
    democli = DemoCLI()
    server = SshCLIServer(cli=democli, port=8301)


    async def start_server():
        ssh_task = asyncio.create_task(server.run_server())

        # wait until the server has started.
        await server.is_running.wait()

        print("SSH Server started on port 8301")

        # Get the ssh_server reference.
        # This is passed on to the CLI so that the CLI can shut down the server if required.
        ssh_server: asyncssh.SSHAcceptor = server.ssh_server
        democli.sshserver = ssh_server

        await asyncio.gather(ssh_task)  # run until the _ssh_server is closed

        print("SSH Server terminated.")


    asyncio.run(start_server())
