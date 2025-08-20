from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetReaderTime(Message):

    def __init__(self, seconds: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetReaderTime.value
        self.seconds = seconds

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        # second, microsecond = divmod(self.seconds, 1000)
        buffer.putLong(self.seconds)
        buffer.putLong(0)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "RTC setup failed."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
