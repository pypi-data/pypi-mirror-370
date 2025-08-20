from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppHeartbeat(Message):

    def __init__(self, serialNumber):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.__msgId = EnumG.AppMid_Heartbeat.value
        self.serialNumber = serialNumber

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.serialNumber)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.serialNumber = buffer.readLong()
            self.rtCode = 0
