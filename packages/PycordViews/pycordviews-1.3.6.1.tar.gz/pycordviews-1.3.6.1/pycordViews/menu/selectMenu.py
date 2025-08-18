
from ..views.easy_modified_view import EasyModifiedViews
from .menu import Menu

from typing import Union, Callable, Any, Optional
from discord.components import ComponentType
from discord import ChannelType, Member, ApplicationContext, Interaction, Role
from discord.abc import GuildChannel

class SelectMenu:
    """
    Create a simply select menu
    """

    def __init__(self, timeout: Union[float, None] = None, disabled_on_timeout: bool = False):
        """
        Init the select menu
        """
        self.__select_menu: EasyModifiedViews = EasyModifiedViews(timeout=timeout, disabled_on_timeout=disabled_on_timeout)

    def add_string_select_menu(self, custom_id: str = None, placeholder: str = None, min_values: int = 1, max_values: int = 1, disabled=False, row=None) -> Menu:
        """
        Add a string select menu in the ui
        :param custom_id: The ID of the select menu that gets received during an interaction. If not given then one is generated for you.
        :param placeholder: The placeholder text that is shown if nothing is selected, if any.
        :param max_values: The maximum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param min_values: The minimum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param disabled: Whether the select is disabled or not.
        :param row: The relative row this select menu belongs to. A Discord component can only have 5 rows. By default, items are arranged automatically into those 5 rows. If you’d like to control the relative positioning of the row then passing an index is advised. For example, row=1 will show up before row=2. Defaults to None, which is automatic ordering. The row number must be between 0 and 4 (i.e. zero indexed).
        """
        return self.__global_add_component(ComponentType.string_select, custom_id=custom_id, placeholder=placeholder, max_values=max_values, min_values=min_values, disabled=disabled, row=row)

    def add_user_select_menu(self, custom_id: str = None, placeholder: str = None, min_values: int = 1, max_values: int = 1, disabled=False, row=None) -> Menu:
        """
        Add an user select menu in the ui
        :param custom_id: The ID of the select menu that gets received during an interaction. If not given then one is generated for you.
        :param placeholder: The placeholder text that is shown if nothing is selected, if any.
        :param max_values: The maximum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param min_values: The minimum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param disabled: Whether the select is disabled or not.
        :param row: The relative row this select menu belongs to. A Discord component can only have 5 rows. By default, items are arranged automatically into those 5 rows. If you’d like to control the relative positioning of the row then passing an index is advised. For example, row=1 will show up before row=2. Defaults to None, which is automatic ordering. The row number must be between 0 and 4 (i.e. zero indexed).
        """
        return self.__global_add_component(ComponentType.user_select, custom_id=custom_id, placeholder=placeholder, max_values=max_values, min_values=min_values, disabled=disabled, row=row)

    def add_role_select_menu(self, custom_id: str = None, placeholder: str = None, min_values: int = 1, max_values: int = 1, disabled=False, row=None) -> Menu:
        """
        Add a role select menu in the ui
        :param custom_id: The ID of the select menu that gets received during an interaction. If not given then one is generated for you.
        :param placeholder: The placeholder text that is shown if nothing is selected, if any.
        :param max_values: The maximum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param min_values: The minimum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param disabled: Whether the select is disabled or not.
        :param row: The relative row this select menu belongs to. A Discord component can only have 5 rows. By default, items are arranged automatically into those 5 rows. If you’d like to control the relative positioning of the row then passing an index is advised. For example, row=1 will show up before row=2. Defaults to None, which is automatic ordering. The row number must be between 0 and 4 (i.e. zero indexed).
        """
        return self.__global_add_component(ComponentType.role_select, custom_id=custom_id, placeholder=placeholder, max_values=max_values, min_values=min_values, disabled=disabled, row=row)

    def add_mentionable_select_menu(self, custom_id: str = None, placeholder: str = None, min_values: int = 1, max_values: int = 1, disabled=False, row=None) -> Menu:
        """
        Add a mentionable select menu in the ui
        :param custom_id: The ID of the select menu that gets received during an interaction. If not given then one is generated for you.
        :param placeholder: The placeholder text that is shown if nothing is selected, if any.
        :param max_values: The maximum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param min_values: The minimum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param disabled: Whether the select is disabled or not.
        :param row: The relative row this select menu belongs to. A Discord component can only have 5 rows. By default, items are arranged automatically into those 5 rows. If you’d like to control the relative positioning of the row then passing an index is advised. For example, row=1 will show up before row=2. Defaults to None, which is automatic ordering. The row number must be between 0 and 4 (i.e. zero indexed).
        """
        return self.__global_add_component(ComponentType.mentionable_select, custom_id=custom_id, placeholder=placeholder, max_values=max_values, min_values=min_values, disabled=disabled, row=row)

    def add_channel_select_menu(self, custom_id: str = None, placeholder: str = None, min_values: int = 1, max_values: int = 1, disabled=False, row=None, channel_types: list[ChannelType] = None):
        """
        Add a channel select menu in the ui
        :param custom_id: The ID of the select menu that gets received during an interaction. If not given then one is generated for you.
        :param placeholder: The placeholder text that is shown if nothing is selected, if any.
        :param max_values: The maximum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param min_values: The minimum number of items that must be chosen for this select menu. Defaults to 1 and must be between 1 and 25.
        :param disabled: Whether the select is disabled or not.
        :param row: The relative row this select menu belongs to. A Discord component can only have 5 rows. By default, items are arranged automatically into those 5 rows. If you’d like to control the relative positioning of the row then passing an index is advised. For example, row=1 will show up before row=2. Defaults to None, which is automatic ordering. The row number must be between 0 and 4 (i.e. zero indexed).
        :param channel_types: A list of channel types that can be selected in this menu.
        """
        return self.__global_add_component(ComponentType.channel_select, custom_id=custom_id, placeholder=placeholder, max_values=max_values, min_values=min_values, disabled=disabled, row=row, channel_types=channel_types)

    def __global_add_component(self, component_type: ComponentType,
                               custom_id: Union[str, None] = None,
                               placeholder: Union[str, None] = None,
                               min_values: int = 1,
                               max_values: int = 1,
                               disabled: bool = False,
                               row: Union[int, None] = None,
                               channel_types: Union[ChannelType, None] = None) -> Menu:
        """
        global function to add a Select component
        """
        menu = Menu(component_type,
                    self,
                    **{'custom_id': custom_id, 'placeholder': placeholder, 'min_values': min_values,
                       'max_values': max_values, 'disabled': disabled, 'row': row, 'channel_types': channel_types})

        self.__select_menu.add_items(menu.component)

        return menu

    def set_callable(self, *custom_ids: str,
                     _callable: Union[Callable, None],
                     data: Optional[dict[str, Any]] = None,
                     autorised_roles : Optional[list[Union[int, Role]]] = None,
                     autorised_key: Optional[Callable] = None) -> "SelectMenu":
        """
        Set a callable for menus associated with custom_ids
        :param custom_ids: IDs menus
        :param _callable: The coroutine to set for all menus
        :param data: Add any data to pass in called function.
        :param autorised_roles: Any role ID allowed to interact with the view
        :param autorised_key: Callable function to check anything. The function get the current interaction passed in parameter
        """
        self.__select_menu.set_callable(*custom_ids, _callable=_callable, data=data, autorised_key=autorised_key, autorised_roles=autorised_roles)
        return self

    async def respond(self, ctx: Union[ApplicationContext, Interaction], *args, **kwargs) -> Any:
        """
        Respond at the ApplicationContext
        """
        return await self.__select_menu.respond(ctx=ctx, *args, view=self.__select_menu, **kwargs)

    async def send(self, target: Union[Member, GuildChannel], *args, **kwargs) -> Any:
        """
        Send at the target
        """
        return await self.__select_menu.send(target=target, *args, view=self.__select_menu, **kwargs)

    async def update(self):
        """
        Update the message.
        If the command doesn't have been respond, nothing happened.
        """
        if self.get_view.message is None:
            return
        await self.__select_menu.update_items(*self.get_view.items)

    def get_callable(self, custom_id: str) -> Union[Callable, None]:
        """
        Get the callable UI
        :param custom_id: UI ID
        """
        return self.__select_menu.get_callable(custom_id)

    @property
    def get_view(self) -> EasyModifiedViews:
        """
        Get the current view
        """
        return self.__select_menu

