class ButtonDataSignificationError(Exception):
    user_id: int
    data: str

    def __init__(
        self,
        user_id: int,
        data: str,
    ):
        self.user_id = user_id
        self.data = data

    def __str__(self) -> str:
        return f"Not valid button-sign `{self.data.encode()}` by user `{self.user_id}` click"
