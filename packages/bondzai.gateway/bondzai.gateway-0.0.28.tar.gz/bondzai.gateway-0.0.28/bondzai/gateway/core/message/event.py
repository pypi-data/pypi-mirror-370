from dataclasses import dataclass

from ..logger import log
from .payload import MessagePayload
from .utils import B642B, unpack_buffer_to_list, B2B64, get_step_struct
from .enums import EventOperationID

@dataclass
class EventHeader:
    mod: int 
    appid: int 
    timestamp: int
    payload_size: int

    def to_dict(self) -> str:
        return {
            "mod": self.mod,
            "appid": self.appid,
            "timestamp": self.timestamp,
            "payload_size": self.payload_size
        }

    def to_array(self) -> list:
        return [
            self.mod, 
            self.appid,
            self.timestamp, 
            self.payload_size
        ]


@dataclass
class EventDataIn:
    datasource: int
    datatype: str
    buffer: bytes

    def to_dict(self) -> str:
        return {
            "datasource": self.datasource,
            "datatype": self.datatype,
            "buffer": unpack_buffer_to_list(self.buffer, self.datatype[0] == "<", 4, self.datatype[1])
        }

    def to_array(self) -> list:
        return [
            self.datasource,
            self.datatype,
            self.buffer
        ]


@dataclass
class EventException:
    error: int
    msg: str

    def to_dict(self) -> str:
        return {
            "error": self.error,
            "msg": self.msg
        }

    def to_array(self) -> list:
        return [
            self.error,
            self.msg
        ]


@dataclass
class EventCMDStatus:
    mod: int
    op: int
    status: int

    def to_dict(self) -> str:
        return {
            "mod": self.mod,
            "op": self.op,
            "status": self.status
        }

    def to_array(self) -> list:
        return [
            self.mod,
            self.op,
            self.status
        ]


@dataclass
class EventLog:
    level: int
    msg: str

    def to_dict(self) -> str:
        return {
            "level": self.level,
            "msg": self.msg
        }

    def to_array(self) -> list:
        return [
            self.level,
            self.msg
        ]


@dataclass
class EventAslResult:
    label_type: int
    key_id: int
    confidence: float
    step: int
    result: list

    def to_dict(self) -> str:

        step_fields = get_step_struct(self.step)

        return {
            "label_type": self.label_type, # keep it for compatibility, it's equal to output
            "confidence": self.confidence,
            "source_id": step_fields.get("source_id",0),
            "process_id": step_fields.get("process_id",0),
            "ai_mode": step_fields.get("ai_mode",0),
            "record_mode": step_fields.get("record_mode",0),
            "output": step_fields.get("output",0),
            "result": self.result,
            "key_id": self.key_id            
        }

    def to_array(self) -> list:
        return [
            self.label_type,
            self.key_id,        
            self.confidence,
            self.step,
            self.result
        ]


@dataclass
class EventInferResult:
    ai_type:int
    label_type: int
    key_id: int
    step: int
    result: list

    def to_dict(self) -> str:
        step_fields = get_step_struct(self.step)

        return {
            "ai_type": self.ai_type,
            "label_type": self.label_type,
            "source_id": step_fields.get("source_id",0),
            "process_id": step_fields.get("process_id",0),
            "ai_mode": step_fields.get("ai_mode",0),
            "record_mode": step_fields.get("record_mode",0),
            "output": step_fields.get("output",0),
            "result": self.result,
            "key_id": self.key_id            
        }

    def to_array(self) -> list:
        return [
            self.ai_type,
            self.label_type,
            self.key_id,
            self.step,
            self.result
        ]


@dataclass
class EventSetMode:
    ai_mode: int
    ai_type: int
    data: list

    def to_dict(self) -> str:
        return {
            "ai_mode": self.ai_mode,
            "ai_type": self.ai_type,
            "data":self.data
        }
    
    def to_array(self) -> list:
        return [
            self.ai_mode,
            self.ai_type,
            self.data
        ]


@dataclass
class EventCorrection:
    position: int
    source_id: int
    ai_type: int
    data: list  # classification.label_type & classification.label OR regression

    def to_dict(self) -> str:
        return {
            "position": self.position,
            "source_id": self.source_id,
            "ai_type": self.ai_type,
            "data": self.data
        }

    def to_array(self) -> list:
        return [
            self.position,
            self.source_id,
            self.ai_type,
            self.data
        ]

@dataclass
class EventTrigger:
    trigger_type: int
    trigger_value: int
    key_id: int

    def to_dict(self) -> str:
        return {
            "trigger_type": self.trigger_type,
            "trigger_value": self.trigger_value,
            "key_id": self.key_id,
        }
    
    def to_array(self) -> list:
        return [
            self.trigger_type,
            self.trigger_value,
            self.key_id
        ]
 
@dataclass
class EventSetRecordMode:
    record_mode: int
    source_id: int

    def to_dict(self) -> str:
        return {
            "record_mode": self.record_mode,
            "source_id": self.source_id,
        }
    
    def to_array(self) -> list:
        return [
            self.record_mode,
            self.source_id
        ]
    
@dataclass
class EventLaunchTrain:

    def to_dict(self) -> str:
        return { }
    
    def to_array(self) -> list:
        return [ ]

@dataclass
class EventKill:

    def to_dict(self) -> str:
        return { }
    
    def to_array(self) -> list:
        return [ ]

@dataclass
class EventCustom:
    data: bytearray

    def __init__(self, data) -> None:
        if(type(data) == str):
            data = B642B(data)
        self.data = bytearray(data)

    def to_dict(self) -> str:
        return { "data": B2B64(self.data) }

    def to_array(self) -> list:
        return [ self.data ]
    

