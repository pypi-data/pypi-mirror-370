import msgpack
import sys, traceback
from enum import Enum
from io import BytesIO

from .utils import B2B64
from .enums import DBMTable
from ..logger import log



class DBM_ATT_VM(Enum):
    DESC                = 0x0
    PREPROC_GRAPH_TRAIN = 0x1
    PREPROC_GRAPH_INFER = 0x2
    PREPROC_GRAPH_OTHER = 0x3
    DEEPLOMATH          = 0x4
    POSTPROC            = 0x5


class DBM_ATT_DAT(Enum):
    META                = 0x0
    DATA                = 0x1


class DbmExportVm(object):
    def __init__(self, raw_data):
        self.attributes = {}

        for att in raw_data:
            if att == DBM_ATT_VM.DESC.value:
                i=0
                self.attributes["desc"] = {}
                self.attributes["desc"]["description"] = raw_data[att][i]
                i+=1
                if len(raw_data[att][i]):
                    self.attributes["desc"]["axis"] = raw_data[att][i]
                    i+=1
                else:
                    self.attributes["desc"]["axis"] = raw_data[att][i+1]
                    i+=2
                if len(raw_data[att][i]):
                    self.attributes["desc"]["split"] = raw_data[att][i]
                    i+=1
                else:
                    self.attributes["desc"]["split"] = raw_data[att][i+1]
                    i+=2
                self.attributes["desc"]["maxsplit"] = raw_data[att][i]
                i+=1
                self.attributes["desc"]["reduction"] = raw_data[att][i]
                i+=1
                self.attributes["desc"]["filter"] = {
                    "max_row": raw_data[att][i],
                    "mode": raw_data[att][i+1],
                    "filters": []
                } 
                i+=2

                for el in raw_data[att][i]:
                    filt =  {
                        "row" : el[0] if len(el[0]) else el[1],
                        "labels": [
                            lbl for lbl in (el[1] if len(el[0]) else el[2]) 
                        ]                        
                    }
                    self.attributes["desc"]["filter"]["filters"].append(filt)            
            elif att in [DBM_ATT_VM.PREPROC_GRAPH_TRAIN.value, DBM_ATT_VM.PREPROC_GRAPH_INFER.value, DBM_ATT_VM.PREPROC_GRAPH_OTHER.value]:
                graph = {
                    "memneed": {
                        "outlen": raw_data[att][0],
                        "templen": raw_data[att][1],
                    },
                    "sizeout": raw_data[att][2],
                }
                
                nodes = []                
                for n in raw_data[att][3]:
                    nodes.append({
                        "op_id": n[0],
                        "memneed": {
                            "outlen": n[1],
                            "templen": n[2]
                        },
                        "mem_policy": n[3],
                        "next": [i for i in n[4]],
                        "param": {
                            "typeid": n[5],
                            "parameters": B2B64(b"".join(n[6]))
                        }
                    })

                    k = "preproc_other"
                    if att == DBM_ATT_VM.PREPROC_GRAPH_TRAIN.value:
                        k = "preproc_train"
                    elif att==DBM_ATT_VM.PREPROC_GRAPH_INFER.value:
                        k = "preproc_infer" 

                    graph["nodes"] = nodes
                    self.attributes[k] = graph
            elif att == DBM_ATT_VM.DEEPLOMATH.value :
                self.attributes["deeplomath"] = {
                    "mode": raw_data[att][0],
                    "rejection": raw_data[att][1],
                    "dim_in": raw_data[att][2],
                    "dim_out": raw_data[att][3],
                    "max_layers": raw_data[att][4]
                }
            elif att == DBM_ATT_VM.POSTPROC.value :
                self.attributes["postproc"] = {
                    "mode": raw_data[att][0],
                    "rejection": raw_data[att][1],
                    "op": raw_data[att][2],
                    "ring_depth": raw_data[att][3],
                    "ring_width": raw_data[att][4],
                    "reserved": raw_data[att][5]
                }

    def to_dict(self):
        return self.attributes


class DbmExportLbl(object):
    pass


class DbmExportDat(object):
    def __init__(self, raw_data):
        self.attributes={}
        for att in raw_data:
            if att == DBM_ATT_DAT.META.value:
                self.attributes["label"] = {
                    "type": raw_data[att][0],
                    "qi": raw_data[att][1]
                } 

                if self.attributes["label"]["type"] == 0:                
                    self.attributes["label"]["labels"] = [{
                        "output_id": l[0],
                        "source_id": l[1],
                        "label": l[2]
                    } for l in raw_data[att][2]]
                else:
                    self.attributes["label"]["values"] = raw_data[att][2]                
            elif att == DBM_ATT_DAT.DATA.value:

                raw_data_l = raw_data[att][0]
                raw_data_bytes = raw_data[att][1]
                self.attributes["record"] = B2B64(b"".join(raw_data_bytes))\

    def to_dict(self):
        return self.attributes


class DbmExportKey(object):
    pass


class DbmExportCtx(object):
    pass


class DbmExportSig(object):
    pass


class DbmExportGen(object):
    pass


DBM_TYPE_TO_CLASS = {
    DBMTable.DBM_VM  : DbmExportVm, 
    DBMTable.DBM_LBL : DbmExportLbl,
    DBMTable.DBM_DAT : DbmExportDat,
    DBMTable.DBM_KEY : DbmExportKey,
    DBMTable.DBM_CTX : DbmExportCtx,
    DBMTable.DBM_SIG : DbmExportSig,
    DBMTable.DBM_GEN : DbmExportGen
}


class DbmProcesser(object):
    @classmethod
    def from_msgpack(cls, data: bytearray) -> "DbmProcesser":
        try:

            stream = BytesIO(data)
            unpacker = msgpack.Unpacker(stream, raw=False, strict_map_key=False)

            table_type = unpacker.unpack()

            nb_attributes = unpacker.read_map_header()
            
            att_map = {}
            for _ in range(nb_attributes):
                k = unpacker.unpack()
                v = unpacker.unpack()
                att_map[k] = v

            return DBM_TYPE_TO_CLASS[DBMTable(table_type)](att_map)
        except Exception as e:
            log(f"Error parsing msgpck in DbmProcesser : {str(e)}", logger_level="ERROR")
            traceback.print_exc(file=sys.stdout)
            return None
