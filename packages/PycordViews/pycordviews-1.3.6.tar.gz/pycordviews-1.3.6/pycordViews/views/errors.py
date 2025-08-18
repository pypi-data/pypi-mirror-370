class Py_cordEasyModifiedViews(Exception):
    """
    Main class exception
    """


class CustomIDNotFound(Py_cordEasyModifiedViews):
    def __init__(self):
        super().__init__(f"custom_id not found !")

class CoroutineError(Py_cordEasyModifiedViews):
    def __init__(self, coro):
        super().__init__(f"{coro} is not a coroutine !")
