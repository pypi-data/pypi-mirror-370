from typing import Type, Union


from ....button.button import Button


class ButtonClassIsNotRegistered(Exception):
    button_class: Union[str, Type[Button]]

    def __init__(
        self,
        button_class: Union[str, Type[Button]],
    ):
        self.button_class = button_class

    def __str__(self) -> str:
        return f"Button `{self.button_class}` is not registered.`"
