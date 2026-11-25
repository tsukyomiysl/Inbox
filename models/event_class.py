from pydantic import BaseModel

class IncomeEvent(BaseModel):
    event_id : str
    event_type: str
    event_data : dict