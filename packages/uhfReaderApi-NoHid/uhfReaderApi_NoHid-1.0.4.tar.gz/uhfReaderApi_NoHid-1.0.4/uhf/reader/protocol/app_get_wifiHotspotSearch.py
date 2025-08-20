from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetWifiHotspotSearch(Message):

    def __init__(self, packetNumber: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetWifiHotspotSearch.value
        self.packetNumber = packetNumber
        self.packetContent = []

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.packetNumber)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.packetNumber = buffer.readLong()
            pnLen = buffer.readShort()
            if pnLen:
                self.packetContent = buffer.readBytes(pnLen * 8)
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.packetNumber, self.packetContent))
