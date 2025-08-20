from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetReaderTime(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetReaderTime.value
        self.seconds = None
        self.formatTime = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            second = buffer.readLong()
            mic = divmod(buffer.readLong(), 1000000)
            self.seconds = second + mic[0]
            self.formatTime = secondFormat(self.seconds)
            self.rtCode = 0

    def __str__(self) -> str:
        return str(self.seconds)
