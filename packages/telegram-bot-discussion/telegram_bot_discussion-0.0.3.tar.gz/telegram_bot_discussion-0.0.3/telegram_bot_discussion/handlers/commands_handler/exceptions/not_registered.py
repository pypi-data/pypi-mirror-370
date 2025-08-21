from typing import Type, Union


from ....command.command import Command


class CommandClassIsNotRegistered(Exception):
    command_class: Union[str, Type[Command]]

    def __init__(
        self,
        command_class: Union[str, Type[Command]],
    ):
        self.command_class = command_class

    def __str__(self) -> str:
        return f"Command class `{self.command_class}` is not registered."
