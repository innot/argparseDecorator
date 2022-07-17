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
from typing import TextIO, Optional, Any, Dict, Awaitable

import asyncssh
from prompt_toolkit import print_formatted_text, PromptSession, HTML
from prompt_toolkit.completion import NestedCompleter, Completer
from prompt_toolkit.contrib.ssh import PromptToolkitSSHServer, PromptToolkitSSHSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import yes_no_dialog, ProgressBar
from prompt_toolkit.styles import Style

from argparsedecorator import *

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
    """"""

    intro = "\nThis is a basic SSH CLI.\nType Ctrl-C to exit.\n"
    """Intro text displayed at the start of a new session. Override as required."""

    prompt = "\n<green># </green>"
    """Prompt text to display. Override as required."""

    cli = ArgParseDecorator()
    """The :class:`ArgParseDecorator` used to decorate command methods."""

    def __init__(self):
        self.stdout: TextIO = sys.stdout
        self.stdin: TextIO = sys.stdin
        self.promptsession = None
        self.server: Optional[asyncssh.SSHAcceptor] = None
        self.completer: Optional[Completer] = None

    @property
    def command_dict(self) -> Dict[str, Optional[Dict]]:
        """

        :return:
        """
        # make the command-dict accessible
        return self.cli.command_dict

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
    async def start_prompt_session(self) -> PromptSession:
        """
        Start a new prompt session.

        Called from :meth:`cmdloop` for each new session.

        By default it will return a simple PromptSession without any argument.
        Override to customize the prompt session.

        :return: a new PromptSession object
        """
        return PromptSession()

    # noinspection PyMethodMayBeStatic
    async def run_prompt(self, prompt_session: PromptSession) -> Any:
        """
        Display a prompt to the remote user and wait for his command.

        The default implementation has only a comand name completer.
        Override to implement other, more advanced features.

        :return: The command entered by the user
        """
        # inititialize command completion
        # List (actually a dict) of all implemented commands is provided by the ArgparseDecorator and
        # used by the prompt_toolkit
        if not self.completer:
            # create the command dict only once
            all_commands = self.cli.command_dict
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
                            if self.server:
                                print_warn("SSH Server is shutting down")
                                self.server.close()
                                return
                            print_warn("Could not shut down ssh server: server not set")

                except KeyboardInterrupt:
                    if self.ctrl_c_handler():
                        print_warn("SSH connection closed by Ctrl-C")
                        return
                    # else ignore
                except EOFError:
                    # Ctrl-D : ignore
                    pass

    # noinspection PyMethodMayBeStatic
    def ctrl_c_handler(self) -> bool:
        """
        Called when a CTRL-C (Keyboard Interrupt) is received.

        If :code:`True` is returned the current session is closed.
        If :code:`False` is returned the CTRL-C is ignored.

        Override if required for more elaborate handling of CTRL-C.
        :return: default :code:`True`
        """
        return True


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
        """
        value = await self.promptsession.prompt_async("Enter some random value: ")
        print_html(f"you have entered a value of {value}")


class SshCLIServer:
    """
    Implementation of the `asyncssh SSHServer <https://asyncssh.readthedocs.io/en/latest/api.html#sshserver>`_

    :param cli: The CLI to use for incoming ssh connections
    :param port: The port number to use for the server. Defaults to 8222
    :param keyfile: Location of the private key file for the server.
        Defaults to '.ssh_cli_key' in the user home directory.
        A new key will be generated if the keyfile does not exist.
    """

    def __init__(self,
                 cli: BaseCLI,
                 port: int = 8222,
                 keyfile: str = None):
        self.cli = cli
        self.port = port

        if keyfile:
            self.host_keyfile = keyfile
        else:
            homedir = os.path.expanduser('~')
            self.host_keyfile = os.path.join(homedir, '.ssh_cli_key')

    async def start(self) -> asyncssh.SSHAcceptor:
        """
        Start the SSH server.

        :return: Reference to the running server.
        """
        self.ssh_server: asyncssh.SSHAcceptor = await asyncssh.create_server(
            lambda: PromptToolkitSSHServer(self.cli.cmdloop),
            "",
            self.port,
            server_host_keys=self._get_host_key(),
        )
        return self.ssh_server

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


if __name__ == "__main__":
    democli = DemoCLI()
    server = SshCLIServer(cli=democli, port=8301)


    async def start_server():
        ssh_task = asyncio.create_task(server.start())

        # The ssh_task will start the actual server in the background and then finish quickly.
        # Wait for it to finish before continuing
        try:
            await asyncio.wait_for(ssh_task, 10)
        except TimeoutError:
            print("SSH Server could not be started")
            sys.exit(-1)

        print("SSH Server started on port 8301")

        # Get the ssh_server reference.
        # This is used
        # a) to wait for it to close to cleanly shut down this programm
        # b) for the cli to be able to shut down the server (via the 'shutdown' command supplied by default)
        ssh_server: asyncssh.SSHAcceptor = server.ssh_server
        democli.server = ssh_server

        await asyncio.gather(ssh_server.wait_closed())  # run until the ssh_server is closed

        print("SSH Server terminated.")


    asyncio.run(start_server())
