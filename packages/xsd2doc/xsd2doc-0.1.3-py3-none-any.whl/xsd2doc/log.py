from rich import print
from rich.text import Text
from enum import Enum

class TermMessage:
    class TYPE(Enum):
        INFO = "[white]Info: [/white]"
        WARN = "[orange3]Warn: [/orange3]"
        ERROR = "[red]Error: [/red]"
    
    @staticmethod
    def write_msg(type: TYPE, msg: str):
        print(f"{type.value} {msg}")