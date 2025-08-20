from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetFreqRange(Message):

    def __init__(self, freqRangeIndex: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetFreqRange.value
        self.freqRangeIndex = freqRangeIndex

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.freqRangeIndex)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Frequency parameter reader is not supported.",
                      2: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
