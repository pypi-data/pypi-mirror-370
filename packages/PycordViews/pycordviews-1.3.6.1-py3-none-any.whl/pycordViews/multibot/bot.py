from threading import Thread
from discord import Intents, Bot, ApplicationCommand
from asyncio import run_coroutine_threadsafe, new_event_loop, set_event_loop, Future, AbstractEventLoop, sleep
from time import sleep as tsleep
from .errors import BotNotStartedError, SetupCommandFunctionNotFound, CommandFileNotFoundError
from typing import Optional
from importlib import reload
from importlib.util import spec_from_file_location, module_from_spec
from os import path
from sys import modules


class DiscordBot:

    def __init__(self, token: str, intents: Intents,  command_prefix: Optional[str] = None):
        self.__token: str = token
        self.__command_prefix: str = command_prefix
        self.__running_bot: Future = None
        self.__loop: AbstractEventLoop = new_event_loop()
        self.__thread: Thread = Thread(target=self.run_loop, daemon=True)  # Thread pour exécuter l'event loop
        self.__thread.start()
        self.__bot: Bot = Bot(loop=self.__loop, intents=intents, command_prefix=command_prefix, help_commad=None, auto_sync_commands=False)
        self.__intents: Intents = intents
        self.__imported_module: list[dict[str, ...]] = []

    def run_loop(self):
        """Lance la boucle asyncio dans un thread séparé."""
        set_event_loop(self.__loop)
        self.__loop.run_forever()

    def start(self) -> None:
        """Démarre le bot"""

        self.__running_bot: Future = run_coroutine_threadsafe(self.__bot.start(token=self.__token, reconnect=True), self.__loop)

    def stop(self) -> None:
        """
        Stop le bot proprement depuis un autre thread
        :raise: BotNotStartedError
        """
        if self.is_running:
            # Attendre que la fermeture du bot soit terminée
            run_coroutine_threadsafe(self.__stop_bot_in_thread(), self.__loop).result(timeout=30)
            self.__bot = Bot(token=self.__token, intents=self.__intents, command_prefix=self.__command_prefix, help_command=None)
            self.__running_bot = None
        else:
            raise BotNotStartedError(self.__bot.user.name)

    async def __stop_bot_in_thread(self):
        """
        Clear le cache du bot de manière asynchrone
        """
        await self.__bot.close()

    def add_pyFile_commands(self, file: str, reload_command: bool, setup_function: str):
        """
        Ajoute et charge un fichier de commande bot et ses dépendances.
        Les fichiers doivent avoir une fonction appelée « setup » ou un équivalent passé en paramètre.

        def setup(bot: Bot) :
            ...

        :param bot_name : Le nom du bot à ajouter au fichier de commandes
        :param file: Chemin relatif ou absolue du fichier de commande
        :param setup_function : Nom de la fonction appelée par le processus pour donner l'instance de Bot.
        :param reload_command : Recharge toutes les commandes dans le fichier et les dépendances. Défaut : True
        """
        module_name = path.splitext(path.basename(file))[0] # récupère le nom du fichier
        spec = spec_from_file_location(module_name, file) # renvoie un "module spec" à partir du nom et du fichier
        if spec and spec.loader:
            module = module_from_spec(spec) # crée le package à partir du "module spec" s'il existe
            spec.loader.exec_module(module) # charge tout le package
            modules[module_name] = module # enregistre le modul dans les packages du système pour qu'il soit retrouvable lors du rechargement de celui-ci
            self.__call_setup_function_in_command_file(file, module, setup_function, reload_command)
        else:
            raise CommandFileNotFoundError(file)

    def modify_pyFile_commands(self, file: str, setup_function: str):
        """
        Modifie un fichier de comandes et le recharge.
        Ne recharge que le fichier et non les commandes du bot !
        :param file: Le chemin d'accès relatif ou absolue du fichier
        """
        module_name = path.splitext(path.basename(file))[0]
        module_found = False

        # Mise à jour du module et de son setup
        for imported in self.__imported_module:

            if imported['module'].__name__ == module_name:
                imported['setup_function'] = setup_function
                module_found = True
                break

        if not module_found:
            raise CommandFileNotFoundError(file)

        # Supprimer toutes les commandes du bot
        for command in self.__bot.application_commands:
            self.__bot.remove_application_command(command)

        # Réattacher toutes les commandes en réexécutant tous les setup
        for imported in self.__imported_module:
            self.__call_setup_function_in_command_file(
                file,
                imported['module'],
                imported['setup_function'],
                reload_command=False
            )

    def reload_pyFile_commands(self):
        """
        Recharge tous les fichiers de commandes du bot
        """
        for imported in self.__imported_module:
            self.modify_pyFile_commands(imported['file'], imported['setup_function'])



    def __call_setup_function_in_command_file(self, file: str, module, setup_function: str, reload_command: bool):
        """
        Appel la fonction de setup du module pour charger toutes les commandes du bot
        :param file: Le chemin d'accès du fichier de commandes
        :param module: Le module préchargé
        :param setup_function: Le nom de la fonction de setup
        :param reload_command: Si les commandes doivent être recharger sur le bot (envoie une requête à Discord) automatiquement
        """
        if hasattr(module, setup_function):  # si la fonction setup (ou autre) est dans le package
            getattr(module, setup_function)(self.__bot)

            ########## permet de modifier le dictionnaire des modules importés si celui-ci existe déjà, sinon il l'ajoute à la liste des dictionaires des modules importés. Utile car on reload tout si un des modules est modifié
            find = False
            for mod in self.__imported_module:
                if mod['module'].__name__ == module.__name__:
                    mod['setup_function'] = setup_function
                    find = True
                    break

            if not find:
                self.__imported_module.append({'setup_function': setup_function, 'module': module, 'file': file})
            ##########

            if reload_command:
                self.reload_commands()
        else:
            raise SetupCommandFunctionNotFound(setup_function, file)

    def reload_commands(self, commands: Optional[list[ApplicationCommand]] = None):
        """
        Charge toutes les commandes du bot sur Discord
        """
        run_coroutine_threadsafe(self.__reload_commands(commands=commands), self.__loop).result(timeout=60)

    async def __reload_commands(self, commands: Optional[list[ApplicationCommand]] = None):
        """
        Recharge les commandes quand le bot est ready
        """
        if self.__running_bot is not None:
            while not self.is_ready:
                await sleep(0.3)
            await self.__bot.register_commands(commands=commands, method='individual', force=False)
        else:
            raise BotNotStartedError(self.__token)


    @property
    def is_running(self) -> bool:
        """Renvoie si la Websocket est connectée"""
        return not self.__bot.is_closed()

    @property
    def is_ready(self) -> bool:
        """
        Renvoie si le bot est ready
        """
        return self.__bot.is_ready()

    @property
    def is_ws_ratelimited(self) -> bool:
        """
        Renvoie si le bot est rate limit
        """
        return self.__bot.is_ws_ratelimited()


    def close_ascyncio_loop(self):
        """
        Ferme la boucle asyncio
        """
        if self.__loop.is_running():
            self.__loop.stop()

        while self.__loop.is_running():
            tsleep(0.3)

        self.__loop.close()


