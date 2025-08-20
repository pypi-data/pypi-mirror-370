from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetWifiConnectStatus(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetWifiConnectStatus.value
        self.hotspotName = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            hnLen = buffer.readShort()
            if hnLen:
                self.hotspotName = listToAscii(buffer.readBytes(hnLen * 8))
            self.rtCode = 0

    def __str__(self) -> str:
        return str(self.hotspotName)
