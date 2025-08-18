class MultibotError(Exception):
    pass

class BotAlreadyExistError(MultibotError):
    def __init__(self, bot_name: str):
        super().__init__(f"'{bot_name}' bot already exist !")

class BotNotFoundError(MultibotError):
    def __init__(self, bot_name: str):
        super().__init__(f"'{bot_name}' bot doesn't exist !")

class BotNotStartedError(MultibotError):
    def __init__(self, bot_name: str):
        super().__init__(f"'{bot_name}' not started !")

class BotNotReadyedError(MultibotError):
    def __init__(self, bot_name: str):
        super().__init__(f"'{bot_name}' not ready !")

class BotAlreadyStartedError(MultibotError):
    def __init__(self, bot_name: str):
        super().__init__(f"'{bot_name}' already started !")

class SetupCommandFunctionNotFound(MultibotError):
    def __init__(self, setup_command_name: str, file: str):
        super().__init__(f"'{setup_command_name}' function not found in '{file}' file ! Init commands impossible.")

class CommandFileNotFoundError(MultibotError):
    def __init__(self, file_name: str):
        super().__init__(f"'{file_name}' file not found ! Init commands impossible !")

class ModuleNotFoundError(MultibotError):
    def __init__(self, module_name: str):
        super().__init__(f"{module_name} module not found !")
