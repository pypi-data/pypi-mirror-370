from typing import Union


from telegram import (
    Update,
    User,
)
from telegram.ext import CallbackContext


__FROM_ID = "from_id"


class FromUserWasNotFetched(Exception):
    def __str__(self):
        return "FromUser was not fetched"


def get_from_user(update: Update) -> User:
    if update.message and update.message.from_user:
        return update.message.from_user
    elif update.callback_query and update.callback_query.from_user:
        return update.callback_query.from_user
    else:
        raise FromUserWasNotFetched()


def get_from_id(
    update: Update,
    context: Union[CallbackContext, None] = None,
) -> int:
    if update.message and update.message.from_user:
        if context:
            context.bot_data[__FROM_ID] = update.message.from_user.id
        return update.message.from_user.id
    # TODO: test
    elif update.callback_query and update.callback_query.from_user:
        if context:
            context.bot_data[__FROM_ID] = update.callback_query.from_user.id
        return update.callback_query.from_user.id
    elif context and context.bot_data.get(__FROM_ID):
        return context.bot_data.get(__FROM_ID)
    else:
        raise FromUserWasNotFetched()
