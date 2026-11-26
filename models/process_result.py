from dataclasses import dataclass
from typing import Any

@dataclass
class ProcessResult:
    result : Any
    status : str
    info : str
    last_code : None | int