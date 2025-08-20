from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseGetResidenceTime(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_GetResidenceTime.value
        self.antLingeringTime = None
        self.freLingeringTime = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            while buffer.pos / 8 < len(self.cData):
                pid = buffer.readInt()
                if pid == 1:
                    self.antLingeringTime = buffer.readShort()
                if pid == 2:
                    self.freLingeringTime = buffer.readShort()

            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.antLingeringTime, self.freLingeringTime))
