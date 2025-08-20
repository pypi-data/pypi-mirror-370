from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseGetCapabilities(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_GetCapabilities.value
        self.minPower = None
        self.maxPower = None
        self.antennaCount = None
        self.frequencyArray = []
        self.protocolArray = []

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.minPower = buffer.readInt()
            self.maxPower = buffer.readInt()
            self.antennaCount = buffer.readInt()
            freLen = buffer.readShort()
            if freLen:
                self.frequencyArray = [buffer.readInt() for i in range(freLen)]
            proLen = buffer.readShort()
            if proLen:
                self.protocolArray = [buffer.readInt() for i in range(proLen)]
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.minPower, self.maxPower, self.antennaCount, self.frequencyArray, self.protocolArray))
