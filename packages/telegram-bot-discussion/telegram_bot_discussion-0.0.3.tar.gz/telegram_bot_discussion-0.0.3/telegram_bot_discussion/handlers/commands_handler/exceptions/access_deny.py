from typing import Type, Union


from ....command.command import Command


class CommandClassAccessDeny(Exception):
    user_id: int
    command_class: Union[str, Type[Command]]

    def __init__(
        self,
        user_id: int,
        command_class: Union[str, Type[Command]],
    ):
        self.user_id = user_id
        self.command_class = command_class

    def __str__(self) -> str:
        return f"Access to command `{self.command_class}` was deny for user `{self.user_id}`"
