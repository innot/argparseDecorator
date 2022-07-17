# argparseDecorator Examples

This folder has a few examples to show how the argparseDecorator can be used to implement command line interfaces.

### 1. simple_cli.py

This is a very simple cli that takes input from stdin. It has a few sample commands that show a few basic features of
the argparseDecorator.

### 2. simple_asyncio_demo.py

A very small sample to test using argparseDecorator in am asyncio context.

### 3. ssh_cli.py

is a more involved demo that shows how argparseDecorator can be used to create a CLI that can be accessed remotly via
ssh.

This demo requires the [asyncssh](https://pypi.org/project/asyncssh/) and the
[prompt toolkit](https://pypi.org/project/prompt-toolkit/) libraries.

