from datetime import datetime, UTC
from typing import Dict, Tuple, Type, Union


from telegram import CallbackQuery, Update, User
from telegram.ext import CallbackContext


from ...bot.contextual import Contextual
from ...button.button import Button
from ...button.buttons_map import ButtonsMap
from ...button.coder_interface import CoderInterface
from ...button.params import Params
from ...dialogue.dialogue import Polemic
from ...functions import (
    get_chat_id,
    get_from_id,
)
from ...logger.logger_interface import LoggerInterface
from .exceptions import (
    ButtonClassAccessDeny,
    ButtonClassIsNotRegistered,
    ButtonClassLifeTimeOverflow,
    ButtonDataSignificationError,
    ButtonsMapIsEmpty,
)


class DiskutoInterface:
    def get_dialogues(self) -> Dict[int, Polemic]: ...
    def get_logger(self) -> LoggerInterface: ...
    def get_buttons_handler(self) -> "ButtonsHandler": ...


class ButtonsHandler:
    buttons_map: ButtonsMap
    coder: CoderInterface

    def __init__(
        self,
        coder: CoderInterface,
        buttons_map: ButtonsMap,
    ):
        self.coder = coder
        self.buttons_map = buttons_map

    def set_buttons(self, buttons_map: ButtonsMap):
        self.buttons_map = buttons_map
        return self

    async def access_control_list(
        self,
        context: CallbackContext,
        user_id: int,
        button_class: Type[Button],
    ) -> bool:
        _, _, _ = context, user_id, button_class
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

        callback_query: Union[CallbackQuery, None] = update.callback_query
        if not callback_query:
            return
        await callback_query.answer()
        if not callback_query.data:
            return
        from_user: Union[User, None] = callback_query.from_user
        if not from_user:
            return

        await callback_query.answer()

        if not self.buttons_map:
            raise ButtonsMapIsEmpty()

        diskuto: DiskutoInterface = Contextual[DiskutoInterface](context)()
        if not diskuto.get_buttons_handler().coder.check_signature(
            get_chat_id(update),
            get_from_id(update),
            callback_query.data,
        ):
            raise ButtonDataSignificationError(from_user.id, callback_query.data)

        params = Params.fetch(
            callback_query=callback_query,
            coder=self.coder,
        )
        diskuto.get_logger().debug(f"Params {params}")

        button_action = params.action
        button_class = self.buttons_map.search(button_action)

        if button_class is None:
            raise ButtonClassIsNotRegistered(button_action)

        if not await self.access_control_list(
            context,
            from_user.id,
            button_class,
        ):
            raise ButtonClassAccessDeny(from_user.id, button_action)
        life_time = button_class.life_time()
        if (
            callback_query.message
            and life_time
            and datetime.now(tz=UTC) > callback_query.message.date + life_time
        ):
            raise ButtonClassLifeTimeOverflow(button_action)
        await button_class.on_click(update, context)
