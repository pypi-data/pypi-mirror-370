from functools import wraps

def extract_data_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)

        if isinstance(response, dict) and "data" in response:
            return response["data"]

        return response

    return wrapper
