from models.process_result import ProcessResult
from logger import logging

async def return_info(values : ProcessResult, event, request_code):
    result = values.result
    info = values.info
    status = values.status
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