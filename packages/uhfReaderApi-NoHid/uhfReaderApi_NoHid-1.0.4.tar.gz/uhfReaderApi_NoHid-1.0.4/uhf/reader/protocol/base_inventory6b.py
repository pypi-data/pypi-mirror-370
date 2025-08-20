from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseInventory6b(Message):

    def __init__(self, antennaEnable: int, inventoryMode: int, area: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_Inventory6b.value
        self.antennaEnable = antennaEnable
        self.inventoryMode = inventoryMode
        self.area = area
        self.readUserData = kwargs.get("readUserData", None)  # type:Param6bReadUserData
        self.hexMatchTid = kwargs.get("hexMatchTid", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putInt(self.inventoryMode)
        buffer.putInt(self.area)
        if self.readUserData is not None:
            buffer.putInt(0x01)
            buffer.putBytes(self.readUserData.toBytes())
        if self.hexMatchTid is not None:
            buffer.putInt(0x02)
            buffer.putBytes(hexToBytes(self.hexMatchTid))

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter error.",
                      2: "Read parameter error.", 3: "UserData parameter error.", 4: "Other error.", }
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
