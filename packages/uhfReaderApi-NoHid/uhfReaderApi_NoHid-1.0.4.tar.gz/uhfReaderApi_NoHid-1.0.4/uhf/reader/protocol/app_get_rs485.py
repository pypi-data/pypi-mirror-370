from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetRs485(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetRs485.value
        self.address = None
        self.baudRate = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.address = buffer.readInt()
            self.baudRate = buffer.readInt()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.address, self.baudRate))
