import asyncio
import atexit
import importlib
import yaml
import os
from inspect import isclass
from pathlib import Path
from yaml.loader import SafeLoader
import threading
from uuid import UUID

from .device import Device
from .logger import init_logging, log
from .manager import Manager
from .message.base import Message
from .websocket.utils import ws_client_serialize
from .events import DeviceEvents, WebsocketEvents
from .observer import dispatcher
from .websocket.connector import WebSocketConnector
from .websocket.client import WebsocketClient
from .websocket.request import ACT_GET_DEVICES_LIST, ACT_SEND_TO_DEVICE, ACT_SUB_TO_DEVICE, ACT_UNSUB_FROM_DEVUCE, \
            ACT_TRANSFERS_TO_WS_CLIENTS, EVT_ON_CLIENT_MSG, EVT_ON_DEVICE_MSG, WebsocketRequest
from .fsm import get_files

from ..device_connectors.base import DeviceConnector


CONFIG_DEFAULT_PATH: Path = Path(__file__).parent.parent / "config.yml"
CONNECTORS_PATH: Path = Path(__file__).parent.parent / "device_connectors"


class Application(object):
    def __init__(self, config_file_path: Path = CONFIG_DEFAULT_PATH) -> None:
        # Loading Configs
        self.config = {}
        self.load_config(config_file_path)
        init_logging(self.config.get("logs", None))

        # Init Device Manager
        Manager.Init()

        # Websocket server
        self.websocket_handler = WebSocketConnector(self.config.get("websocketserver", {}))

        # Device connectors
        self._connectors: list[DeviceConnector] = []
        self.load_connectors()

        # Adding event observers
        dispatcher.add_observer(WebsocketEvents.ON_REQUEST, self.handle_ws_client_request)
        dispatcher.add_observer(WebsocketEvents.CONNECTED, self.on_websocket_client_connected)
        dispatcher.add_observer(WebsocketEvents.DISCONNECTED, self.on_websocket_client_disconnected)
        dispatcher.add_observer(DeviceEvents.CONNECTED, self.on_device_connected)
        dispatcher.add_observer(DeviceEvents.DISCONNECTED, self.on_device_disconnected)
        dispatcher.add_observer(DeviceEvents.ON_MESSAGE, self.on_device_message)

    def load_config(self, config_file: Path) -> None:
        # Loading yaml config file
        try:
            with open(config_file) as f:
                self.config = yaml.load(f, Loader=SafeLoader)
        except Exception as e:
            raise RuntimeError(str(e))

    def load_connectors(self) -> None:
        # Loading active connectors from config
        config_connectors = self.config.get("connectors", {})
        active_connector_names = [k for k in config_connectors.keys() if config_connectors[k].get("active", False)]

        # Getting all python files in our connector directory path
        for connector_name in get_files(str(CONNECTORS_PATH), "py"):
            if connector_name not in ["__init__.py", "base.py", "__pycache__"]:
                # Loading the python module file
                connector_module_name = connector_name.replace(".py", "")
                # log(f"Application Loading Connector from module {connector_module_name}")
                mo = importlib.import_module(f".device_connectors.{connector_module_name}", package="bondzai.gateway")

                # Getting connectors classes from loaded module
                connector_cls = None
                for attr in dir(mo):
                    if attr != "DeviceConnector" and attr in active_connector_names:
                        log(f"Application Loading Connector {attr}")
                        connector_cls = getattr(mo, attr)
                        # If our object is a class and a sub class of DeviceConnector
                        # Then we add it to our connectors list
                        if isclass(connector_cls) and issubclass(connector_cls, DeviceConnector):
                            connector = connector_cls(config_connectors[attr].get("config", {}))
                            self._connectors.append(connector)

    def run(self) -> None:
        # Run open method for each active connectors
        for instance in self._connectors:
            instance.open()
        
        # TODO : Find Windows solution
        def clean_exit():
            log("Exiting application")
            # Cleanning active connectors
            for c in self._connectors:
                c.close()
        atexit.register(clean_exit)

        # Method for WebSocketServer Thread
        def run_websockets_server():
            asyncio.run(self.websocket_handler.run())

        threads = []

        # Creating Thread for WebSocketServer
        t = threading.Thread(target=run_websockets_server, daemon=True)
        threads.append(t)
        # Launching thread
        t.start()

        for c in self._connectors:
            # Creating thread for active connector
            x = threading.Thread(target=c.run, daemon=True)
            threads.append(x)
            # Launching thread
            x.start()
        
        try:
            for x in threads:
               # Waiting threads to finish
                x.join()
        except KeyboardInterrupt:
            pass

    # Callback for WebSocketServer event ON_REQUEST
    def handle_ws_client_request(self, client: WebsocketClient, request: WebsocketRequest):
        log(f"Application Got Client ({client.id}) Request : {request.to_string()}")

        # Handle client request. Could be:
        #   - Register to device events
        #   - Unregister from device events
        #   - Get Device List
        #   - Send to device

        if request.action == ACT_SUB_TO_DEVICE:
            Manager.SubToDeviceEvents(request.device_name, client)
        elif request.action == ACT_UNSUB_FROM_DEVUCE:
            Manager.UnsubFromDeviceEvents(request.device_name, client)
        elif request.action == ACT_GET_DEVICES_LIST:
            self.send_device_list_to_clients(client)
        elif request.action == ACT_TRANSFERS_TO_WS_CLIENTS:
            self.transfers_msg_to_clients(request.message, client.id, request.to_client_id)
        elif request.action == ACT_SEND_TO_DEVICE:
            device = Manager.GetDevice(request.device_name)
            if device:
                msg = Message.from_json(request.message)

                # Force the session id to be the one generated at handshake
                msg.header.session = device.session.bytes

                device.send(msg.to_msgpack())

    def send_device_list_to_clients(self, client: WebsocketClient = None) -> None:
        # if a client is specified, we send the list only to him, else to all clients
        clients = [client] if client is not None else Manager.GetClients()
        device_list = [d.name for d in Manager.GetDevices()]
        msg = ws_client_serialize({
            "action": ACT_GET_DEVICES_LIST,
            "devices": device_list
        })

        for client in clients:
            client.send(msg)

    def transfers_msg_to_clients(self, msg: str, from_client_id: UUID, to_client: str = None) -> None:
        for client in Manager.GetClients():
            if client.id != from_client_id and (not to_client or str(to_client) == str(client.id)):
                client.send(ws_client_serialize({
                    "from_client_id": str(from_client_id),
                    "action": EVT_ON_CLIENT_MSG,
                    "message": msg
                }))

    # Callback for Device event CONNECTED
    def on_device_connected(self, device: Device) -> None:
        log(f"New device connected {device.name}")
        Manager.RegisterDevice(device)
        self.send_device_list_to_clients()

    # Callback for Device event DISCONNECTED
    def on_device_disconnected(self, device: Device) -> None:
        log(f"Device disconnected {device.name}")
        Manager.UnregisterDevice(device)
        self.send_device_list_to_clients()

    # Callback for Device Event ON_MESSAGE
    def on_device_message(self, device: Device, msg: Message) -> None:
        # TODO : Handle msg       
        # TMP : For now send msg to every subscribed websocket clients
        log(f"Application On Device Message {device.name}")
        for client in Manager.GetDeviceEventSubs(device.name):
            log(f"Application Forward")
            client.send(ws_client_serialize({ 
                "action": EVT_ON_DEVICE_MSG,
                "device_name": device.name,
                "message": msg.to_dict()
            }))

    # Callback when a websocket client is connected
    def on_websocket_client_connected(self, client: WebsocketClient) -> None:
        Manager.RegisterClient(client)

    # Callback when a websocket client is disconnected
    def on_websocket_client_disconnected(self, client: WebsocketClient) -> None:
        log(f"Websocket Client {client.id} disconnected")
        Manager.UnregisterClient(client)
        Manager.UnsubClient(client)
