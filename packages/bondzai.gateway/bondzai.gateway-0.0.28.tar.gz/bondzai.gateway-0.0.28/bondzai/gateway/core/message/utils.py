import base64
import json
from typing import Any
import struct


def msg_serialize(o: Any) -> str:
    return json.dumps(o)


def msg_deserialize(o: str) -> Any:
    return json.loads(o)


def B2B64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def B642B(data: str) -> bytes:
    return base64.b64decode(data)


def unpack_buffer_to_list(buffer, is_little, data_len, pack_unit_format) -> list[Any]:
    buffer = bytearray(buffer)
    buffer_len = len(buffer)
    nb_items = int(buffer_len / data_len)
    struct_format = "".join([pack_unit_format for _ in range(0, nb_items)])
    if buffer_len != nb_items*data_len: # should not happened
        buffer_len = nb_items*data_len
        buffer = buffer[:buffer_len]
    return list(struct.unpack(f"{'<' if is_little else'>'}{struct_format}", buffer))


def pack_list_to_buffer(buffer: list[Any], is_little: bool, pack_unit_format: str) -> bytes:
    struct_format = "".join([pack_unit_format for _ in range(0, len(buffer))])
    return struct.pack(f"{'<' if is_little else' >'}{struct_format}", *buffer)


def get_step_uint32(**kwargs): # copy of generate_id in Dexim
    step_as_uint32 = int(b"00000000000000000000000000000000", 2) 
    
    #Reserved [4 bits]
    bits_to_shift = 4
    
    #Output [4 bits]
    output = kwargs.get("output", 0) 
    if output > (2**4-1) or output < 0:
        raise Exception("Invalid output")
    step_as_uint32 = step_as_uint32 | (output<<bits_to_shift)
    bits_to_shift +=4
    
    #Record mode (BACKGROUND/SUBJECT) [4 bits]
    record_mode = kwargs.get("record_mode", 0)
    if record_mode > (2**4-1) or record_mode < 0:
        raise Exception("Invalid record_mode")
    step_as_uint32 = step_as_uint32 | (record_mode<<bits_to_shift)
    bits_to_shift +=4

    #AI mode (ENROLL/INFER) [4 bits]
    ai_mode = kwargs.get("ai_mode", 0)
    if ai_mode > (2**4-1) or ai_mode < 0:
        raise Exception("Invalid ai_mode")
    step_as_uint32 = step_as_uint32 | (ai_mode<<bits_to_shift)
    bits_to_shift +=4
    
    #"Process" (DATA-TRANSFORM, CORRECTION, TRAIN…) [8 bits]
    process_id = kwargs.get("process_id", 0)
    if process_id > (2**8-1) or process_id < 0:
        raise Exception("Invalid process_id")
    step_as_uint32 = step_as_uint32 | (process_id<<bits_to_shift)
    bits_to_shift +=8

    #Source [7 bits]
    source_id = kwargs.get("source_id", -1)
    if source_id > (2**7-1) or source_id < 0:
        raise Exception("Invalid source_id")
    step_as_uint32 = step_as_uint32 | (source_id<<bits_to_shift)
    
    return step_as_uint32


def get_step_struct(id_as_uint32):
    standard_bit = id_as_uint32 >> 31
    if standard_bit != 0 :
        result = {
            "source_id":0,
            "process_id":0,
            "ai_mode":0,
            "record_mode":0,
            "output":0
        }
        return result
    #Reserved [4 bits]
    bits_to_shift = 4
    
    #Output [4 bits] 
    mask = 2**4-1
    mask = mask<<bits_to_shift
    output = (id_as_uint32 & mask)>> bits_to_shift
    bits_to_shift +=4
    
    #Record mode (BACKGROUND/SUBJECT) [4 bits]
    mask = 2**4-1
    mask = mask<<bits_to_shift
    record_mode = (id_as_uint32 & mask)>> bits_to_shift
    bits_to_shift +=4

    #AI mode (ENROLL/INFER) [4 bits]
    mask = 2**4-1
    mask = mask<<bits_to_shift
    ai_mode = (id_as_uint32 & mask)>> bits_to_shift
    bits_to_shift +=4
    
    #"Process" (DATA-TRANSFORM, CORRECTION, TRAIN…) [8 bits]
    mask = 2**8-1
    mask = mask<<bits_to_shift
    process_id = (id_as_uint32 & mask)>> bits_to_shift
    bits_to_shift +=8

    #Source [7 bits]
    mask = 2**7-1
    mask = mask<<bits_to_shift
    source_id = (id_as_uint32 & mask)>> bits_to_shift
    bits_to_shift +=7

    
    result = {
        "source_id":source_id,
        "process_id":process_id,
        "ai_mode":ai_mode,
        "record_mode":record_mode,
        "output":output
    }

    return result