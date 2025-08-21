import uuid
from .observer import dispatcher
from .events import DeviceEvents

TAG_AGENT_ID = 0x01
TAG_SESSION = 0x02

class Device(object):

    def __init__(self) -> None:
        self.out_data = []
        self.in_data = b""
        self.hid = 0
        self.ready = False # The device is not ready until it received the handshake
        self.name = None # The device name is set on handshake
        self.session = None # The session is set on handshake


    def set_name(self, hid: int, name: str) -> None:
        """ Called on handshake """
        
        if (self.ready):
            raise RuntimeError("Device is already ready")
        
        self.ready = True

        # set the hid and name
        self.hid = hid
        self.name = str(name, "utf-8")
    
        # generate a session id
        self.session = uuid.uuid4()

        # send the session id to the device
        self.out_data += [ 
            b"\x11" + 
            self.hid.to_bytes(1,"little") + 
            TAG_SESSION.to_bytes(1,"little") + 
            len(self.session.bytes).to_bytes(1,"little") + 
            self.session.bytes 
        ]

        # notify of connection
        dispatcher.notify(DeviceEvents.CONNECTED, self)


    def send(self, data: bytes) -> None:
        self.out_data += [b"\x13"+self.hid.to_bytes(1,"little")+data]
