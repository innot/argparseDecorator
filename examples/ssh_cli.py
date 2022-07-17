#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or
#  go to <https://opensource.org/licenses/MIT>.
#

"""
Example of running a argparseDecorator CLI in an asyncssh server.

This is still work in progress.

"""
import asyncio
import os
import time
from typing import TextIO

import asyncssh
from prompt_toolkit import print_formatted_text, PromptSession, HTML
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.contrib.ssh import PromptToolkitSSHServer, PromptToolkitSSHSession

from argparsedecorator import *

# from sshPromptUI import CommandParser

intro = "\n<grey>This is a sample CLI to demonstrate a the use of the <i>argparseDecorator</i> Library with a SSH Server.\n" \
        "Press <b>Ctrl-C</b> to close connection.</grey>\n"
prompt = "\n<green># </green>"


class CLI:
    cli = ArgParseDecorator()

    @property
    def stdout(self) -> TextIO:
        return self._stdout

    @stdout.setter
    def stdout(self, stdout: TextIO):
        self._stdout = stdout

    @property
    def command_dict(self):
        # make the command-dict accessible
        return self.cli.command_dict

    @cli.command
    def exit(self) -> str:
        """exit closes this ssh connection."""
        return "exit"

    @cli.command
    def shutdown(self) -> str:
        """shutdown the ssh server. All connections will be disconnected."""
        return "shutdown"

    @cli.command
    def sleep(self, seconds: float):
        """sleep for n seconds. Test for command interrupts."""
        print(f"sleeping for {seconds} seconds")
        time.sleep(seconds)
        print("sleep finished")

    def error_handler(self, exc):
        print_formatted_text(HTML(f"<red>{str(exc)}</red>"))

    def execute(self, cmdline):
        return self.cli.execute(cmdline, base=self, error_handler=self.error_handler, stdout=self._stdout)


class SshServer:

    def __init__(self,
                 cli: CLI,
                 port: int = 8222,
                 keyfile: str = None):
        self.cli = cli
        self.port = port

        if keyfile:
            self.host_keyfile = keyfile
        else:
            homedir = os.path.expanduser('~')
            self.host_keyfile = os.path.join(homedir, '.ssh_cli_key')

    async def interact(self, ssh_session: PromptToolkitSSHSession) -> None:
        """
        The application interaction.
        This will run automatically in a prompt_toolkit AppSession, which means
        that any prompt_toolkit application (dialogs, prompts, etc...) will use the
        SSH channel for input and output.
        """

        # tell the CLI about stdout (if not using the print_formatted_text() function)
        self.cli.stdout = ssh_session.app_session.output
        self.cli.stdin = ssh_session.app_session.input

        # inititialize command completion
        # List (actually a dict) of all implemented commands is provided by the ArgparseDecorator and
        # used by the prompt_toolkit
        all_commands = self.cli.command_dict
        completer = NestedCompleter.from_nested_dict(all_commands)

        self.prompt_session = PromptSession(refresh_interval=0.5)

        print_formatted_text(HTML(intro))
        prompt_formatted = HTML(prompt)

        while True:
            try:
                command = await self.prompt_session.prompt_async(prompt_formatted, completer=completer)
                if command:
                    result = self.cli.execute(command)
                    if result == "exit":
                        # close current connection
                        print_formatted_text(HTML("<orange>Closing ssh connection</orange>"))
                        return

                    if result == "shutdown":
                        print_formatted_text(HTML("<orange>SSH Server is shutting down</orange>"))
                        await asyncio.sleep(0)  # yield so that output is transmitted before event
                        self._shutdown_event.set()
                        return

            except KeyboardInterrupt:
                print_formatted_text("ssh connection closed by Ctrl-C")
                self._running = False
            except EOFError:
                # Ctrl-D : ignore
                pass

    async def _start_server(self):
        await asyncssh.create_server(
            lambda: PromptToolkitSSHServer(self.interact),
            "",
            self.port,
            server_host_keys=self._get_host_key(),
        )

    def _get_host_key(self) -> asyncssh.SSHKey:
        """load the private key for the SSH server.
        Default location is the file '.ssh_cli_key' file in the home directory of the user.
        Other location can be specified with the :meth:'keyfile' property (e.g. for testing).
        If the key file does not exist or is not a valid key a new private key is generated and
        saved.

        :return: the private key for the ssh server
        :rtype: asyncssh.SSHKey
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

    async def run(self):
        # this event is set to signal that the server should be shut down.
        self._shutdown_event = asyncio.Event()

        # create the server and run it as a task
        ssh_task = asyncio.create_task(self._start_server())

        print("SSH Server started on port 8301")

        # now let the ssh server run until the 'shutdown' command is issued
        # which will in turn set the shutdown_event.
        await self._shutdown_event.wait()

        # put other cleanup code here

        print("SSH Server terminated.")


if __name__ == "__main__":
    server = SshServer(cli=CLI(), port=8301)
    asyncio.run(server.run())
