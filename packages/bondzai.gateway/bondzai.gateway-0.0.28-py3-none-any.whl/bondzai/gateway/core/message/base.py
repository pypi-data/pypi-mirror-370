from enum import Enum
from dataclasses import dataclass
from io import BytesIO
import msgpack

from ..logger import log

from .event import EventMessagePayload
from .command import CommandMessagePayload
from .response import ResponseMessagePayload
from .payload import MessagePayload
from .utils import B2B64, msg_deserialize, msg_serialize, pack_list_to_buffer, B642B


class MSG_TYP(Enum):
    COMMAND     = 0
    RESPONSE    = 1
    ERR         = 2
    EVENT       = 3


@dataclass
class MsgHeader:
    session: bytes
    id: int
    op: int
    typ: int
    mod: int

    def to_dict(self) -> str:
        return {
            "session": B2B64(self.session),
            "id": self.id,
            "op": self.op,
            "typ": self.typ,
            "mod": self.mod
        }

    def to_array(self) -> list:

        #make sure session is 32 bytes, else pad
        if len(self.session) < 32:
            self.session = self.session + bytearray(32-len(self.session))

        return [
            self.session, 
            self.id, 
            self.op, 
            self.typ, 
            self.mod
        ]


class Message(object):
    def __init__(self, raw_data: list = None) -> None:
        self.header: MsgHeader = MsgHeader(*raw_data[:5]) if raw_data is not None else None
        self.payloads: list[MessagePayload] = []

        if raw_data is not None:
            payload = None
            if self.header.typ == MSG_TYP.EVENT.value:
                payload = EventMessagePayload.from_array(
                    self.header.op, 
                    raw_data[5:]
                )
            elif self.header.typ == MSG_TYP.COMMAND.value:
                payload = CommandMessagePayload.from_array(
                    self.header.mod,
                    self.header.op, 
                    raw_data[5:]
                )
            elif self.header.typ == MSG_TYP.RESPONSE.value:
                payload = ResponseMessagePayload.from_array(
                    self.header.mod,
                    self.header.op, 
                    raw_data[5:]
                )
            else:
                log(f"Unknown type {str(self.header.typ)}", logger_level="ERROR")
                
            if payload is not None:
                self.payloads.append(payload)

    def to_dict(self) -> dict:
        res = {
            "header": self.header.to_dict(),
            "payloads": [p.to_dict() for p in self.payloads]
        }
        return res

    def to_json(self) -> str:
        return msg_serialize(self.to_dict())

    @classmethod
    def from_json(cls, json_data: str) -> "Message":
        try:
            data = msg_deserialize(json_data)
        except Exception as e:
            log(f"Error parsing json in {str(e)}", logger_level="ERROR")
            return None

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        if "header" not in data:
            log("Missing Header in data", logger_level="ERROR")
            return None
        
        if "payloads" not in data:
            log("Missing payloads in data", logger_level="ERROR")
            return None
            
        if isinstance(data["header"]["session"], str):
            data["header"]["session"] = B642B(data["header"]["session"])

        m = Message()
        m.header = MsgHeader(**data["header"])

        for payload in data["payloads"]:
            #FIXME: (JDE) I think this should be done in the to_array function of the class
            #if "buffer" in payload["data"] and type(payload["data"]["buffer"][0]) == (float):                
            if "buffer" in payload["data"] and "datatype" in payload["data"] and payload["data"]["datatype"][-1] == "f":
                payload["data"]["buffer"] = pack_list_to_buffer(payload["data"]["buffer"], True, "f")

            if m.header.typ == MSG_TYP.COMMAND.value:
                p = CommandMessagePayload.from_json(
                    data["header"]["mod"],
                    data["header"]["op"], 
                    payload                    
                )
            elif m.header.typ == MSG_TYP.EVENT.value:
                p = EventMessagePayload.from_json(
                    data["header"]["op"], 
                    payload
                )
            else:
                log(f"This message type is not supported : {str(m.header)}", logger_level="ERROR")

            m.payloads.append(p)

        return m

    @classmethod
    def from_msgpack(cls, data: bytearray) -> "Message":
        try:
            raw_data = []

            unpacker = msgpack.Unpacker(BytesIO(data), raw=False)
            for unpacked in unpacker:
                raw_data.append(unpacked)

            return cls(raw_data)
        except Exception as e:
            log(f"Error parsing msgpck in {str(e)}", logger_level="ERROR")
            return None

    def to_msgpack(self) -> bytes:
        raw_data = self.header.to_array()

        for payload in self.payloads:
            if "header" in payload.__dict__:
                raw_data.extend(payload.header.to_array())
            if "event" in payload.__dict__:
                raw_data.extend(payload.event.to_array())
            if "command" in payload.__dict__:
                raw_data.extend(payload.command.to_array())

        packer = msgpack.Packer()
        buffer = BytesIO()
        for i in range(len(raw_data)):
            data = raw_data[i]
            buffer.write(packer.pack(data))
        buffer.seek(0)

        return buffer.read()


class Handshake(object):

    def __init__(self, hid: int, agent_id: bytes) -> None:
        self.hid = hid
        self.agent_id = agent_id

