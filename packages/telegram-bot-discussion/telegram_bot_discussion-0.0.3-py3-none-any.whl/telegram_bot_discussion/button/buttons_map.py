from typing import Dict, Type, Union


from .button import Button


class ButtonsMap:
    _buttons: Dict[str, Type[Button]]

    def __init__(
        self,
        *buttons: Type[Button],
    ):
        self._buttons = dict()
        for button in buttons:
            self.add(button)

    def add(
        self,
        x: Type[Button],
    ) -> "ButtonsMap":
        if x.action() not in self._buttons:
            self._buttons[x.action()] = x
        else:
            raise Exception(f"Button '{x.action()}' is already added to `ButtonsMap`.")
        return self

    def search(
        self,
        x: Union[str, Type[Button]],
    ) -> Union[Type[Button], None]:
        if isinstance(x, str):
            return self._buttons.get(x, None)
        if issubclass(x, Button):
            return self._buttons.get(x.__name__, None)
        return None
