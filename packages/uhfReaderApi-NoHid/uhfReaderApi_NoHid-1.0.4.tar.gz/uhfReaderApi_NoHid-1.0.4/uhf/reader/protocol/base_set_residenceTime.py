from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetResidenceTime(Message):

    def __init__(self, onOff: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetResidenceTime.value
        self.antLingeringTime = kwargs.get("antLingeringTime", None)
        self.freLingeringTime = kwargs.get("freLingeringTime", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.antLingeringTime is not None:
            buffer.putInt(0x01)
            buffer.putShort(self.antLingeringTime)
        if self.freLingeringTime is not None:
            buffer.putInt(0x02)
            buffer.putShort(self.freLingeringTime)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Parameter error.",
                      2: "Other error.", 3: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
