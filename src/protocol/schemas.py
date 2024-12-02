import json

from pydantic import BaseModel
from pydantic.v1 import validator


class Request(BaseModel):
    type: str
    user: str


class JoinRequest(Request):
    type: str = 'join'


class ShipType(BaseModel):
    name: str
    length: int
    hits: int


class BoardType(BaseModel):
    size: int
    grid: list[list[str]]
    ships: list[ShipType]


class BoardRequest(Request):
    type: str = 'board'
    board: BoardType


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
