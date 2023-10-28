from pydantic import BaseModel


class Request(BaseModel):
    user_token: str
    platform_token: str
    websocket_id: str
