class Config:
    """Base class of Telegram-bot configuration."""

    token: str

    def __init__(
        self,
        token: str,
    ):
        """_summary_

        Args:
            token (str): _description_
        """
        self.token = token
