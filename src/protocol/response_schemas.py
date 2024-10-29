from pydantic import BaseModel
from typing import Optional


class AckResponse(BaseModel):
    type: str = 'ack'
    result: str
    user: str
    hit: Optional[bool] = None


class ServerMessage(BaseModel):
    type: str


class QuitNotification(ServerMessage):
    type: str = 'quit'
    user: str


class JoinNotification(ServerMessage):
    type: str = 'join'
    user: str


class WelcomeMessage(BaseModel):
    type: str = 'welcome'
    message: str = "Welcome to Battleship!"
