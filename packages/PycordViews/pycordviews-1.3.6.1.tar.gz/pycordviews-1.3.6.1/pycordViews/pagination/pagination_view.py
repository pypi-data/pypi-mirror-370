from ..views.easy_modified_view import EasyModifiedViews
from discord import ButtonStyle, Interaction, TextChannel, Member, ApplicationContext, File, Embed
from discord.ui import Button
from .errors import PageNumberNotFound
from .page import Page

from typing import Union, Any, Optional


class Pagination:
    """
    Class
    -------------
    Allows you to easily setup a view pagination
    """

    def __init__(self, timeout: Union[float, None] = None, disabled_on_timeout: bool = False, default_row: int = 0):
        """
        Initialisation for pagination
        :param timeout: The time before disable items on the view
        :param disabled_on_timeout: If timeout is done, disable all items
        """
        self.__view = EasyModifiedViews(timeout, disabled_on_timeout=disabled_on_timeout)

        self.__view.add_items(Button(label='⏮', row=default_row, custom_id='back+', style=ButtonStyle.blurple))
        self.__view.add_items(Button(label='◀', row=default_row, custom_id='back', style=ButtonStyle.blurple))
        self.__view.add_items(Button(label='None', row=default_row, custom_id='counter', style=ButtonStyle.gray, disabled=True))
        self.__view.add_items(Button(label='▶', row=default_row, custom_id='forward', style=ButtonStyle.blurple))
        self.__view.add_items(Button(label='⏭', row=default_row, custom_id='forward+', style=ButtonStyle.blurple))
        self.__view.set_callable('back+', 'back', 'forward', 'forward+', _callable=self.__turn_page)

        self.__pages: list[Page] = []
        self.__current_page: int = 0

    def add_page(self, content: Optional[str] = None, embed: Optional[Embed] = None, embeds: list[Embed] = [], file: Optional[File] = None,  files: Optional[list[File]] = [], view: Optional[EasyModifiedViews] = None) -> "Pagination":
        """
        Adds a page (in a list) as if this function directly sent the message
        Pages are just modified and not reset ! Don't forget to disable embeds or content if the page don't need this.

        add_page(content="my message", embeds=[embed1, embed2], ...)
        """
        self.__pages.append(Page(content=content, embed=embed, embeds=embeds, file=file, files=files, view=view))
        self.__view.get_ui('counter').label = f"{self.__current_page+1}/{len(self.__pages)}"
        return self

    def delete_pages(self, *page_numbers: Union[str, int]) -> "Pagination":
        """
        Deletes pages in the order in which they were added
        **Start to 0 !**

        delete_pages(0,1,2,3,...)
        """
        nbr_pages = len(self.__pages)-1
        for page_number in page_numbers:

            if page_number < 0 or page_number > nbr_pages:
                raise PageNumberNotFound(page_number)

            del self.__pages[page_number]
        self.__view.get_ui('counter').label = f"{self.__current_page+1}/{len(self.__pages)}"
        return self

    async def __turn_page(self, button, interaction: Interaction, data):
        """
        Turn the page when button is pressed
        """
        page_count = len(self.__pages)

        if page_count <= 1:
            await self.__view.shutdown()
            await interaction.response.defer(invisible=True)
            return

            # Update the current page based on the button pressed

        if interaction.custom_id == 'back+':  # Go to the first page
            self.__current_page = 0

        elif interaction.custom_id == 'back':  # Go to the previous page
            self.__current_page = max(0, self.__current_page - 1)

        elif interaction.custom_id == 'forward':  # Go to the next page
            self.__current_page = min(page_count-1, self.__current_page + 1)

        elif interaction.custom_id == 'forward+':  # Go to the last page
            self.__current_page = page_count-1

        self.__view.get_ui('counter').label = f"{self.__current_page + 1}/{len(self.__pages)}"

        c = self.__pages[self.__current_page]

        await interaction.message.edit(

            content=c.content,
            embeds=c.embeds,
            files=c.files,

            view=self.__view.copy() + self.__pages[self.__current_page].get_page_view,

        )

        # Acknowledge the interaction
        await interaction.response.defer(invisible=True)

    async def send(self, target: Union[Member, TextChannel]) -> Any:
        """
        Send pagination without introduction message.
        :param target: The member or channel to send the pagination
        """
        first_page = self.__pages[0]
        return await self.__view.send(target=target, content=first_page.content, embeds=first_page.embeds, files=first_page.files, view=self.__view.copy() + first_page.get_page_view)

    async def respond(self, ctx: Union[ApplicationContext, Interaction]) -> Any:
        """
        Respond to the command call
        :param ctx: ApplicationContext to respond
        """
        first_page = self.__pages[0]
        return await self.__view.respond(ctx=ctx, content=first_page.content, embeds=first_page.embeds, files=first_page.files, view=self.__view.copy() + first_page.get_page_view)

    def get_page(self, page_number: int) -> Page:
        """
        Get the page
        """
        if 0 <= page_number <= len(self.__pages):
            return self.__pages[page_number]
        else:
            raise PageNumberNotFound(page_number)

    @property
    def get_current_showed_page(self) -> int:
        """
        Get the number of showed page
        (start to 0)
        """
        return self.__current_page

    @property
    def get_view(self) -> EasyModifiedViews:
        return self.__view
