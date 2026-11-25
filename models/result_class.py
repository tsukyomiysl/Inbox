from dataclasses import dataclass
from datetime import datetime

@dataclass
class Result():
    ev_id : str
    status : str
    attempt_count : int
    deliver_url : str
    error : str
    final_code : int | None
    current_code : int | None
    next_attempt : datetime | None
    attempt_confirm : bool
    
