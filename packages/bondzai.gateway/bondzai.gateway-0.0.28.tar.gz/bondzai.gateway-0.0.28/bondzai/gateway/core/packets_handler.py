# Filename: packets_handler.py
# the class that handles packets coming from the device

from .message.base import Handshake, Message
from .device import TAG_AGENT_ID

class PacketsHandler(object):
    """
    This class is here to handle the packets (before handling the message)
    It allows to check packet header and to collatione the packet if message is not
    complete
    """
    def __init__(self):
        self._buffer = bytearray([])
        self._pid = -1

    def handle_handshake_message(self, header, payload ):        
        """
        This function is here to handle the applicative messages
        """
        agent_id = None
        pid = header[1]

        #look for AGENT_ID tag
        i = 0
        while i<len(payload):
            tag = payload[i]
            length = payload[i+1]
            value = payload[i+2:i+2+length]
            i += 2+length

            if tag == TAG_AGENT_ID:
                agent_id = value
                break
        
        if not agent_id:
            raise RuntimeError("No agent id in handshake message")
        
        return Handshake(pid,agent_id)



    def handle_app_message(self, header, payload ):        
        """
        This function is here to handle the applicative messages
        """

        islast = (header[0]&1)
        pid = header[1]

        self._pid = pid
        self._buffer += payload

        if not islast:
            return None

        self._pid = -1
        message = self._buffer
        self._buffer = bytearray([])

        return Message.from_msgpack(message)

         
    def push(self, packet):
        if not packet:
            raise RuntimeError("Connection error, empty packet")

        header = packet[:2]
        payload = packet[2:]

        pid = header[1]
        #check version
        version = ((header[0]>>4)&0xF)
        issecure = (header[0]&8)
        msgtyp = ((header[0]&6)>>1)

        if (version != 1):
            raise RuntimeError("Bad protocol version %d, only supporting version 1" % version)

        if (self._pid != -1 and pid != self._pid):
            raise RuntimeError("This version of gateway doesn't support interleaved messages")

        if issecure:
            raise RuntimeError("This version of gateway doesn't support secure messages")

        if (msgtyp == 0):
            return self.handle_handshake_message(header, payload)


        if (msgtyp == 1):
            return self.handle_app_message(header, payload)
       

        raise RuntimeError("Bad msg type %d, only supporting application message (1)" % msgtyp)
