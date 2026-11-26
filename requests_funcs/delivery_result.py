async def delivery_separation(code : int | None) -> str | None:
    if code is None:
        return "retry"
    if 500 <= code < 600 or code == 429:
        return "retry"
    elif 200 <= code < 300:
        return "delivered"
    elif 300 <= code < 500:
            return "failed"