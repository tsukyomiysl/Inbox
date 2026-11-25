from fastapi import FastAPI
app = FastAPI()


@app.post("/receive")
async def receive_event(event: dict):
    print("Received event:", event)
    return  {
        "status": "ok"
        }
