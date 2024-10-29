from src.protocol.schemas import JoinRequest, Request
from src.util.error_handler import ClientErrorHandler


class GameMenu:
    def __init__(self, msg_processor):
        self.msg = msg_processor

    @ClientErrorHandler()
    def handle_response(self):
        if self.msg.request:
            request = Request(**self.msg.request)
            if request.type == "welcome":
                player_name = input("Enter your player name: ")
                self.msg.enqueue_message(JoinRequest(player_name=player_name).dict())
            elif request.type == "ack":
                result = self.msg.request.get("result")
                if result == "joined":
                    print(f"Successfully joined as {self.msg.request.get('player_name')}")
                elif result == "move_processed":
                    hit = self.msg.request.get("hit")
                    print(f"Move result: {'Hit!' if hit else 'Miss!'}")
                elif result == "chat_received":
                    print(f"Chat acknowledged for {self.msg.request.get('player_name')}")
                elif result == "quit_success":
                    print(f"Successfully quit the game for {self.msg.request.get('player_name')}")
