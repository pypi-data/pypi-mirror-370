from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestWorkModeGet(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_ReaderWorkModeGet.value
        self.workMode = None
        self.rs485BaudRate = None
        self.rs485DataBit = None
        self.rs485ParityBit = None
        self.rs485StopBit = None
        self.rs232BaudRate = None

    def bytesToClass(self):
        pass

    def pack(self):
        pass

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.workMode = buffer.readInt()
            self.rs485BaudRate = buffer.readInt()
            self.rs485DataBit = buffer.readInt()
            self.rs485ParityBit = buffer.readInt()
            self.rs485StopBit = buffer.readInt()
            self.rs232BaudRate = buffer.readInt()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.workMode, self.rs485BaudRate, self.rs485DataBit, self.rs485ParityBit, self.rs485StopBit,
                    self.rs232BaudRate))
