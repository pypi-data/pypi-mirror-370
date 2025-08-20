from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetWifiHotspot(Message):

    def __init__(self, hotspotName: str, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetWifiHotspot.value
        self.hotspotName = hotspotName
        self.password = kwargs.get("password", None)
        self.certificationType = kwargs.get("certificationType", 1)
        self.encryptionAlgorithm = kwargs.get("encryptionAlgorithm", 0)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.hotspotName:
            buffer.putShort(len(self.hotspotName))
            buffer.putBytes(self.hotspotName.encode())
        if self.password is not None:
            buffer.putInt(0x01)
            buffer.putShort(len(self.password))
            buffer.putBytes(self.password.encode())

        if self.certificationType is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.certificationType)

        if self.encryptionAlgorithm is not None:
            buffer.putInt(0x03)
            buffer.putInt(self.encryptionAlgorithm)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Set Fail."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
