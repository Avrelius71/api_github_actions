from pydantic import BaseModel


class RequestPostAuth(BaseModel):
    username: str
    password: str


class ResponsePostAuth(BaseModel):
    token: str
