from typing import Type, Union


from ....button.button import Button


class ButtonClassLifeTimeOverflow(Exception):
    button_class: Union[str, Type[Button]]

    def __init__(
        self,
        button_class: Union[str, Type[Button]],
    ):
        self.button_class = button_class

    def __str__(self) -> str:
        return f"Lifetime of button `{self.button_class}` is overflow.`"
