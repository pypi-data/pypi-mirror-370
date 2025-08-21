from datetime import timedelta


ACTION: str = "action"
LIFE_TIME: str = "life_time"
TITLE: str = "title"


class ButtonMeta:
    action: str
    life_time: timedelta
    title: str
