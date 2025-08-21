from typing import Sequence, Union


from telegram import ReplyKeyboardMarkup


from .command import Command


class CommandsMenu:
    _commands: Sequence[Sequence[Command]] = []

    def __init__(self, commands: Union[Sequence[Sequence[Command]], None] = None):
        if commands is None:
            self._commands = self.__class__._commands
        else:
            self._commands = commands

    def set_commands(self, commands: Sequence[Sequence[Command]]) -> "CommandsMenu":
        self._commands = commands
        return self

    def get_commands(self) -> Sequence[Sequence[Command]]:
        return self._commands

    def as_keyboard(self) -> ReplyKeyboardMarkup:
        str_commands: Sequence[Sequence[str]] = []
        for row in self.get_commands():
            str_commands_row: Sequence[str] = []
            for command in row:
                str_commands_row.append(command.action())
            str_commands.append(str_commands_row)
        return ReplyKeyboardMarkup(
            str_commands,
            one_time_keyboard=True,
            resize_keyboard=True,
            is_persistent=False,
        )
