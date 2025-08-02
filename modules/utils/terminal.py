from colorama import Fore

def new_print(text: str, color: str, end: str = "\n") -> None:
    print(colorize_text(text, color), end=end)

def colorize_text(text: str, color: str) -> str:
    return f"{color}{text}{Fore.RESET}"
