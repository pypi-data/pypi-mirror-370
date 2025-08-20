from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestEncryptionParamGet(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_EpcEncryptionGet.value
        self.encryptedPassword = None

    def bytesToClass(self):
        pass

    def pack(self):
        pass

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.encryptedPassword = buffer.readShort()
            self.rtCode = 0
