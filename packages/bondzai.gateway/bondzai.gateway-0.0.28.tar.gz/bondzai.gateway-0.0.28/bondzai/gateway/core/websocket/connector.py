import asyncio
from websockets import WebSocketServerProtocol, serve

from ..logger import log
from ..observer import dispatcher
from ..events import WebsocketEvents
from ..websocket.client import WebsocketClient
from ..websocket.request import WebsocketRequest
from ..websocket.utils import ws_client_deserialize


DEFAULT_HOST="localhost"
DEFAULT_PORT=8765


class WebSocketConnector(object):
    def __init__(self, config: dict = {}) -> None:
        self._clients: set[WebsocketClient] = set()
        self._sockets: set[WebSocketServerProtocol] = set()
        self._host: str = config.get("host", DEFAULT_HOST)
        self._port: int = config.get("port", DEFAULT_PORT)

    async def on_message(self, socket: WebSocketServerProtocol) -> None:
        # We got a new client
        client = WebsocketClient(socket)
        self._clients.add(client)
        dispatcher.notify(WebsocketEvents.CONNECTED, client)
        log(f"WebSocket Server Got New Client {client.id}")

        # We'll loop asynchronously while client is connected
        # reading request it could send
        try:
            async for msg in socket:
                request = self.parse_request(msg)
                if request.is_valid():
                    dispatcher.notify(WebsocketEvents.ON_REQUEST, client=client, request=request)
        except Exception as err:
            log(f"Websocket error {err}", logger_level="ERROR")
            
        dispatcher.notify(WebsocketEvents.DISCONNECTED, client)
        try:
            self._clients.remove(client)
        except Exception as err:
            log(f"err removing Websocket {err}", logger_level="ERROR")
    
    async def run(self) -> None:
        # Serving server to host
        log(f"WebSocket Server Listenning on {self._host}:{self._port}")
        async with serve(self.on_message, self._host, self._port, max_size=None):
            await asyncio.Future()

    async def async_send_to_socket(self, socket: WebSocketServerProtocol, msg: str) -> None:
        await socket.send(msg)

    def send_to_socket(self, socket: WebSocketServerProtocol, msg: str) -> None:
        asyncio.create_task(self.async_send_to_socket(socket, msg))

    def parse_request(self, data: str) -> WebsocketRequest:
        try:
            # Loading json from recieved message
            # The mapping it to a request object
            # TODO: Maybe check that the request is valid here? 
            request_data = ws_client_deserialize(data)
            request = WebsocketRequest(**request_data)
            return request
        except Exception as e:
            log(f"Error parsing request data {str(e)}", logger_level="ERROR")
