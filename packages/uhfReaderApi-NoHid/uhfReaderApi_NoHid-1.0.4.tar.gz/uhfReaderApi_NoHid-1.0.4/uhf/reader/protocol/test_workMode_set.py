from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestWorkModeSet(Message):

    def __init__(self, workMode: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_ReaderWorkModeSet.value
        self.workMode = workMode
        self.rs485BaudRate = kwargs.get("rs485BaudRate", None)
        self.rs485DataBit = kwargs.get("rs485DataBit", None)
        self.rs485ParityBit = kwargs.get("rs485ParityBit", None)
        self.rs485StopBit = kwargs.get("rs485StopBit", None)
        self.rs232BaudRate = kwargs.get("rs232BaudRate", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.workMode)
        if self.rs485BaudRate and self.rs485DataBit and self.rs485ParityBit and self.rs485StopBit:
            buffer.putInt(0x01)
            buffer.putInt(self.rs485BaudRate)
            buffer.putInt(self.rs485DataBit)
            buffer.putInt(self.rs485ParityBit)
            buffer.putInt(self.rs485StopBit)
        if self.rs232BaudRate:
            buffer.putInt(0x02)
            buffer.putInt(self.rs232BaudRate)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success.", 1: "Other error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
