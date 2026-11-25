from models.agent_model import hook_agent
from requests_funcs.post_request import send_post_request
from requests_funcs.delivery_result import delivery_separation
from datetime import datetime, timedelta
from models.tables import InputEvent
from models.result_class import Result
from logger import logging

async def req_to_deliever(event : InputEvent ) -> dict | None:
        DELIVER_URL = "http://127.0.0.1:8001/receive"

        if event.event_status == "pending" and (event.next_attempt is None or event.next_attempt <= datetime.now()):
            if event.attempt_count >= 3:
                last_code = await hook_agent.select_last_status_code(event.event_id)
                result = await hook_agent.update_after_request(Result(event.event_id, "failed", event.attempt_count,
                DELIVER_URL,"Delivery attempt limit reached", last_code, None, None, False ))
                if result:
                    logging.error("Event delivery failed")
                    return {
                            "status" : "failed",
                            "event_id" : event.event_id,
                            "status_code" : last_code
                        }
                else:
                    logging.critical("Failed to save the delivery result")
                    return {
                        "status" : "write error",
                        "event_id" : event.event_id,
                        "status_code" : last_code
                    }
                 
            request_code = await send_post_request(event, DELIVER_URL)
            code = await delivery_separation(request_code)

            if code == "delivered":
                result = await hook_agent.update_after_request(Result(event.event_id, "delivered" ,
                (event.attempt_count + 1), DELIVER_URL, "-", request_code ,request_code, None, True) )
                status = "delivered"
                info = "Event delivered"
                
            elif code == "failed" :
                result = await hook_agent.update_after_request(Result(event.event_id, "failed" ,(event.attempt_count + 1), DELIVER_URL,
                "Delivery failed", request_code ,request_code, None, True) )
                status = "failed"
                info = "Event delivery failed"

            elif code == "retry":
                if event.attempt_count + 1 < 3:
                    result = await hook_agent.update_after_request(Result(event.event_id, "pending", 
                    (event.attempt_count + 1), DELIVER_URL, "Temporary delivery failure", None,request_code, datetime.now() + timedelta(seconds=2), True) )
                    status = "pending"
                    info = "Delivery retry scheduled"
                else:
                    result = await hook_agent.update_after_request(Result(event.event_id, "failed", event.attempt_count + 1,
                    DELIVER_URL,"Delivery attempt limit reached", request_code, request_code, None, True ))
                    status = "failed"
                    info = "Event delivery failed"
            if result:
                if info == "Event delivered":
                    logging.info(info)
                elif info == "Event delivery failed":
                    logging.error(info)
                elif info == "Delivery retry scheduled":
                    logging.warning(info)
                return {
                    "status" : status,
                    "event_id" : event.event_id,
                    "status_code" : request_code
                }
            else:
                logging.critical("Failed to save the delivery result")
                return {
                    "status" : "sql write error",
                    "event_id" : event.event_id,
                    "status_code" : request_code

                }
        else:
                return        
                        
                        
