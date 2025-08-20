from uhf.reader.protocol import *
from uhf.reader.utils import *


class LogGpiStart(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppLogMid_gpi.value
        self.gpiPort = None
        self.gpiPortLevel = None
        self.systemTime = None
        self.readerSerialNumber = None
        self.readerName = None

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.gpiPort = buffer.readInt()
            self.gpiPortLevel = buffer.readInt()
            second = buffer.readLong()
            mic = divmod(buffer.readLong(), 1000000)
            self.systemTime = secondFormat(second + mic[0])

    def __str__(self) -> str:
        return str((self.gpiPort, self.gpiPortLevel, self.systemTime))
