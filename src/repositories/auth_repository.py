from models.authenticate import Request
from fastapi.exceptions import HTTPException
import aiohttp
import os
import logging


async def authenticate(*args, **kwargs):
    body = Request(*args, **kwargs)
    url = f"{os.getenv('AUTH_SERVICE_URL')}/authenticate"
    headers = {
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            url,
            json=body.model_dump(),
        ) as response:
            if not response.status == 200:
                logging.warning(f"Error on authenticate service: {response.status}")
                raise HTTPException(
                    detail="Error on authenticate service",
                    status_code=response.status,
                )
            return await response.json()
