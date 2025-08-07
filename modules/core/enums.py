from enum import StrEnum

from colorama import Fore


class PrintColors(StrEnum):
    SPECIAL = Fore.LIGHTCYAN_EX
    USER_TURN = Fore.LIGHTBLUE_EX
    MODEL_TURN = Fore.LIGHTMAGENTA_EX
    SUCCESS = Fore.LIGHTGREEN_EX
    WARNING = Fore.LIGHTYELLOW_EX
    ERROR = Fore.LIGHTRED_EX
