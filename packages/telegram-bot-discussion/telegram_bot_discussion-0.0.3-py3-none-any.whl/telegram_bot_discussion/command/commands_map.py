from typing import Dict, Type, Union


from .command import Command


class CommandsMap:
    _commands: Dict[str, Type[Command]]

    def __init__(
        self,
        *commands: Type[Command],
    ):
        self._commands = dict()
        for command in commands:
            self.add(command)

    def add(
        self,
        x: Type[Command],
    ) -> "CommandsMap":
        if x.action() not in self._commands:
            self._commands[x.action()] = x
        else:
            raise Exception(
                f"Command '{x.action()}' is already added to `CommandsMap`."
            )
        return self

    def search(
        self,
        x: Union[str, Type[Command]],
    ) -> Union[Type[Command], None]:
        if isinstance(x, str):
            return self._commands.get(x, None)
        if issubclass(x, Command):
            return self._commands.get(x.__name__, None)
        return None
