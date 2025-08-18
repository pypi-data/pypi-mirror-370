from typing import Any
class MenuError(Exception):
    pass

class NotCoroutineError(MenuError):
    def __init__(self, callable: Any):
        """
        If callable is not a coroutine
        """
        super().__init__(f"{callable} is not a coroutine")

class ComponentTypeError(MenuError):
    def __init__(self):
        """
        If the component type is not a string_select
        """
        super().__init__(f"Only string select type is available")
