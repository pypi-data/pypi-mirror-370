from dataclasses import dataclass

from ..logger import log
from .payload import MessagePayload
from .enums import CommandOperationID, MessageModule, LogCommand, DBMCommand
from .utils import B642B,B2B64


@dataclass
class CommandGet:
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
class CommandSet:
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
class CommandStartLogGetKpi:
    itemid: int
    index: int

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "index": self.index
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.index
        ]


@dataclass
class CommandStartDbmExportRow:
    itemid: int
    handle: int
    key: str
    index: int

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "handle": self.handle,
            "key": self.key,
            "index": self.index
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.handle,
            self.key,
            self.index
        ]


@dataclass
class CommandStartDbmCreateTable:
    itemid: int
    table: int
    nbrows: str
    rowsize: int

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "table": self.table,
            "nbrows": self.nbrows,
            "rowsize": self.rowsize
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.table,
            self.nbrows,
            self.rowsize
        ]
    
@dataclass
class CommandStartDbmImportRow:
    itemid: int
    table: int
    key: str
    data: bytes

    def __init__(self, itemid, table, key, data) -> None:
        self.itemid = itemid
        self.table = table
        self.key = key
        if(type(data) == str):
            data = B642B(data)
        self.data = bytearray(data)

    def to_dict(self) -> str:
        return {
            "itemid": self.itemid,
            "table": self.table,
            "key": self.key,
            "data": B2B64(self.data),
        }

    def to_array(self) -> list:
        return [
            self.itemid,
            self.table,
            self.key,
            self.data,
        ]


OP_TO_COMMAND_TYPES = {
    MessageModule.LOG.value: {
        CommandOperationID.CMD_GET.value : CommandGet,            
        CommandOperationID.CMD_START.value : {
            LogCommand.LOG_GET_KPI.value: CommandStartLogGetKpi
        }
    },

    MessageModule.DBM.value: {
        CommandOperationID.CMD_GET.value : CommandGet,            
        CommandOperationID.CMD_START.value : {
            DBMCommand.DBM_EXPORT_ROW.value: CommandStartDbmExportRow, 
            DBMCommand.DBM_CREATE_TABLE.value: CommandStartDbmCreateTable,
            DBMCommand.DBM_IMPORT_ROW.value: CommandStartDbmImportRow
        }
    },

    MessageModule.RUN.value: {
        CommandOperationID.CMD_GET.value : CommandGet
    },
    
    MessageModule.MAL.value: {
        CommandOperationID.CMD_GET.value : CommandGet
    }
    
}


def get_command_class(mod: int, op_id: int,  raw_data: list):
    if not mod in OP_TO_COMMAND_TYPES:
        return None

    if not op_id in OP_TO_COMMAND_TYPES[mod]:
        return None

    if op_id in (CommandOperationID.CMD_SET.value, CommandOperationID.CMD_START.value):
        if isinstance(raw_data,list):
            return OP_TO_COMMAND_TYPES[mod][op_id][raw_data[0]]
        else:
            return OP_TO_COMMAND_TYPES[mod][op_id].get(raw_data["data"]["itemid"], None)

    return OP_TO_COMMAND_TYPES[mod][op_id]


class CommandMessagePayload(MessagePayload):
    @classmethod
    def from_array(cls, mod: int, operation: int, raw_data: list) -> "MessagePayload":
        command_class = get_command_class(mod,operation,raw_data)
        if command_class is None:
            log(f"Operation {operation} unknown", logger_level="ERROR")
            return

        payload = cls()
        payload.command = command_class(*raw_data)

        return payload

    @classmethod
    def from_json(cls, mod: int, operation: int, raw_data: list) -> "MessagePayload":
        command_class = get_command_class(mod,operation,raw_data)
        if command_class is None:
            log(f"Operation {operation} unknown", logger_level="ERROR")
            return
            
        payload = cls()
        payload.command = command_class(**raw_data["data"])

        return payload

    def to_dict(self) -> dict:
        return {
            "data": self.command.to_dict()
        }
