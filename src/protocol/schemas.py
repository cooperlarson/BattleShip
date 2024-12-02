from pydantic import BaseModel


class Request(BaseModel):
    type: str
    user: str


class JoinRequest(Request):
    type: str = 'join'


class BoardRequest(Request):
    type: str = 'board'
    board: str


class MoveRequest(Request):
    type: str = 'move'
    row: int
    col: int


class ViewRequest(Request):
    type: str = 'view'
    user: str


class ChatRequest(Request):
    type: str = 'chat'
    message: str


class QuitRequest(Request):
    type: str = 'quit'

class SetNameRequest(Request):
    type: str = 'set_name'
    user: str
