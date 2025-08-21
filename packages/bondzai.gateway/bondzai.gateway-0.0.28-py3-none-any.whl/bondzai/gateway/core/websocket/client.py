from websockets import WebSocketServerProtocol
from uuid import uuid4
import asyncio

from ..logger import log


class WebsocketClient(object):
    last_sent = 0
    
    def __init__(self, socket: WebSocketServerProtocol) -> None:
        self.socket = socket
        self.id = uuid4()

    async def _do_send(self, msg: str) -> None:
        await self.socket.send(msg)

    def send(self, msg: str) -> None:
        if len(msg) < 128:
            log(f"Sending message to client, msg = {msg}")
        else:
            log(f"Sending message to client, msg = {msg[:64]} ... {msg[-64:]}")

        new_loop = False
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                # if the loop is not running we do as if there is none.
                raise
        except RuntimeError as e:
            if str(e).startswith('There is no current event loop in thread') or not loop.is_running():
                # If no loop or not running we create a new loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                new_loop = True
            else:
                log(f"Unable to send message to Websocket Client (no loop) : {str(e)}", logger_level="ERROR")
            
        if new_loop:
            # In the case of a new loop it means that we're not in
            # the websocket server thread. So we are in a connector thread
            # In that case we want to start asyncio and a new loop only to send
            # the message to the client then stop the loop
            loop.run_until_complete(self._do_send(msg))
            loop.close()
        else:
            # If it's not a new loop, then we're on the websocket server thread
            # And we just have to add a new task to the main running loop
            loop.create_task(self._do_send(msg))
