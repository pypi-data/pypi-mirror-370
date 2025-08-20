from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetSerialParam(Message):

    def __init__(self, baudRateIndex: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetSerialParam.value
        self.baudRateIndex = baudRateIndex

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.baudRateIndex)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Failed,This baud rate is not supported ."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
