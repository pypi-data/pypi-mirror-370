from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseInventoryHybrid(Message):

    def __init__(self, antennaEnable: int, read6b: int, readGb: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_Hybrid.value
        self.antennaEnable = antennaEnable
        self.read6b = read6b
        self.readGb = readGb

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putInt(self.read6b)
        buffer.putInt(self.readGb)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Other error.", }
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
