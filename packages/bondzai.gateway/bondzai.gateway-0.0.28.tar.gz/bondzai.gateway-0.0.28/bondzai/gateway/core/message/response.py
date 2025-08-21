import msgpack
from dataclasses import dataclass
from io import BytesIO

from ..logger import log

from .payload import MessagePayload
from .enums import BLDCommandParameter, CommandOperationID, MALCommandParameter, MessageModule, LogCommand, DBMCommand, LogCommandParameter,\
                    DBMCommandParameter, RUNCommandParameter
from .process_dbm import DbmProcesser
from .utils import B2B64, B642B


@dataclass
class ResponseGetLogNbKpi:
    itemid: int    
    number: int

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "number": self.number
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.number
        ]
    

@dataclass
class ResponseGetMalLifeCycle:
    itemid: int    
    lifecycle: int

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "lifecycle": self.lifecycle
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.lifecycle
        ]


@dataclass
class ResponseSet:
    itemid: int    

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
        }

    def to_array(self) -> list:
        return [
            self.itemid,
        ]


@dataclass
class ResponseBldSetInitDone(ResponseSet):
    pass


@dataclass
class ResponseLogGetKpi:
    itemid: int
    execid: int
    result: int
    appuid: int
    typ: int
    kpid: int
    description: str
    value: int

    def to_dict(self) -> str:
        # Translate the kpid
        vmid,modelid = self.translate_kpi()
        return {
            "itemid": self.itemid,
            "execid": self.execid,
            "result": self.result,
            "appuid": self.appuid,
            "typ": self.typ,
            "kpid": self.kpid,
            "vmid": vmid,
            "modelid": modelid,
            "description": self.description,
            "value": self.value,
        }

    def to_array(self) -> list:
        vmid,modelid = self.translate_kpi()
        return [
            self.itemid,
            self.execid,
            self.result,
            self.appuid,
            self.typ,
            self.kpid,
            vmid,
            modelid,
            self.description,
            self.value
        ]

    def translate_kpi(self):
        modelid = 0
        vmid = 0
        kpid = self.kpid
        if kpid :
            mask = 2**8-1
            mask = mask<<24
            iscustom = (kpid & mask)>> 24

            if iscustom == 0:
                mask = 2**8-1
                mask = mask<<16
                vmid = (kpid & mask)>> 16

                mask = 2**8-1
                mask = mask<<8
                modelid = (kpid & mask)>> 8

                mask = 2**8-1
                typeid = (kpid & mask)
        return vmid,modelid


@dataclass
class ResponseDbmTableInfo:
    handle      : int
    typ         : int
    nbrows      : int
    rowsize     : int
    count       : int
    reserved    : int
    used        : int

    def to_dict(self) -> str:
        return {
            "handle"    : self.handle,
            "typ"       : self.typ,
            "nbrows"    : self.nbrows,
            "rowsize"   : self.rowsize,
            "count"     : self.count,
            "reserved"  : self.reserved,
            "used"      : self.used
        }

    def to_array(self) -> list:
        return [
            self.handle,
            self.typ,
            self.nbrows,
            self.rowsize,
            self.count,
            self.reserved,
            self.used
        ]


@dataclass(init=False)
class ResponseDbmGetInfo:    
    itemid: int    
    tables: list[ResponseDbmTableInfo]

    def __init__(self,itemid,tables):
        self.itemid = itemid
        self.tables = [ResponseDbmTableInfo(*t) for t in tables]


    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "tables": [t.to_dict() for t in self.tables]
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            [t.to_array for t in self.tables]
        ]


@dataclass
class ResponseDbmExportRow:
    itemid: int
    execid: int
    result: int
    attributes: dict

    def to_dict(self) -> str:
        att = DbmProcesser.from_msgpack(self.attributes)
        if att is None:
            att_as_dict = {}
        else:
            att_as_dict= att.to_dict()
        return {
            "itemid": self.itemid,
            "execid": self.execid,
            "result": self.result,
            "attributes": att_as_dict
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.execid,
            self.result,
            self.attributes
        ]


@dataclass
class ResponseRunGetOps:
    itemid: int
    ops: list

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "ops": self.ops
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.ops
        ]

