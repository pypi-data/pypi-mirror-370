from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestGetRssiCalibration(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_RssiCalibrationGet.value
        self.rssiBaseValue = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.rssiBaseValue = buffer.readSigned(16)
            self.rtCode = 0

    def __str__(self) -> str:
        return str(self.rssiBaseValue)
