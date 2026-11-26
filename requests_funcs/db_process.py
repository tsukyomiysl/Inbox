from models.result_class import Result
from models.process_result import ProcessResult
from models.agent_model import hook_agent
from datetime import datetime, timedelta

async def get_base_process_result(event, Deliver_url, request_code, code, exceeding_limit) -> ProcessResult:
    if not exceeding_limit:
        if code == "delivered":
            result = await hook_agent.update_after_request(Result(event.event_id, "delivered" ,
            (event.attempt_count + 1), Deliver_url, "-", request_code ,request_code, None, True) )
            status = "delivered"
            info = "Event delivered"
            last_code=None
        elif code == "failed" :
            result = await hook_agent.update_after_request(Result(event.event_id, "failed" ,(event.attempt_count + 1), Deliver_url,
            "Delivery failed", request_code ,request_code, None, True) )
            status = "failed"
            info = "Event delivery failed"
            last_code=None
        elif code == "retry":
            if event.attempt_count + 1 < 3:
                result = await hook_agent.update_after_request(Result(event.event_id, "pending", 
                (event.attempt_count + 1), Deliver_url, "Temporary delivery failure", None,request_code, datetime.now() + timedelta(seconds=2), True) )
                status = "pending"
                info = "Delivery retry scheduled"
                last_code=None
            else:
                result = await hook_agent.update_after_request(Result(event.event_id, "failed", event.attempt_count + 1,
                Deliver_url,"Delivery attempt limit reached", request_code, request_code, None, True ))
                status = "failed"
                info = "Event delivery failed"
                last_code=None
    else:
        last_code = await hook_agent.select_last_status_code(event.event_id)
        result = await hook_agent.update_after_request(Result(event.event_id, "failed", event.attempt_count,
        Deliver_url,"Delivery attempt limit reached", last_code, None, None, False ))
        status = "failed"
        info = "Event delivery failed"

    return ProcessResult(result=result, status=status, info=info, last_code=last_code)