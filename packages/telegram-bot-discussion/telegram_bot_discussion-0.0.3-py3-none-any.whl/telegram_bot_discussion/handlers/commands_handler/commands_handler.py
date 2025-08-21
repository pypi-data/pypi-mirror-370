from typing import Tuple, Type, Union


from telegram import Update, Message
from telegram.ext import CallbackContext


from ...command.command import Command
from ...command.commands_map import CommandsMap
from .exceptions import (
    CommandClassAccessDeny,
    CommandClassIsNotRegistered,
    CommandsMapIsEmpty,
)
from ...functions import get_from_id


class CommandsHandler:
    commands_map: Union[CommandsMap, None] = None

    def __init__(
        self,
        commands_map: Union[CommandsMap, None] = None,
    ):
        self.commands_map = commands_map

    def set_commands(self, commands_map: CommandsMap):
        self.commands_map = commands_map
        return self

    async def access_control_list(
        self,
        context: CallbackContext,
        user_id: int,
        command: Type[Command],
    ) -> bool:
        _, _, _ = context, user_id, command
        return True

    async def middleware(
        self,
        update: Update,
        context: CallbackContext,
    ) -> Union[Tuple[Update, CallbackContext], None]:
        return update, context

    async def handle(
        self,
        update: Update,
        context: CallbackContext,
    ):
        if (
            await self.middleware(
                update,
                context,
            )
            is None
        ):
            return

        message: Union[Message, None] = update.message
        if not message:
            return
        if not message.text:
            return
        if not message.text.startswith("/"):
            return
        command_name = message.text
        await self._handle_by_name(update, context, command_name)

    async def _handle_by_name(
        self,
        update: Update,
        context: CallbackContext,
        command_name: str,
    ):
        if not isinstance(self.commands_map, CommandsMap):
            raise CommandsMapIsEmpty()

        command = self.commands_map.search(command_name)
        if command is None:
            raise CommandClassIsNotRegistered(command_name)

        from_id: int = get_from_id(update)

        if await self.access_control_list(
            context,
            from_id,
            command,
        ):
            await command().on_call(
                update,
                context,
            )
        else:
            raise CommandClassAccessDeny(
                from_id,
                command_name,
            )
