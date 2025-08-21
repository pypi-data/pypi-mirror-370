from typing import Self, Tuple, TypeVar, Union


from telegram import CallbackQuery


from ..coder_interface import CoderInterface


T = TypeVar("T", bound="Params")


class Params:
    action: str

    def __new__(cls, action, **kwargs):
        if getattr(cls, "keys", None) is None:
            raise Exception(f"classmethod `keys()` not defined in class {cls}")
        if getattr(cls, "create", None) is None:
            raise Exception(f"classmethod `create()` not defined in class {cls}")
        if getattr(cls, "fetch", None) is None:
            raise Exception(f"classmethod `fetch()` not defined in class {cls}")
        if cls.keys()[0] != "action":
            raise Exception(f"first `{cls.__name__}.keys()` item must be `action`")
        self = super().__new__(cls)
        self.action = action
        return self

    @classmethod
    def fetch(
        cls,
        callback_query: Union[CallbackQuery, None],
        coder: CoderInterface,
    ) -> Self:
        if not callback_query:
            raise CallbackQueryIsNone()
        if not callback_query.data:
            raise CallbackQueryDataIsNone()
        params_values = coder.fetch_deserialized_data(callback_query.data)
        return cls.create(params_values)

    @classmethod
    def create(cls, fields_values):
        kwargs = dict()
        for i in range(0, len(cls.keys())):
            kwargs[cls.keys()[i]] = fields_values[i]
        return cls(**kwargs)

    @classmethod
    def keys(cls) -> Tuple[str, ...]:
        list_of_attrs = set(cls.__annotations__.keys())
        for i in cls.__mro__[1:]:
            list_of_super_me = (
                getattr(i, "keys")()
                if getattr(i, "keys", None) and callable(getattr(i, "keys"))
                else []
            )
            list_of_attrs = list_of_attrs.union(list_of_super_me)
        list_of_attrs = list(list_of_attrs)
        if "action" in list_of_attrs:
            list_of_attrs.remove("action")
        list_of_attrs.sort()
        list_of_attrs.insert(0, "action")
        return tuple(list_of_attrs)

    def set_action(self, action: str) -> "Params":
        self.action = action
        return self

    def get_action(self) -> str:
        return self.action

    def values(self) -> tuple:
        return tuple(getattr(self, x) for x in self.keys())

    def __str__(self) -> str:
        return str(self.values())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        self_values = self.values()
        other_values = other.values()
        return self_values == other_values


class CallbackQueryDataIsNone(Exception):
    def __str__(self) -> str:
        return "CallbackQuery-data is None"


class CallbackQueryIsNone(Exception):
    def __str__(self) -> str:
        return "CallbackQuery is None"
