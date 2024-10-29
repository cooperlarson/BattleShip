from pydantic import BaseModel


class Request(BaseModel):
    type: str
    user: str


class JoinRequest(Request):
    type: str = 'join'


class MoveRequest(Request):
    type: str = 'move'
    row: int
    col: int


class ChatRequest(Request):
    type: str = 'chat'
    message: str


class QuitRequest(Request):
    type: str = 'quit'
