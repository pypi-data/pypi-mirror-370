from typing import Optional
from ..views.easy_modified_view import EasyModifiedViews
from discord import Interaction, ButtonStyle
from discord.ui import Button
from asyncio import wait_for, Future, get_event_loop, TimeoutError


class Confirm:

    def __init__(self, timeout: Optional[float] = None, disable_on_click: bool = False):
        """
        Init a Confirm class instance kit.
        :param timeout: Time before end the view
        """
        self.__timeout: float = timeout
        self.__disable_on_click: bool = disable_on_click
        self.__view: EasyModifiedViews = EasyModifiedViews(disabled_on_timeout=True, timeout=timeout, call_on_timeout=self._on_timeout)
        self.__button_confirm: Button = Button(label='Confirm', emoji='✅', style=ButtonStyle.green, custom_id='Confirm_confirm')
        self.__button_denied: Button = Button(label='Denied', emoji='❌', style=ButtonStyle.gray, custom_id='Confirm_denied')
        self.__view.add_items(self.__button_confirm, self.__button_denied)
        self.__view.set_callable(self.__button_confirm.custom_id, _callable=self._confirm)
        self.__view.set_callable(self.__button_denied.custom_id, _callable=self._denied)

        self.__future: Future = get_event_loop().create_future()

    async def _confirm(self, button: Button, interaction: Interaction, data):
        """
        Base asynchronous _confirm function called when button is pressed
        """
        if not self.__future.done():
            self.__future.set_result(True)
        if self.__disable_on_click:
            await self.__view.disable_items('Confirm_confirm', 'Confirm_denied')
        await interaction.response.defer()

    async def _denied(self, button: Button, interaction: Interaction):
        """
        Base asynchronous _denied function called when button is pressed
        """
        if not self.__future.done():
            self.__future.set_result(False)
        if self.__disable_on_click:
            await self.__view.disable_items('Confirm_confirm', 'Confirm_denied')
        await interaction.response.defer()

    async def wait_for_response(self) -> Optional[bool]:
        """
        Wait and return the result of current button pressed.
        :return: True if it is confirmed, False else. If timeout is reached, return None
        """
        try:
            return await wait_for(self.__future, timeout=self.__timeout)

        except TimeoutError:
            return None

    async def _on_timeout(self, ctx):
        """
        Called when the timeout is reached to end the Future
        """
        if not self.__future.done():
            self.__future.set_result(None)

    @property
    def get_view(self) -> EasyModifiedViews:
        """
        Get the current view
        """
        return self.__view
