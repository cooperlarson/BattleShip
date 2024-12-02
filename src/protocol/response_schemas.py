from pydantic import BaseModel
from typing import Optional

from src.protocol.schemas import BoardType


class AckResponse(BaseModel):
    type: str = 'ack'
    result: str
    user: str
    hit: Optional[bool] = None


class ServerMessage(BaseModel):
    type: str = 'info'
    message: str = ''


class QuitNotification(ServerMessage):
    type: str = 'quit'
    user: str


class JoinNotification(ServerMessage):
    type: str = 'join'
    user: str


class GameStartedNotification(ServerMessage):
    type: str = 'game_started'
    player1: str
    player2: str


class ViewResponse(BaseModel):
    type: str = 'view'
    user: str
    my_board: str
    opponent_board: str


class NameChangeResponse(BaseModel):
    type: str = 'set_name'
    user: str
    success: bool


class WelcomeMessage(BaseModel):
    type: str = 'welcome'
    message: str = "Welcome to Battleship!"


class TurnSwitchNotification(BaseModel):
    type: str = 'turn_switch'
    user: str
