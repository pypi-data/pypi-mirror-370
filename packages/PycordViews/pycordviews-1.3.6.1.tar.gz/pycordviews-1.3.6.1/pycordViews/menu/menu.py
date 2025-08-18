from discord.components import ComponentType
from discord.ui import Select, Item
from discord import MISSING, Emoji, PartialEmoji, Role
from typing import Callable, Union, Optional, Any

from .errors import NotCoroutineError, ComponentTypeError


class Menu:

    def __init__(self, menu_type: ComponentType, selectmenu: "SelectMenu", **kwargs):
        """
        A basic menu from selectMenu class
        """
        self.__menu: CustomSelect = CustomSelect(menu=self, select_type=menu_type, **kwargs)
        self.__selectMenu = selectmenu
        self.__menu_type: ComponentType = menu_type

    def set_callable(self, _callable: Union[Callable, None],
                     data: Optional[dict[str, Any]] = None,
                     autorised_roles : Optional[list[Union[int, Role]]] = None,
                     autorised_key: Optional[Callable] = None) -> "Menu":
        """
        Add a coroutine to the menu (same function on SelectMenu class)
        This coroutine can have 3 parameters (X, interaction, data)
        """
        if not isinstance(_callable, Callable):
            raise NotCoroutineError(_callable)

        self.__selectMenu.set_callable(self.__menu.custom_id, _callable=_callable, data=data, autorised_roles=autorised_roles, autorised_key=autorised_key)
        return self

    def add_option(self, label: str, value: str = MISSING, description: Union[str, None] = None, emoji: Union[str, Emoji, PartialEmoji, None] = None, default: bool = False) -> "Menu":
        """
        Add an option to choice.
        Only from string_select type !
        """
        self.__is_string_select()

        self.__menu.add_option(label=label, value=value, description=description, emoji=emoji, default=default)
        return self

    def remove_options(self, *labels: str) -> "Menu":
        """
        Remove an option to choice.
        Only from string_select type !
        :param labels: Label option name to delete
        """
        self.__is_string_select()

        self.__menu.options = [i for i in self.__menu.options if i.label not in labels]
        return self

    def update_option(self, current_label: str, new_label: str = None, value: str = None, description: Union[str, None] = None, emoji: Union[str, Emoji, PartialEmoji, None] = None, default: Union[bool, None] = None) -> "Menu":
        """
        Update option. To find the option, write her actual label in "current_label" option.
        Only from string_select type !
        :param current_label: The current label option to edit
        """
        self.__is_string_select()

        for option in self.__menu.options:
            if option.label == current_label:
                option.label = new_label if new_label is not None else option.label
                option.value = value if value is not None else option.value
                option.description = description if description is not None else option.description
                option.default = default if default is not None else option.default
                option.emoji = emoji if emoji is not None else option.emoji
                break
        return self

    def __is_string_select(self) -> None:
        """
        Check if the menu is a string_select
        :raise: ComponentTypeError
        """
        if self.__menu.type != ComponentType.string_select:
            raise ComponentTypeError()

    @property
    def component(self) -> "CustomSelect":
        """
        Get the component
        """
        return self.__menu

    @property
    def selectmenu(self) -> "SelectMenu":
        """
        Get the selectMenu
        """
        return self.__selectMenu

    @property
    def callable(self) -> Callable:
        """
        Get the current callable menu
        """
        return self.__selectMenu.get_callable(self.__menu.custom_id)

class CustomSelect(Select):
    """
    Subclass of Select discord Class to use some SelectMenu functions
    """

    def __init__(self, menu: Menu, select_type: ComponentType, *items: Item, **kwargs):
        super().__init__(select_type=select_type, *items, **kwargs)
        self.__menu: Menu = menu

    async def update(self):
        """
        Bridge to SelectMenu update function
        """
        return await self.__menu.selectmenu.update()

    @property
    def get_view(self) -> "EasyModifiedViews":
        """
        Bridge to SelectMenu get_view property
        """
        return self.__menu.selectmenu.get_view
