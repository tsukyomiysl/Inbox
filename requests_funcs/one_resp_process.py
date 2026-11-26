from models.agent_model import hook_agent
from requests_funcs.post_request import send_post_request
from requests_funcs.delivery_result import delivery_separation
from datetime import datetime
from models.tables import InputEvent
from requests_funcs.after_db_process import return_info
from requests_funcs.db_process import get_base_process_result

async def req_to_deliever(event : InputEvent ) -> dict | None:
        DELIVER_URL = "http://127.0.0.1:8001/receive"

        if event.event_status == "pending" and (event.next_attempt is None or event.next_attempt <= datetime.now()):
            if event.attempt_count >= 3:
                values = await get_base_process_result(event , DELIVER_URL, None, None, True)
                info_result = await return_info(values, event, values.last_code)
                return info_result
            else:
                request_code = await send_post_request(event, DELIVER_URL)
                code = await delivery_separation(request_code)
                values = await get_base_process_result(event, DELIVER_URL, request_code, code, False)
                info_result = await return_info(values, event, request_code)
                return info_result
        else:
                return        
                        
                        
