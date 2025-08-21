from abc import ABC, abstractmethod
from typing import Union


from telegram import Message, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext


from telegram_bot_discussion.functions import get_message


class ReplicaMeta: ...


class Replica(ABC):
    class Meta(ReplicaMeta): ...

    def __str__(self):
        return f"{self.__class__}"

    @abstractmethod
    async def as_reply(self, *args, **kwargs): ...


class EmptyReplica(Replica):
    async def as_reply(self, *args, **kwargs): ...


class AutoReply(Replica):
    text: str = ""

    def __init__(self, text: Union[str, None] = None):
        if text is None:
            text = "✓"
        self.text = text

    async def as_reply(self, update: Update, context: CallbackContext):
        message = get_message(update)
        if isinstance(message, Message):
            _ = await message.reply_text(
                text=self.text,
                reply_to_message_id=message.id,
                allow_sending_without_reply=True,
            )


class CleanReplica(Replica):

    async def as_reply(self, update: Update, context: CallbackContext):
        message = get_message(update)
        if isinstance(message, Message):
            new_message = await message.reply_text(
                text="...",
                reply_markup=ReplyKeyboardRemove(),
            )
            await new_message.delete()


class NoNeedReactionReplica(Replica):
    replica: Replica

    def __init__(self, replica: Replica):
        self.replica = replica

    async def as_reply(self, *args, **kwargs):
        return await self.replica.as_reply(*args, **kwargs)


class StopReplica(NoNeedReactionReplica): ...
