from pydantic import BaseModel


class SensorResponse(BaseModel):
    access_token: str
