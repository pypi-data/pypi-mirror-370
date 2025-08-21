from typing import Type, Union


from ....button.button import Button


class ButtonClassAccessDeny(Exception):
    user_id: int
    button_class: Union[str, Type[Button]]

    def __init__(
        self,
        user_id: int,
        button_class: Union[str, Type[Button]],
    ):
        self.user_id = user_id
        self.button_class = button_class

    def __str__(self) -> str:
        return (
            f"Access to button `{self.button_class}` was deny for user `{self.user_id}`"
        )
