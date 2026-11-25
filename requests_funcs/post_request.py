import httpx
from httpx import RequestError
from models.tables import InputEvent

async def send_post_request(event : InputEvent, url : str) -> int | None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json={"event_id":event.event_id,"event_type":event.event_type,
            "event_data":event.event_data }, timeout=10)
            result = response.status_code
            return int(result)
        except RequestError:
            return None
    
