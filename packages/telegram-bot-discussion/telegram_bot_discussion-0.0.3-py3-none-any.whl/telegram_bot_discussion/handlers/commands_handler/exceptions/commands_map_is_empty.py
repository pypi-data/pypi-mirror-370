class CommandsMapIsEmpty(Exception):
    def __str__(self) -> str:
        return f"Commands map is empty."
