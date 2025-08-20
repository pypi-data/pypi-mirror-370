from uhf.reader.protocol import *
from uhf.reader.utils import *


class LogAppAllGpiState(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppLogMid_allGpiState.value
        self.gpiPortLevel = None
        self.readerSerialNumber = None
        self.readerName = None

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.gpiPortLevel = buffer.readLong()

    def toBinaryString(self):
        return format(self.gpiPortLevel, "b").zfill(32)

    def __str__(self) -> str:
        return str(self.gpiPortLevel)
