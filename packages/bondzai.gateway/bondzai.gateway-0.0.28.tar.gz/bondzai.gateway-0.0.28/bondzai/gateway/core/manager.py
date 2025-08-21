from uuid import UUID

from .device import Device
from .websocket.client import WebsocketClient


class Manager(object):
    _devices: dict[str, Device] = {}
    _clients: dict[UUID, WebsocketClient] = {}
    _subscriptions: dict[str, dict[str, dict[UUID, WebsocketClient]]] = {}

    @classmethod
    def Init(cls) -> None:
        cls._devices = {}
        cls._subscriptions = {}

    @classmethod
    def RegisterDevice(cls, device: Device) -> None:
        cls._devices[str(device.name)] = device

    @classmethod
    def UnregisterDevice(cls, device: Device, remove_subs: bool = True) -> None:
        if device.name in cls._devices:
            del cls._devices[device.name]
        
        if remove_subs and device.name in cls._subscriptions:
            del cls._subscriptions[device.name]

    @classmethod
    def GetDevices(cls) -> list[Device]:
        return list(cls._devices.values())

    @classmethod
    def GetDevice(cls, device_name: str) -> Device:
        return cls._devices.get(device_name, None)

    @classmethod
    def RegisterClient(cls, client: WebsocketClient) -> None:
        cls._clients[client.id] = client

    @classmethod
    def UnregisterClient(cls, client: WebsocketClient) -> None:
        if client.id in cls._clients:
            del cls._clients[client.id]

    @classmethod
    def GetClients(cls) -> list[WebsocketClient]:
        return list(cls._clients.values())

    @classmethod
    def GetClient(cls, client_id: UUID) -> WebsocketClient:
        return cls._clients.get(client_id, None)

    # For now we only register to all events, but we have the posibility to 
    # register only for specific events

    @classmethod
    def SubToDeviceEvents(cls, device_name: str, client: WebsocketClient) -> None:
        if device_name not in cls._subscriptions:
            cls._subscriptions[device_name] = { "ALL": {} }
        cls._subscriptions[device_name]["ALL"][client.id] = client

    @classmethod
    def UnsubFromDeviceEvents(cls, device_name: str, client: WebsocketClient) -> None:
        if device_name in cls._subscriptions:
            if client.id in cls._subscriptions[device_name]["ALL"]:
                del cls._subscriptions[device_name]["ALL"][client.id]

    @classmethod
    def GetDeviceEventSubs(cls, device_name: str) -> list[WebsocketClient]:
        return list(cls._subscriptions.get(device_name, {}).get("ALL", {}).values())

    @classmethod
    def UnsubClient(cls, client: WebsocketClient) -> None:
        for device_name in cls._subscriptions:
            cls.UnsubFromDeviceEvents(device_name, client)