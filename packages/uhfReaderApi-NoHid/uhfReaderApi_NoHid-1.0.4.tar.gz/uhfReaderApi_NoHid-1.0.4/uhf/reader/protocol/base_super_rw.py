from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSuperRW(Message):

    def __init__(self, antennaEnable: int, instructType: int, start: int, extraCode: str, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SuperRW.value
        self.antennaEnable = antennaEnable
        self.instructType = instructType
        self.start = start
        self.extraCode = extraCode
        self.hexData = kwargs.get("hexData", None)
        self.readData = None

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putInt(self.instructType)
        buffer.putShort(self.start)
        buffer.putBytes(hexToBytes(self.extraCode))
        if self.hexData:
            buffer.putInt(0x01)
            to_bytes = hexToBytes(self.hexData)
            buffer.putBytes(to_bytes)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter error.", 3: "Other error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
            if len(self.cData) > 1:
                readBuffer = DynamicBuffer("0x" + bytesToHex(self.cData))
                readBuffer.pos = 8
                if readBuffer.readInt() == 1:
                    self.readData = bytesToHex(readBuffer.readBytes(16))
