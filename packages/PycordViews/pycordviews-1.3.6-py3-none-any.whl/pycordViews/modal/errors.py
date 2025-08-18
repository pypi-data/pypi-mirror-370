class ModalError(Exception):
    pass


class CustomIDNotFound(ModalError):
    def __init__(self, customID: str):
        super().__init__(f"'{customID}' ID not found !")


class CoroutineError(ModalError):
    def __init__(self, coro):
        super().__init__(f"{coro} is not a coroutine !")
