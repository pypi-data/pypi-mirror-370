from __future__ import annotations
from discord import Interaction, ApplicationContext, Message, Member, Role
from discord.abc import GuildChannel
from discord.ui import View, Item
from typing import Union, Callable, TYPE_CHECKING, Optional, Any
from asyncio import iscoroutinefunction, create_task

from .errors import CustomIDNotFound, CoroutineError

if TYPE_CHECKING:
    from ..menu.selectMenu import SelectMenu
    from ..pagination.pagination_view import Pagination
    from ..kit import Poll, Confirm


class EasyModifiedViews(View):
    """
    Class
    -------------
    Allows you to easily modify and replace an ui.
    """

    def __init__(self, timeout: Optional[float] = None, disabled_on_timeout: bool = False, call_on_timeout: Optional[Callable] = None, *items: Item):
        """
        Init a Class view for Discord UI
        :param timeout: The time before ui disable
        :param disabled_on_timeout: disable view if timeout is reached
        :param call_on_timeout: asynchronous function to call after view timed-out
        """
        super().__init__(*items, timeout=timeout)
        self.__timeout: Optional[float] = timeout
        self.__disabled_on_timeout: bool = disabled_on_timeout
        self.__callback: dict[str, dict[str, Union[Callable[[Interaction], None], Item, Any]]] = {}
        self.__ctx: Union[Message, Interaction] = None
        self.__call_on_timeout: Callable = call_on_timeout

    def __check_custom_id(self, custom_id: str) -> None:
        """
        Check if the custom_id is alive
        :param custom_id: ID to find
        :raise: CustomIDNotFound
        """
        if custom_id not in self.__callback.keys():
            raise CustomIDNotFound()

    async def respond(self, ctx: Union[ApplicationContext, Interaction], *args, **kwargs) -> None:
        """
        Respond at the ApplicationContext or Interaction
        """
        self.__ctx = await ctx.respond(*args, **kwargs)

    async def send(self, target: Union[Member, GuildChannel], *args, **kwargs) -> None:
        """
        Send at the target
        """
        self.__ctx = await target.send(*args, **kwargs)

    def add_items(self,
                   *items: Union[EasyModifiedViews, Confirm, Pagination, Poll, SelectMenu, Item]) -> EasyModifiedViews:
        """
        Add all items in the View.
        """

        for ui in items:

            if ui is None: # si l'ui n'est pas setup
                continue

            if type(ui).__name__ in ('SelectMenu', 'Pagination', 'Confirm', 'Poll', 'EasyModifiedViews'):
                for item in ui.get_view.items:
                    self.add_items(item)
                    self.set_callable(item.custom_id, _callable=ui.get_view.get_callable(item.custom_id), data=ui.get_view.get_callable_data(item.custom_id))

            else:
                self.__callback[ui.custom_id] = {'ui': ui, 'func': None, 'data': {}, 'autorised_roles': None, 'autorised_key': None}
                self.add_item(ui)

        return self

    async def update_items(self, *items: Item) -> "EasyModifiedViews":
        """
        Update all views.
        Append items if custom_ids not in the view
        Update items if custom_ids in the view
        :param items: items to update
        """

        for item in items:
            try:
                self.__check_custom_id(item.custom_id)
                self.__callback[item.custom_id]['ui'] = item

            except CustomIDNotFound:
                self.add_items(item)

        await self._update()
        return self

    def set_callable_decorator(self, custom_id: str,
                               data: Optional[dict[str, Any]] = None,
                               autorised_roles : Optional[list[Union[int, Role]]] = None,
                               autorised_key: Optional[Callable] = None):
        """
        Decorator to set up a callable for the item

        **Ui, Interaction and data parameters is required in coroutine function !**

        view = EasyModifiedViews(None)
        view.add_view(discord.ui.Button(label='coucou', custom_id='test_ID'))

        @view.set_callable_decorator(custom_id='test_ID')

        async def rep(**UI**, **interaction**, data):
            await interaction.response.send_message('coucou !!!')

        await ctx.respond('coucou', view=view)

        :param custom_id: item ID of the view
        :param data: Add any data to pass in called function.
        :param autorised_roles: Any role ID allowed to interact with the view
        :param autorised_key: Callable function to check anything. The function get the current interaction and data passed in parameter
        """

        def decorator(_callable: Callable):
            self.set_callable(custom_id,
                              _callable=_callable,
                              data=data,
                              autorised_roles=autorised_roles,
                              autorised_key=autorised_key)
            return _callable

        return decorator

    def set_callable(self, *custom_ids: str,
                     _callable: Callable,
                     data: Optional[dict[str, Any]] = None,
                     autorised_roles : Optional[list[Union[int, Role]]] = None,
                     autorised_key: Optional[Callable] = None):
        """
        set up a callable for items
        :param custom_ids: items IDs of the view
        :param _callable: The asynchronous callable linked. Take UI (Button, Select...) and Interaction parameters.
        :param data: Add any data to pass in called function.
        :param autorised_roles: Any role ID allowed to interact with the view
        :param autorised_key: Callable function to check anything. The function get the current interaction and data passed in parameter

        **UI, Interaction and data parameter is required in callable function !**

        view = EasyModifiedViews(None)

        view.add_view(discord.ui.Button(label='coucou', custom_id='test_ID'))

        async def rep(**UI**, **interaction**, data: dict[str, Any]):
            await interaction.response.send_message(data['message'])

        view.set_callable(custom_id='test_ID', callable=rep, data={'message': 'Hello !'})
        await ctx.respond('coucou', view=view)
        """
        for custom_id in custom_ids:
            self.__check_custom_id(custom_id)

            self.__callback[custom_id]['func'] = _callable
            self.__callback[custom_id]['data'] = data if data is not None else {}
            self.__callback[custom_id]['autorised_key'] = autorised_key
            if autorised_roles is not None:
                self.__callback[custom_id]['autorised_roles'] = [role.id if isinstance(role, Role) else role for role in autorised_roles if isinstance(role, (Role, int))]
            else:
                self.__callback[custom_id]['autorised_roles'] = None

    def get_callable(self, custom_id: str) -> Union[Callable, None]:
        """
        Get the callable UI
        :param custom_id: UI ID
        """
        self.__check_custom_id(custom_id)
        return self.__callback[custom_id]['func']

    async def interaction_check(self, interaction: Interaction) -> bool:
        """
        Func to apply items
        """
        func = self.__callback[interaction.custom_id]['func']
        data = self.__callback[interaction.custom_id]['data']
        autorised_roles = self.__callback[interaction.custom_id]['autorised_roles']
        autorised_key = self.__callback[interaction.custom_id]['autorised_key']

        if func is not None:
            if autorised_roles is not None: # si des rôles sont obligatoires
                if not (set(autorised_roles) & set([i.id for i in interaction.user.roles])): # si aucun rôle de l'user est dans les rôles aubligatoires
                    await interaction.response.defer(invisible=True)
                    return False

            if autorised_key is not None: # si une fonction est config pour la vérification
                if not autorised_key(interaction, data): # Si la fonction renvoie False
                    return False

            return await func(self.__callback[interaction.custom_id]['ui'], interaction, data)

        else:
            await interaction.response.defer(invisible=True)

        return True

    async def shutdown(self) -> None:
        """
        Disable all items (ui) in the view
        """
        self.disable_all_items()
        await self._update()

    async def disable_items(self, *custom_ids: str) -> None:
        """
        Disable partial items in the view
        :param custom_ids: custom ids of all items to deactivate
        """

        self.disable_all_items(exclusions=[self.get_item(id_) for id_ in self.__callback.keys() if id_ not in custom_ids])
        await self._update()

    async def enable_items(self, *custom_ids: str) -> None:
        """
        Enabl partial items in the view
        :param custom_ids: custom ids of all items to activate
        """
        self.enable_all_items(
            exclusions=[self.get_item(id_) for id_ in self.__callback.keys() if id_ not in custom_ids])
        await self._update()

    async def full_enable_items(self) -> None:
        """
        Enable all items in the view
        """
        self.enable_all_items()
        await self._update()


    async def switch_status_items(self):
        """
        Switch status for all items
        Enable -> Disable
        Disable -> Enable
        """

        for key, in self.__callback.keys():
            self.__callback[key]['ui'].disabled = not self.__callback[key]['ui'].disabled

        await self._update()


    def is_items_disabled(self, *custom_ids: str) -> bool:
        """
        Return True if all items are disabled
        """

        for custom_id in custom_ids:
            self.__check_custom_id(custom_id)
            if not self.__callback[custom_id]['ui'].disabled:
                return False

        return True


    def is_items_enabled(self, *custom_ids: str) -> bool:
        """
        Return True il aff items are enabled
        """

        for custom_id in custom_ids:
            self.__check_custom_id(custom_id)
            if self.__callback[custom_id]['ui'].disabled:
                return False

        return True

    async def delete_items(self, clear_all: bool = False, *custom_ids: str) -> None:
        """
        Delete an item on the view
        :param custom_ids: IDs of items to delete
        :param clear_all: Clear all items in the view
        :raise: CustomIDNotFound
        """
        if clear_all:
            self.clear_items()

        else:

            for custom_id in custom_ids:
                self.__check_custom_id(custom_id)
                self.remove_item(self.get_item(custom_id))

        await self._update()

    async def on_timeout(self) -> None:
        """
        Called if timeout view is finished
        """
        if self.__disabled_on_timeout:
            await self.shutdown()
        if self.__call_on_timeout is not None:
            await self.__call_on_timeout(self.__ctx)

    def call_on_timeout(self, _callable: Callable) -> None:
        """
        Call asynchronous function passed when the timeout is reached.
        :param _callable: asynchronous function to call. It takes one argument : ctx
        """
        if iscoroutinefunction(_callable):
            self.__call_on_timeout = _callable
        else:
            raise CoroutineError(_callable)

    async def _update(self) -> None:
        """
        Update the View on the attached message.
        """
        if self.is_finished() and not self.__disabled_on_timeout:
            return

        if self.message:
            await self.message.edit(view=self)

        elif self.__ctx:
            await self.__ctx.edit(view=self)

    def get_ui(self, custom_id: str) -> Item:
        """
        Get an ui in the view
        :param custom_id: UI ID
        :raise: CustomIDNotFound
        """
        self.__check_custom_id(custom_id)
        return self.__callback[custom_id]['ui']

    def get_callable_data(self, custom_id: str) -> dict[str, Any]:
        """
        Get datas passed in the callable asynchronous function
        :param custom_id: UI ID
        """
        self.__check_custom_id(custom_id)
        return self.__callback[custom_id]['data']

    def copy(self) -> EasyModifiedViews:
        """
        Return an exact copy of the view. All mutable object in the view is a new object
        """
        e = EasyModifiedViews(timeout=self.__timeout, disabled_on_timeout=self.__disabled_on_timeout).add_items(*self.items)
        for i in self.items:
            e.set_callable(i.custom_id, _callable=self.get_callable(i.custom_id), data=self.get_callable_data(i.custom_id))

        return e

    def __str__(self):
        return str(self.__callback)

    @property
    def items(self) -> tuple[Item]:
        return tuple([i['ui'] for i in self.__callback.values()])

    @property
    def get_view(self) -> EasyModifiedViews:
        """
        Get The current view. Don't use in your code
        """
        return self

    def __add__(self, _view: Union[EasyModifiedViews, Confirm, Pagination, Poll, SelectMenu, Item]) -> EasyModifiedViews:
        """
        Add all items to _view from the current EasyModifiedViews instance
        """
        self.add_items(_view)
        return self

    def __iadd__(self, _view) -> EasyModifiedViews:
        """
        Add all items to _view from the current EasyModifiedViews instance
        """
        return self.__add__(_view)
