from queue import Empty
from multiprocessing import get_context
from multiprocessing.queues import Queue
from .process import ManageProcess
from discord import Intents
from sys import platform
from typing import Union, Optional


class Multibot:

    def __init__(self, global_timeout: int = 30):
        """
        Get instance to run few Discord bot
        """
        if platform == 'win32':
            ctx = get_context("spawn")
        else:
            ctx = get_context("forkserver")
        self.__main_queue: Queue = ctx.Queue()
        self.__process_queue: Queue = ctx.Queue()
        # Création du processus gérant les bots
        self.__DiscordProcess = ctx.Process(target=self._start_process)
        self.__DiscordProcess.start()
        
        self.global_timeout = global_timeout
        
    def __get_data_queue(self, type: str) -> Union[list[dict], dict]:
        """
        Récupère les données dans la queue processus
        :param type: Type de la requête. Si elle ne correspond pas à la requête écoutée, elle refera un cicle d'écoute
        """
        try:
            result = self.__process_queue.get(timeout=self.global_timeout)
            if result['type'] == type:
                return result
            else:
                # Si le type ne correspond pas, on relance la récupération
                return self.__get_data_queue(type)
        except Empty:
            return {'status': 'error', 'message': 'timeout request exceeded'}
        except ValueError:
            return {'status': 'critical error', 'message': 'queue was closed ! Process was killed ?'}

    def _start_process(self):
        """
        Initialise et exécute le gestionnaire de processus.
        """
        manager = ManageProcess(self.__main_queue, self.__process_queue)
        manager.run()

    def add_bot(self, bot_name: str, token: str, intents: Intents):
        """
        Add a bot in the process
        :param bot_name: Bot name
        :param token: Token bot
        :param intents: Intents bot to Intents discord class
        """
        request_type = "ADD"
        self.__main_queue.put({"type": request_type,
                               "bot_name": bot_name,
                               "token": token,
                               "intents": intents})
        response = self.__get_data_queue(request_type)
        return response  # Retourne le statut de l'ajout

    def remove_bots(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Shutdown and remove bots
        :param bot_names: Bot name to remove
        """
        request_type = "REMOVE"
        response = []
        for bot_name in bot_names:
            self.__main_queue.put({"type": request_type, "bot_name": bot_name})
            response.append(self.__get_data_queue(request_type))
        return response  # Retourne le statut de la suppression

    def start(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Start bots
        :param bot_names: Bots name to start
        :return: List of data bot status
        """
        request_type = "START"
        results = []
        for bot_name in bot_names:
            self.__main_queue.put({'type': request_type, 'bot_name': bot_name})
            results.append(self.__get_data_queue(request_type))
        return results

    def stop(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Stop bots
        :param bot_names: Bots name to start
        :return: Data status dict
        """
        request_type = "STOP"
        results = []
        for bot_name in bot_names:
            self.__main_queue.put({'type': request_type, 'bot_name': bot_name})
            results.append(self.__get_data_queue(request_type))
        return results

    def restart(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Stop and start bots.
        This function is slow ! It's shutdown all bots properly.
        """
        request_type = "RESTART"
        results = []
        for bot_name in bot_names:
            self.__main_queue.put({'type': request_type, 'bot_name': bot_name})
            results.append(self.__get_data_queue(request_type))
        return results

    def restart_all(self):
        """
        Stop and restart all bots
        This function is slow ! It's shutdown all bots properly.
        """
        request_type = "RESTARTALL"
        self.__main_queue.put({'type': request_type})
        return self.__get_data_queue(request_type)

    def start_all(self) -> list[dict[str, list[str]]]:
        """
        Start all bots in the process.
        """
        request_type = "STARTALL"
        self.__main_queue.put({'type': request_type})
        return self.__get_data_queue(request_type)
    
    def stop_all(self) -> list[dict[str, list[str]]]:
        """
        Stop all bots in the process.
        This function is slow ! It's shutdown all bots properly.
        """
        request_type = "STOPALL"
        self.__main_queue.put({'type': request_type})
        return self.__get_data_queue(request_type)

    def add_modules(self, *modules_name):
        """
        Adds modules (library) to the process (thus affecting bots).
        Only previously removed modules can be added again!
        To be run before launching a bot!
        :param modules_name: names of modules to be added
        """
        request_type = "ADD_MODULES"
        self.__main_queue.put({'type': request_type, 'modules_name': modules_name})
        return self.__get_data_queue(request_type)

    def remove_modules(self, *modules_name):
        """
        Removes modules (library) to the process (thus affecting bots).
        To be run before launching a bot!
        :param modules_name: names of modules to be removed
        """
        request_type = "REMOVE_MODULES"
        self.__main_queue.put({'type': request_type, 'modules_name': modules_name})
        return self.__get_data_queue(request_type)

    def is_started(self, bot_name: str) -> bool:
        """
        Return the current Websocket connexion status
        :param bot_name: Bot name
        :return: True if the Websocket is online, else False
        """
        request_type = "IS_STARTED"
        self.__main_queue.put({'type': request_type, 'bot_name': bot_name})
        return self.__get_data_queue(request_type)['message']

    def is_ready(self, bot_name: str) -> bool:
        """
        Return the current bot connexion status
        :param bot_name: Bot name
        :return: True if the bot if ready, else False
        """
        request_type = "IS_READY"
        self.__main_queue.put({'type': request_type, 'bot_name': bot_name})
        return self.__get_data_queue(request_type)['message']

    def is_ws_ratelimited(self, bot_name: str) -> bool:
        """
        Get the current ratelimit status of the bot
        :param bot_name: Bot name
        :return: True if the bot was ratelimited, else False
        """
        request_type = "IS_WS_RATELIMITED"
        self.__main_queue.put({'type': request_type, 'bot_name': bot_name})
        return self.__get_data_queue(request_type)['message']

    def reload_commands(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Reload all commands for each bot when bots are ready
        :param bot_names: Bots name to reload commands
        """
        request_type = "RELOAD_COMMANDS"
        result = []
        for name in bot_names:
            self.__main_queue.put({'type': request_type, 'name': name})
            result.append(self.__get_data_queue(request_type))
        return result

    def add_pyFile_commands(self, bot_name: str, file: str, setup_function: str = 'setup', reload_command: bool = True) -> dict[str, str]:
        """
        Add and load a command bot file and dependencies.
        Files must have a function called ‘setup’ or an equivalent passed as a parameter.

        def setup(bot: Bot):
            ...

        :param bot_name: The bot's name to add commands file
        :param file: Relative or absolute commands file's path
        :param setup_function: Function name called by the process to give the Bot instance. Set to 'setup' by default.
        :param reload_command: Reload all command in the fil and dependencies. Default : True
        """
        request_type = "ADD_COMMAND_FILE"
        self.__main_queue.put({'type': request_type,
                               'bot_name': bot_name,
                               'file': file,
                               'setup_function': setup_function,
                               'reload_command': reload_command})
        return self.__get_data_queue(request_type)

    def modify_pyFile_commands(self, bot_name: str, file: str, setup_function: str = 'setup') -> dict[str, str]:

        """
        Modifies a file of commands and reloads it.
        Reloads only the file, not the bot commands!
        :param bot_name: The bot's name
        :param file: The file's relative or absolute path
        """
        request_type = "MODIFY_COMMAND_FILE"
        self.__main_queue.put({'type': request_type,
                               'bot_name': bot_name,
                               'file': file,
                               'setup_function': setup_function})
        return self.__get_data_queue(request_type)

    @property
    def bot_count(self) -> int:
        """
        Return the total number of bots
        """
        request_type = "BOT_COUNT"
        self.__main_queue.put({'type': request_type})
        return self.__get_data_queue(request_type)['message']

    @property
    def started_bot_count(self) -> int:
        """
        Return the total number of started bots
        """
        request_type = "STARTED_BOT_COUNT"
        self.__main_queue.put({'type': request_type})
        return self.__get_data_queue(request_type)['message']

    @property
    def shutdown_bot_count(self) -> int:
        """
        Return the total number of shutdown bots
        """
        request_type = "SHUTDOWN_BOT_COUNT"
        self.__main_queue.put({'type': request_type})
        return self.__get_data_queue(request_type)['message']

    @property
    def get_bots_name(self) -> list[str]:
        """
        Return all bots name (not real name of bots)
        """
        request_type = "BOTS_NAME"
        self.__main_queue.put({'type': request_type})
        return self.__get_data_queue(request_type)['message']
