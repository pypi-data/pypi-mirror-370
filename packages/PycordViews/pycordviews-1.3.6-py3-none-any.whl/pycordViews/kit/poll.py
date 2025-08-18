from ..views.easy_modified_view import EasyModifiedViews
from ..views.errors import CoroutineError
from discord.ui.button import Button, ButtonStyle
from discord import Emoji, PartialEmoji, Embed, Color
from typing import Optional, Callable, Union
from asyncio import iscoroutinefunction


class Poll:

    def __init__(self, timeout: Optional[float] = None, unique_vote: bool = True):
        """
        Class instance to make poll with buttons
        :param timeout: Time before end the view
        :param unique_vote: Set True to make vote unchangeable
        """
        self.yes_count: int = 0
        self.no_count: int = 0
        self.__unique_vote: bool = unique_vote
        self.__view = EasyModifiedViews(disabled_on_timeout=True, timeout=timeout)
        self.__button_yes = Button(label='Yes', emoji='✅', custom_id='Poll_yes', style=ButtonStyle.green)
        self.__button_no = Button(label='No', emoji='❌', custom_id='Poll_no', style=ButtonStyle.gray)
        self.__view.add_items(self.__button_yes, self.__button_no)
        self.__view.set_callable('Poll_yes', _callable=self.yes)
        self.__view.set_callable('Poll_no', _callable=self.no)
        self.__view.call_on_timeout(self._result) # asynchrone fonction quand la view est arrivé à son timeout
        self.__clicked_members: list[int] = []

    def add_answer_button(self, label: str,
                            custom_id: str,
                            emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
                            style: ButtonStyle = ButtonStyle.secondary,
                            row: Optional[int] = None,
                            _callable: Optional[Callable] = None) -> Button:
        """
        Create a new answer button and add it in the view.
        :param label: Button label
        :param custom_id: Button ID
        :param emoji: Button emoji
        :param style: Button style
        :param row: Button row
        :param _callable: Asynchronous function linked to the button interaction. It's called when the button is pressed
        """

        if not iscoroutinefunction(_callable):
            raise CoroutineError(_callable)

        b = Button(label=label, emoji=emoji, style=style, row=row, custom_id=custom_id)
        self.__view.add_items(b)
        self.__view.set_callable(custom_id, _callable=_callable)

        return b


    def set_yes_button(self, label: Optional[str] = None,
                       emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
                       style: Optional[ButtonStyle] = None,
                       row: Optional[int] = None,
                       _callable: Optional[Callable] = None):
        """
        Set yes button parameters (he didn't change dynamically if the view was sent before)
        :param label: Button label
        :param emoji: Button emoji
        :param style: Button style
        :param row: Button row
        :param _callable: Asynchronous function linked to the button interaction. It's called when the button is pressed
        """
        self.__button_yes.emoji = emoji if emoji is not None else self.__button_yes.emoji
        self.__button_yes.style = style if style is not None else self.__button_yes.style
        self.__button_yes.label = label if label is not None else self.__button_yes.label
        self.__button_yes.row = row if row is not None else self.__button_yes.row

        if not iscoroutinefunction(_callable):
            raise CoroutineError(_callable)

        if _callable is not None:
            self.__view.set_callable(self.__button_yes.custom_id, _callable=_callable)

    def set_no_button(self, label: Optional[str] = None,
                        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
                        style: Optional[ButtonStyle] = None,
                        row: Optional[int] = None,
                        _callable: Optional[Callable] = None):
        """
        Set no button parameters (he didn't change dynamically if the view was sent before)
        :param label: Button label
        :param emoji: Button emoji
        :param row: Button row
        :param style: Button style
        :param _callable: Asynchronous function linked to the button interaction. It's called when the button is pressed
        """
        self.__button_no.emoji = emoji if emoji is not None else self.__button_no.emoji
        self.__button_no.style = style if style is not None else self.__button_no.style
        self.__button_no.label = label if label is not None else self.__button_no.label
        self.__button_no.row = row if row is not None else self.__button_no.row

        if not iscoroutinefunction(_callable):
            raise CoroutineError(_callable)

        if _callable is not None:
            self.__view.set_callable(self.__button_no.custom_id, _callable=_callable)

    async def yes(self, button, interaction, data):
        """
        Base asynchronous function when "yes" button is pressed.
        Increment “yes_count” attribute when pressed and respond with an ephemeral message.
        This function can be changed.
        """
        if self.__unique_vote and interaction.user.id in self.__clicked_members:
            await interaction.response.send_message(f"You have already voted !", ephemeral=True)
            return
        self.yes_count += 1
        self.__clicked_members.append(interaction.user.id)
        await interaction.response.send_message(f"You have selected : {button.label}", ephemeral=True)

    async def no(self, button, interaction, data):
        """
        Base asynchronous function when "no" button is pressed.
        Increment “yes_count” attribute when pressed and respond with an ephemeral message.
        This function can be changed.
        """
        if self.__unique_vote and interaction.user.id in self.__clicked_members:
            await interaction.response.send_message(f"You have already voted !", ephemeral=True)
            return
        self.yes_count += 1
        self.__clicked_members.append(interaction.user.id)
        await interaction.response.send_message(f"You have selected : {button.label}", ephemeral=True)

    async def _result(self, ctx):
        """
        Asynchronous base function called when timeout is reached.
        :param ctx: Actual command context
        """
        embed = Embed(title="Poll ended !",
                      description=f"## Results :\n"
                                  f" `-` {self.__button_yes.emoji.name} {self.__button_yes.label} -> `{self.yes_count}`\n"
                                  f" `-` {self.__button_no.emoji.name} {self.__button_no.label} -> `{self.no_count}`",
                      color=Color.gold())

        await self.__view.message.reply(embed=embed)

    @property
    def get_view(self) -> EasyModifiedViews:
        """
        Get the current view
        """
        return self.__view
