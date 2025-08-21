import selectors
import socket
import traceback
import time

from ..core.packets_handler import PacketsHandler
from ..core.device import Device
from ..core.observer import dispatcher
from ..core.events import ApplicationEvents, DeviceEvents
from ..core.logger import log
from ..core.message.base import Handshake, Message
from .base import DeviceConnector


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9588
DEFAULT_HEADER_LEN = 4
DEFAULT_MAX_MSG_LEN = 4096



class RecvStatus:
    def __init__(self, device):
        self.device = device
        self.expected = 0
        self.binary_data = []


class SocketServerConnector(DeviceConnector):

    def __init__(self, config: dict = {}) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._selector = selectors.DefaultSelector()

        self._host = config.get("host", DEFAULT_HOST)
        self._port = config.get("port", DEFAULT_PORT)
        self._pck_max_len = config.get("pck_max_len", DEFAULT_MAX_MSG_LEN)

        self._run = False

        self._handler = PacketsHandler()

        dispatcher.add_observer(ApplicationEvents.ON_QUIT, self.on_exit)

    def on_exit(self):
        self._run = False

    def open(self) -> None:
        self._socket.bind((self._host, self._port))
        self._socket.listen()
        self._socket.setblocking(False)

        log(f"Socket Server Listenning on {self._host}:{self._port}")

        self._selector.register(self._socket, selectors.EVENT_READ, data=None)

    def close(self) -> None:
        log(f"Socket Server Closing")
        self._socket.close()
        self._selector.close()

    def new_device(self, socket: socket.socket) -> None:
        conn, addr = socket.accept()  # Should be ready to read

        device = Device()

        conn.setblocking(False)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self._selector.register(conn, events, data=RecvStatus(device))

        # JDE: the connected event is sent only whe, the device is ready 

    def on_device_msg(self, device: Device, socket: socket.socket, msg: Message) -> None:
        msg_str = msg.to_json()
        if len(msg_str) > 128:
            log(f"Socket Server Got message from {device.name}: {msg_str[:64]} ... {msg_str[-64:]}")
        else:
            log(f"Socket Server Got message from {device.name}: {msg_str}")

        dispatcher.notify(DeviceEvents.ON_MESSAGE, device, msg)

    def read_device(self, socket: socket.socket, status: RecvStatus) -> Message:
        log(f"Socket Server Got Msg")

        if status.expected == 0:
            length_data = []
            while len(length_data) < DEFAULT_HEADER_LEN:
                try:
                    length_data += socket.recv(DEFAULT_HEADER_LEN - len(length_data))
                except BlockingIOError:
                    return None
                except ConnectionResetError as err:
                    log(f"Socket Connector: Connection Reset Error Reading Device {err}", logger_level="ERROR")
                    raise err
                
                if len(length_data) == 0:
                    raise RuntimeError("Socket was closed")

            status.expected = int.from_bytes(length_data, "little")
            status.binary_data = []

        log(f"Socket waiting for {status.expected-len(status.binary_data)} bytes.", logger_level="INFO")
        while len(status.binary_data) < status.expected:
            try:
                status.binary_data += socket.recv(status.expected - len(status.binary_data))
            except BlockingIOError:
                return None
            except ConnectionResetError as err:
                log(f"Socket Connector: Connection Reset Error Reading Device {err}", logger_level="ERROR")
                raise err
           
            if len(status.binary_data) == 0:
                raise RuntimeError("Socket was closed")
        
        status.expected = 0

        return self._handler.push(bytearray(status.binary_data.copy()))

    def handle_connection(self, key, mask) -> None:
        sock = key.fileobj
        status: RecvStatus = key.data

        did_something = False
        try:
            if mask & selectors.EVENT_READ:
                did_something = True
                try:
                    msg = self.read_device(sock, status)
                    if msg:
                        if type(msg) == Handshake:
                            log("Got handshake from device: %s" % msg.agent_id)
                            status.device.set_name(msg.hid,msg.agent_id)

                        if type(msg) == Message:
                            self.on_device_msg(status.device, sock, msg)
                except RuntimeError as e:
                    self._selector.unregister(sock)
                    log(f"Closing case 1.1 {str(e)}", logger_level="ERROR")
                    sock.close()
                    dispatcher.notify(DeviceEvents.DISCONNECTED, status.device)
                except ConnectionResetError as e:
                    log(f"Closing case 1.2 {str(e)}", logger_level="ERROR")
                    dispatcher.notify(DeviceEvents.DISCONNECTED, status.device)

            if mask & selectors.EVENT_WRITE:
                if len(status.device.out_data):
                    did_something = True
                    data = status.device.out_data[0]
                    l = len(data)
                    log(f"Socket sending {l} bytes to device.")
                    remaining = 4
                    while (remaining):
                        remaining -= sock.send(l.to_bytes(4, "little"))
                    remaining = l
                    while (remaining):
                        remaining -= sock.send(data)
                    status.device.out_data = status.device.out_data[1:]

        except (ConnectionResetError, BrokenPipeError):
            self._selector.unregister(sock)
            log("Closing case 2", logger_level="ERROR")
            sock.close()
            dispatcher.notify(DeviceEvents.DISCONNECTED, status.device)
        except BlockingIOError:
            pass
        except Exception as e: 
            log(e, logger_level="ERROR")
            # raise e

        return did_something

    def run(self) -> None:
        try:
            self._run = True
            while self._run:
                ev = self._selector.select(timeout=1)
                if len(ev) == 0:
                    time.sleep(0.0001) # nothing was done so we give back then hand to the OS
                for key, mask in ev:
                    if key.data is None:
                        self.new_device(key.fileobj)
                    else:
                        if not self.handle_connection(key, mask):
                            time.sleep(0.0001) # nothing was done so we give back then hand to the OS
        except KeyboardInterrupt:
            self._run = False
        except Exception as e:
            log(e, logger_level="ERROR")
            traceback.print_exc()
        finally:
            log("Closing case 3")
            self.close()
