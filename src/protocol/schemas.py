from pydantic import BaseModel


class Request(BaseModel):
    type: str


class JoinRequest(Request):
    type: str = 'join'
    player_name: str


class MoveRequest(Request):
    type: str = 'move'
    player_name: str
    row: int
    col: int


class ChatRequest(Request):
    type: str = 'chat'
    player_name: str
    message: str


class QuitRequest(Request):
    type: str = 'quit'
    player_name: str
