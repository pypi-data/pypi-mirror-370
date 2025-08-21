from enum import Enum


class WebsocketEvents(Enum):
    ON_REQUEST = "WEBSOCKET-ON-REQUEST"
    CONNECTED = "WEBSOCKET-CLIENT-CONNECTED"
    DISCONNECTED = "WEBSOCKET-CLIENT-DISCONNECTED"

    def __repr__(self) -> str:
        return self.value


class DeviceEvents(Enum):
    CONNECTED = "DEVICE_CONNECTED"
    DISCONNECTED = "DEVICE_DISCONNECTED"

    ON_MESSAGE = "ON_DEVICE_MESSAGE"

    def __repr__(self) -> str:
        return self.value


class ApplicationEvents(Enum):
    ON_QUIT = "APPLICATION-ON-QUIT"
    
    def __repr__(self) -> str:
        return self.value