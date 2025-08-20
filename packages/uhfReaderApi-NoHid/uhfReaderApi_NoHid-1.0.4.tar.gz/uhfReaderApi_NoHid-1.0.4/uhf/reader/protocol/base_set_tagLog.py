from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetTagLog(Message):

    def __init__(self, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetTagLog.value
        self.repeatedTime = kwargs.get("repeatedTime", None)
        self.rssiTV = kwargs.get("rssiTV", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.repeatedTime is not None:
            buffer.putInt(0x01)
            buffer.putShort(self.repeatedTime)
        if self.rssiTV is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.rssiTV)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Parameter reader is not supported.",
                      2: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
