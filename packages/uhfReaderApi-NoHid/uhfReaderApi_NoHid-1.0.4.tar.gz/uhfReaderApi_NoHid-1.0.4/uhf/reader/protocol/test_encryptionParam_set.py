from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestEncryptionParamSet(Message):

    def __init__(self, encryptedPassword: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_EpcEncryptionSet.value
        self.encryptedPassword = encryptedPassword

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putShort(self.encryptedPassword)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success.", 1: "Save failed."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
