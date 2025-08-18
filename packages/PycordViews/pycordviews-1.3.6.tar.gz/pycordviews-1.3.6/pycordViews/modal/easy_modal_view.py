from discord.ui import Modal, InputText
from discord import InputTextStyle, Interaction
from typing import Optional, Callable, Union
from functools import partial
from asyncio import iscoroutinefunction

from .errors import CoroutineError, CustomIDNotFound

class EasyModal(Modal):

    def __init__(self, title: str, custom_id: Optional[str] = None, timeout: Optional[float] = None, global_callable: Optional[Callable] = None):
        """
        Init EasyModal instance.
        :param title: The title set to the Modal
        :param custom_id: ID set to the Modal
        :param timeout: Timeout before the view don't allow response.
        :param global_callable: Asynchronous function called when user submit the modal. Called before all subcoroutine function set for each inputText. Get the instance modal and user interaction in parameters
        """
        super().__init__(title=title, custom_id=custom_id, timeout=timeout)

        self.__callback: dict[str, Union[Callable, None]] = {}

        if global_callable is not None and not iscoroutinefunction(global_callable):
            raise CoroutineError(global_callable)

        self.__global_callable: Optional[Callable] = global_callable

    def add_input_text(self, label: str,
                       style: InputTextStyle = InputTextStyle.short,
                       custom_id: Optional[str] = None,
                       placeholder: Optional[str] = None,
                       min_length: Optional[int] = None,
                       max_length: Optional[int] = None,
                       required: Optional[bool] = True,
                       value: Optional[str] = None,
                       row: Optional[int] = None) -> Callable:
        """
        Add an input text on the Modal.
        :return: set_inputText_callable function to set the callable on the inputText. Require an asynchronous function in parameters.
        """

        x = InputText(label=label, style=style, custom_id=custom_id, placeholder=placeholder, min_length=min_length, max_length=max_length, required=required, row=row, value=value)
        self.__callback[x.custom_id] = None
        self.add_item(x)
        return partial(self.set_inputText_callable, x.custom_id)

    def set_inputText_callable(self, inputText_id: str, _callable: Callable) -> "EasyModal":
        """
        Set an asynchronous function to a single inputText. _callable function was called when modal is completed by the user

        x = EasyModal(title="test")
        # init '8878' custom_id for one inputtext

        x.set_inputText_callable(inputText_id='8878', _callable=set_any)

        async def set_any(data: InputText, interaction: Interaction):
                ...
        """
        if not iscoroutinefunction(_callable):
            raise CoroutineError(_callable)

        if inputText_id not in self.__callback.keys():
            raise CustomIDNotFound(inputText_id)

        self.__callback[inputText_id] = _callable
        return self

    def del_inputText_callable(self, inputText_id: str) -> "EasyModal":
        """
        Delete callable object link to the inputText ID
        :param inputText_id: ID to the inputText
        """
        if inputText_id not in self.__callback.keys():
            raise CustomIDNotFound(inputText_id)

        self.__callback[inputText_id] = None

    async def callback(self, interaction: Interaction):
        """
        Call when the user submit the modal.
        All callable function set to the user get the 'interaction' parameter.
        """

        if self.__global_callable is not None:
            await self.__global_callable(self, interaction)

        for inputTextID, _callable in self.__callback.items():
            if _callable is not None:
                await _callable(self.get_input_text(inputTextID),interaction)



    def get_input_text(self, inputText_id: str) -> InputText:
        """
        Return the inputText associated to the inputText_id
        :param inputText_id: ID inputText
        """
        for i in self.children:
            if i.custom_id == inputText_id:
                return i

        raise CustomIDNotFound(inputText_id)
