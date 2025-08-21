from typing import Union


from telegram import (
    MaybeInaccessibleMessage,
    Message,
    Update,
)


class MessageWasNotFetched(Exception):
    def __str__(self):
        return "Message was not fetched"


def get_message(update: Update) -> Union[MaybeInaccessibleMessage, Message]:
    if update.callback_query and update.callback_query.message:
        return update.callback_query.message
    elif update.message:
        return update.message
    else:
        raise MessageWasNotFetched()
