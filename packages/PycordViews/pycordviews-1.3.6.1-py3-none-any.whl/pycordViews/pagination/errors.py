from typing import Union

class Py_cordPagination(Exception):
    """
    Main class exception
    """

class PageNumberNotFound(Py_cordPagination):
    """
    If the page number is not found
    """
    def __init__(self, number: Union[int, str]):
        super().__init__(f"Page {number} not found !")