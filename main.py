from fastapi import FastAPI, HTTPException, Response
from models.event_class import IncomeEvent
from models.agent_model import hook_agent
from contextlib import asynccontextmanager
from requests_funcs.one_resp_procces import req_to_deliever
import asyncio
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from logger import logging


async def worker():
    while True:
        try:
            event = await hook_agent.check_only_pending_resp()
            if event is not None:
                result = await req_to_deliever(event)
                print(result)
            else:
                await asyncio.sleep(0.3)
        except Exception as error:
            logging.critical(error)


@asynccontextmanager
async def lifespan(app:FastAPI):
    await hook_agent.connect()
    worker_task = asyncio.create_task(worker())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    await hook_agent.close()


app = FastAPI(lifespan=lifespan)

@app.post("/receive")
async def receive_webhook(event : IncomeEvent):
    try:
        result = await hook_agent.add_income_event(event.event_id, event.event_type, event.event_data)
        if result == "ok":
            return JSONResponse(
                status_code=202,
                content={
                    "status" : "accepted",
                    "message": "Event saved and queued for delivery",
                    "event_id" : event.event_id
                },
            )
        elif result == "duplicate":
            return {
                    "status" : "already received",
                "event_id" : event.event_id
            }
        elif result == "violation of terms":
            raise HTTPException(status_code=422, detail="Invalid data: constraint violation")
        
        elif result == "error":
                raise HTTPException(status_code=500, detail="Database error")
    except ValidationError:
        raise HTTPException(status_code=422, detail="Invalid data: constraint violation")



@app.get("/events/{event_id}")
async def get_event_deliver_status(event_id : str, response : Response):
    result = await hook_agent.get_event_by_id(event_id)
    if result is None:
        response.status_code = 404
        return {
                "event" : "Event not found"
        }
    else:
        return {
            "event_id" : result.event_id,
            "event_type" : result.event_type,
            "event_data" : result.event_data,
            "event_status" : result.event_status,
            "attempt_count" : result.attempt_count,
            "final_status_code" : result.final_status_code,
            "received_at" : result.received_at
        }
