from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestSerialNoSet(Message):

    def __init__(self, readerSerialNumber: str):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_SerialNoSet.value
        self.readerSerialNumber = readerSerialNumber

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.readerSerialNumber is not None:
            buffer.putShort(len(self.readerSerialNumber))
            buffer.putBytes(self.readerSerialNumber.encode())

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success.", 1: "Other error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
