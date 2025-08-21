import traceback
from serial import Serial
import threading

from ..core.packets_handler import PacketsHandler
from ..core.device import Device
from ..core.observer import dispatcher
from ..core.events import ApplicationEvents, DeviceEvents
from ..core.logger import log
from ..core.message.base import Handshake, Message
from .base import DeviceConnector


DEFAULT_PORT = "COM3"
MAX_PAYLOAD_SIZE = 4 * 1024





class RecvStatus:
    def __init__(self, device):
        self.device = device
        self.expected = 0
        self.binary_data = []


class SerialConnector(DeviceConnector):

    def __init__(self, config: dict = {}) -> None:
        self._port = config.get("port", DEFAULT_PORT)
        self._serial = None
        self._run = False

        self._handler = PacketsHandler()

        dispatcher.add_observer(ApplicationEvents.ON_QUIT, self.on_exit)

    def on_exit(self):
        self._run = False

    def open(self) -> None:
        self._serial = Serial(self._port)
        self._serial.baudrate = 115200;


    def close(self) -> None:
        log(f"Closing serial port")
        self._serial.close()

    def new_device(self) -> None:
        device = Device()
        dispatcher.notify(DeviceEvents.CONNECTED, device)
        x = threading.Thread(target=self._device_sender, args=(device,),daemon=True)
        x.start()

        return device

    def read_device(self) -> Message:
        length_array = self._serial.read(4)
        length =  int.from_bytes(length_array, "little")
        data = self._serial.read(length)

        try:
            msg = self._handler.push(data)
        except Exception as e:
            log(f"Error while handling packet: {e}")
            return None
        return msg

    def _device_sender(self,device):
        
        log("Serial Sender waiting for data...")
        while(self._run):
            if len(device.out_data) == 0:
                continue

            data = device.out_data[0]
            length =  len(data)
            if length > MAX_PAYLOAD_SIZE:
                log(f"Payload too big, max size is {MAX_PAYLOAD_SIZE} bytes")
                raise RuntimeError("Payload too big, max size is %d bytes" % MAX_PAYLOAD_SIZE)

            log(f"Sending {length} bytes to device")
            l1 = self._serial.write(length.to_bytes(4, "little"))
            self._serial.flush()
            l2 = self._serial.write(data)
            self._serial.flush()
            log(f"Sent {l1} header + {l2} payload to device")

            device.out_data = device.out_data[1:]
        log("Serial Sender ended")

    def run(self) -> None:
        log(f"Listening to serial port {self._port}")

        try:
            device = self.new_device()
            self._run = True
            while self._run:
                msg = self.read_device()
                if msg:
                    if type(msg) == Handshake:
                        log("Got handshake from device: %s" % msg.to_json())
                        device.set_name(msg.agent_id)

                    if type(msg) == Message:
                        log("Got message from device: %s" % msg.to_json())
                        dispatcher.notify(DeviceEvents.ON_MESSAGE, device, msg)


        except KeyboardInterrupt:
            self._run = False
        finally:
            log("Closing case 3")
            traceback.print_exc()
            self.close()
