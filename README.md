# Webhook:
A learning project demonstrating webhook ingestion, PostgreSQL persistence, background delivery, retry handling, and delivery-status tracking.

# Endpoints:
URL = http://127.0.0.1:8000
- `POST /receive` - accepts and stores an event for delivery.
- `GET /events/{event_id}` - returns the current delivery status.

# Payload Example:
post:

``` json
    {
        "event_id" : "example_id",
        "event_type" : "example_type",
        "event_data" : {"data":"example_value"}
    }
```

# GET Answer Example:

get:

``` json

    {
        "event_id" : "example_id",
        "event_type" : "example_type",
        "event_data" : "example_data",
        "event_status" : "delivered",
        "attempt_count" : 1,
        "final_status_code" : 200,
        "received_at" : "2026-11-25 21:40:12.345678"

   }
```


# feeder_test inputs:
1 - event_id 
2 - event_type
3 - event_data

# Responses & Retries
`202 Accepted` — The event was saved and queued for delivery.
`422 INVALID DATA ` - The data submitted in the request cannot be accepted.
`500 DATABASE ERROR` - An error occurred while writing the message to the database.
`404 NOT FOUND` - The event was not found in the database.
* Retry policy: 
- Delivery is attempted up to three times. HTTP 429, 5xx responses, and network errors trigger a retry if attempts remain


# Run the demo:

- Create and activate a virtual environment

``` bash 
    python3 -m venv venv
    source venv/bin/activate
```

- Starting the PSQL server and creating a database
```bash
    brew services start postgresql@16
    createdb webhook_base
```


- Install dependencies
``` bash
    pip install -r requirements.txt
```


- Run each command in a separate terminal with the virtual environment activated
``` bash
    uvicorn main:app --port 8000 # Inbox
    uvicorn receiver_test:app --port 8001 # Receiver
    python feeder_test.py # Sender
```

# Limitations:
- This is a local demo. Webhook signatures are not verified.