@dataclass
class ResponseRunApp:
    uuid: bytes
    desc: str
    threads: int
    mem: list[int]
    ops: list[int]
    meta: dict

    def to_dict(self) -> str:

        stream = BytesIO(self.meta)
        unpacker = msgpack.Unpacker(stream, raw=False, strict_map_key=False)

        meta = unpacker.unpack()
        return {
            "uuid": B2B64(self.uuid),
            "desc": self.desc,
            "threads": self.threads,
            "mem": self.mem,
            "ops": self.ops,
            "meta": meta
        }
    
    def to_array(self) -> list:
        packer = msgpack.Packer()
        buffer = BytesIO()
        buffer.write(packer.pack(self.meta))
        buffer.seek(0)
        return [
            B642B(self.uuid),
            self.desc,
            self.threads,
            self.mem,
            self.ops,
            buffer.read()
        ]


@dataclass
class ResponseRunGetApps:
    itemid: int
    apps: list

    def to_dict(self) -> str:

        apps = [ResponseRunApp(*app).to_dict() for app in self.apps]

        return {
            "itemid": self.itemid,
            "apps": apps
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            [self.app.to_array() for self.app in self.apps]
        ]


@dataclass
class ResponseDbmCreateTable:
    itemid: int
    execid: int
    result: int

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "execid": self.execid,
            "result": self.result,
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.execid,
            self.result,
        ]


@dataclass
class ResponseDbmImportRow:
    itemid: int
    execid: int
    result: int

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "execid": self.execid,
            "result": self.result,
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.execid,
            self.result,
        ]


OP_TO_RESPONSE_TYPES = {
    MessageModule.LOG.value: {
        CommandOperationID.CMD_GET.value : {
            LogCommandParameter.LOG_NB_KPIS.value: ResponseGetLogNbKpi,
        },    

        CommandOperationID.CMD_START.value : {
            LogCommand.LOG_GET_KPI.value: ResponseLogGetKpi
        } 
    },

    MessageModule.DBM.value: {
        CommandOperationID.CMD_GET.value : {
            DBMCommandParameter.DBM_PARAM_INFO.value: ResponseDbmGetInfo,
        },    

        CommandOperationID.CMD_START.value : {
            DBMCommand.DBM_EXPORT_ROW.value: ResponseDbmExportRow,
            DBMCommand.DBM_CREATE_TABLE.value: ResponseDbmCreateTable,
            DBMCommand.DBM_IMPORT_ROW.value: ResponseDbmImportRow
        } 
    },

    MessageModule.RUN.value: {
        CommandOperationID.CMD_GET.value : {
            RUNCommandParameter.RUN_PARAM_OPS.value: ResponseRunGetOps,
            RUNCommandParameter.RUN_PARAM_APPS.value: ResponseRunGetApps,
        },
    },

    MessageModule.BLD.value: {
        CommandOperationID.CMD_SET.value : {
            BLDCommandParameter.BLD_PARAM_CORTEXM_INIT_DONE.value: ResponseBldSetInitDone,
        },
    },

    MessageModule.MAL.value: {
        CommandOperationID.CMD_GET.value : {
            MALCommandParameter.MAL_PARAM_LIFE_CYCLE.value: ResponseGetMalLifeCycle,
        },
    },

}


def get_response_class(mod: int, op_id: int, raw_data: list):
    if not mod in OP_TO_RESPONSE_TYPES:
        return None

    if not op_id in OP_TO_RESPONSE_TYPES[mod]:
        return None

    if op_id in (CommandOperationID.CMD_GET.value, CommandOperationID.CMD_SET.value, CommandOperationID.CMD_START.value):
        return OP_TO_RESPONSE_TYPES[mod][op_id].get(raw_data[0], None)

    return OP_TO_RESPONSE_TYPES[mod][op_id]


class ResponseMessagePayload(MessagePayload):
    @classmethod
    def from_array(cls, mod: int, operation: int, raw_data: list) -> "MessagePayload":
        response_class = get_response_class(mod, operation, raw_data)
        if response_class is None:
            log(f"Operation {operation} unknown", logger_level="ERROR")
            return

        payload = cls()
        payload.command = response_class(*raw_data)

        return payload

    @classmethod
    def from_json(cls, mod: int, operation: int, raw_data: list) -> "MessagePayload":
        response_class = get_response_class(mod, operation, raw_data)
        if response_class is None:
            log(f"Operation {operation} unknown", logger_level="ERROR")
            return
            
        payload = cls()
        payload.command = response_class(**raw_data["data"])

        return payload

    def to_dict(self) -> dict:
        return {
            "data": self.command.to_dict()
        }
