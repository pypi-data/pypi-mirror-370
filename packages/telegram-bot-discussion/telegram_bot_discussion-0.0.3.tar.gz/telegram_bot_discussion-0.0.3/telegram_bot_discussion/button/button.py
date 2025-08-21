from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Type, Union


from telegram import InlineKeyboardButton, Update
from telegram.ext import CallbackContext


from .button_meta import ButtonMeta, ACTION, LIFE_TIME, TITLE
from .coder_interface import CoderInterface
from .params import Params


class Button(ABC):
    _title: str

    class Meta(ButtonMeta): ...

    chat_id: int
    recipient_id: int

    params: Params

    def __init__(
        self,
        chat_id: int,
        *args,
        **kwargs,
    ):
        self.chat_id = chat_id

    @classmethod
    @abstractmethod
    async def on_click(
        cls,
        update: Update,
        context: CallbackContext,
    ): ...

    @classmethod
    def action(cls) -> str:
        return getattr(cls.Meta, ACTION, cls.__name__.lower())

    @classmethod
    def life_time(cls) -> Union[timedelta, None]:
        return getattr(cls.Meta, LIFE_TIME, None)

    def get_title(self) -> str:
        if getattr(self, "_title", None):
            return getattr(self, "_title")
        if getattr(self.__class__.Meta, TITLE, None):
            return getattr(self.__class__.Meta, TITLE)
        return self.__class__.__name__

    def set_title(self, title: str):
        self._title = title
        return self

    def equals(
        self,
        other: Union[Type["Button"], InlineKeyboardButton],
        callback_data_coder: CoderInterface,
    ) -> bool:
        if not isinstance(other, (self.__class__, InlineKeyboardButton)):
            return False

        if isinstance(other, self.__class__):
            return self.params == other.params

        if isinstance(other, InlineKeyboardButton):
            if isinstance(other.callback_data, str):
                deserialized_values_of_other = (
                    callback_data_coder.fetch_deserialized_data(other.callback_data)
                )
                try:
                    return self.params == self.params.__class__.create(
                        deserialized_values_of_other
                    )
                except IndexError as _:
                    return False

        return False

    def as_button(
        self,
        callback_data_coder: CoderInterface,
    ) -> InlineKeyboardButton:
        serialized_data = callback_data_coder.serialize(
            *self.params.values(),
        )
        signature = callback_data_coder.get_signature(
            self.chat_id,
            self.recipient_id,
            serialized_data,
        )
        callback_data = callback_data_coder.sign(
            signature,
            serialized_data,
        )
        return InlineKeyboardButton(
            self.get_title(),
            callback_data=callback_data,
        )