@dataclass
class EventProcessAck:
    evt_id: int
    process_state: int
    step: int
    app_id: int
    meta: bytes

    def to_dict(self) -> str:
        step_fields = get_step_struct(self.step)
        return {
            "evt_id": self.evt_id,
            "process_state": self.process_state,
            "source_id": step_fields.get("source_id",0),
            "process_id": step_fields.get("process_id",0),
            "ai_mode": step_fields.get("ai_mode",0),
            "record_mode": step_fields.get("record_mode",0),
            "output": step_fields.get("output",0),
            "app_id": self.app_id,
            "meta": self.meta
        }

    def to_array(self) -> list:

        return [
            self.evt_id,
            self.process_state,
            self.step,
            self.app_id,
            self.meta
        ]


@dataclass
class EventDataResult:
    evt_id: int
    process_state: int
    step: int
    app_id: int
    datatype: str
    result: bytes

    def to_dict(self) -> str:
        listofresult = [unpack_buffer_to_list(b, self.datatype[0] == "<", 4, self.datatype[1]) for b in self.result]
        result = [item for onelist in listofresult for item in onelist]
        step_fields = get_step_struct(self.step)

        return {
            "evt_id": self.evt_id,
            "process_state": self.process_state,
            "source_id": step_fields.get("source_id",0),
            "process_id": step_fields.get("process_id",0),
            "ai_mode": step_fields.get("ai_mode",0),
            "record_mode": step_fields.get("record_mode",0),
            "output": step_fields.get("output",0),
            "app_id": self.app_id,
            "datatype": self.datatype,
            "result": result
        }

    def to_array(self) -> list:
        return [
            self.evt_id,
            self.process_state,
            self.step,
            self.app_id,
            self.datatype,
            self.result
        ]
    

@dataclass
class EventTrainResult:
    evt_id: int
    process_state: int
    step: int
    app_id: int
    nb_models: int

    def to_dict(self) -> str:
        step_fields = get_step_struct(self.step)

        return {
            "evt_id": self.evt_id,
            "process_state": self.process_state,
            "source_id": step_fields.get("source_id",0),
            "process_id": step_fields.get("process_id",0),
            "ai_mode": step_fields.get("ai_mode",0),
            "record_mode": step_fields.get("record_mode",0),
            "output": step_fields.get("output",0),
            "app_id": self.app_id,
            "nb_models": self.nb_models
        }

    def to_array(self) -> list:
        return [
            self.evt_id,
            self.process_state,
            self.step,
            self.app_id,
            self.nb_models
        ]    

OP_TO_EVENT_TYPES = {
    EventOperationID.EVT_EXT_EXCEPTION.value:     EventException,
    EventOperationID.EVT_EXT_DATA_IN.value:       EventDataIn,
    EventOperationID.EVT_EXT_CMD_STATUS.value:    EventCMDStatus,
    EventOperationID.EVT_EXT_LOG.value:           EventLog,
    EventOperationID.EVT_EXT_ASL_RESULT.value:    EventAslResult, 
    EventOperationID.EVT_EXT_VM_RESULT.value:     EventInferResult, 
    EventOperationID.EVT_EXT_SET_MODE.value:      EventSetMode,
    EventOperationID.EVT_EXT_CORRECTION.value:    EventCorrection,
    EventOperationID.EVT_EXT_TRIGGER.value:       EventTrigger,
    EventOperationID.EVT_EXT_SET_RECORD_MODE.value: EventSetRecordMode,
    EventOperationID.EVT_EXT_LAUNCH_TRAIN.value:  EventLaunchTrain,
    EventOperationID.EVT_EXT_KILL.value:          EventKill,
    EventOperationID.EVT_EXT_CUSTOM_1.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_2.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_3.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_4.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_5.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_6.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_7.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_8.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_9.value:      EventCustom,
    EventOperationID.EVT_EXT_CUSTOM_10.value:     EventCustom,
    EventOperationID.EVT_EXT_PROCESS_ACK.value:   EventProcessAck,
    EventOperationID.EVT_EXT_DATA_TRANSFORM_RESULT.value:   EventDataResult,
    EventOperationID.EVT_EXT_DATA_ACQ_RESULT.value:   EventDataResult,
    EventOperationID.EVT_EXT_ENROLL_RESULT.value: EventDataResult,
    EventOperationID.EVT_EXT_DATASET_PREPARATION_RESULT.value: EventTrainResult,
    EventOperationID.EVT_EXT_TRAINING_RESULT.value: EventTrainResult
}

def GetEventClass(event_type_id: int):
    return OP_TO_EVENT_TYPES.get(event_type_id, None)

class EventMessagePayload(MessagePayload):
    @classmethod
    def from_array(cls, operation: int, raw_data: list) -> "MessagePayload":
        EventClass = GetEventClass(operation)
        if EventClass is None:
            log(f"Operation {operation} unknown", logger_level="ERROR")
            return

        payload = cls()
        payload.header = EventHeader(*raw_data[:4])
        payload.event = EventClass(*raw_data[4:])

        return payload

    @classmethod
    def from_json(cls, operation: int, raw_data: list) -> "MessagePayload":
        EventClass = GetEventClass(operation)
        if EventClass is None:
            log(f"Operation {operation} unknown", logger_level="ERROR")
            return
            
        payload = cls()
        payload.header = EventHeader(**raw_data["header"])
        payload.event = EventClass(**raw_data["data"])

        return payload

    def to_dict(self) -> dict:
        return {
            "header": self.header.to_dict(),
            "data": self.event.to_dict()
        }
