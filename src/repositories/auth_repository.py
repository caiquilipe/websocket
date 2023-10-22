from models.authenticate import Request, Response
from fastapi.exceptions import HTTPException
import aiohttp
import os
import logging


async def authenticate(*args, **kwargs):
    body = Request(*args, **kwargs)
    url = f"{os.getenv('PLAYER_SERVICE_URL')}/authenticate"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv("PLAYER_SERVICE_API_KEY"),
    }
    logging.warning(f"authenticate: {body.model_dump()}")
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            url,
            json=body.model_dump(),
        ) as response:
            logging.warning(f"TA INDO: {response.status}")
            if not response.status == 200:
                logging.warning(f"authenticate error: {await response.json()}")
                raise HTTPException(
                    detail="Error on authenticate service",
                    status_code=response.status,
                )
            logging.warning(f"authenticate: {await response.json()}")
            return Response(**await response.json())
