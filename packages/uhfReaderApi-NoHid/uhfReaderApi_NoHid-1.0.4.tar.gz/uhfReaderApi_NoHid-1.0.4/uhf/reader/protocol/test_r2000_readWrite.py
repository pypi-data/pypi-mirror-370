from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestR2000ReadWrite(Message):

    def __init__(self, operationType: int, registerAddress: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_R2000ReadWrite.value
        self.operationType = operationType
        self.registerAddress = registerAddress
        self.writeContent = kwargs.get("writeContent", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.operationType)
        buffer.putShort(self.registerAddress)
        if self.writeContent:
            buffer.putInt(0x01)
            buffer.putShort(self.writeContent)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success.", 1: "Failed."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
            if len(self.cData) > 1:
                dataBuffer = DynamicBuffer("0x" + bytesToHex(self.cData))
                dataBuffer.pos = 8
                if dataBuffer.readInt() == 1:
                    self.writeContent = dataBuffer.readShort()
