from telegram import InlineKeyboardMarkup


from telegram_bot_discussion.button.button import Button
from telegram_bot_discussion.button.coder_interface import CoderInterface


def change_button_at_keyboard(
    where: InlineKeyboardMarkup,
    change_from_button: Button,
    change_to_button: Button,
    coder: CoderInterface,
) -> InlineKeyboardMarkup:
    reply_markup_inline_keyboard = list(map(list, where.inline_keyboard))
    was_change = False
    for row_id, reply_markup_buttons_row in enumerate(reply_markup_inline_keyboard):
        for column_id, reply_markup_button in enumerate(reply_markup_buttons_row):
            if change_from_button.equals(
                reply_markup_button,
                coder,
            ):
                reply_markup_inline_keyboard[row_id][column_id] = (
                    change_to_button.as_button(coder)
                )
                was_change = True
    if was_change:
        return InlineKeyboardMarkup(reply_markup_inline_keyboard)
    return where  # None
