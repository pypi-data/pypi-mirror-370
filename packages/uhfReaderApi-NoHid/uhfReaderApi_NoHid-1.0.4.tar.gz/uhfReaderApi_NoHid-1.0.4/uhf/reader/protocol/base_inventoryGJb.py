from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseInventoryGJb(Message):

    def __init__(self, antennaEnable: int, inventoryMode: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_InventoryGJb.value
        self.antennaEnable = antennaEnable
        self.inventoryMode = inventoryMode
        self.filter = kwargs.get("filter", None)  # type:ParamEpcFilter
        self.readTid = kwargs.get("readTid", None)  # type:ParamEpcReadTid
        self.readUserData = kwargs.get("readUserData", None)  # type:ParamEpcReadUserData
        self.hexPassword = kwargs.get("hexPassword", None)
        self.safeMark = kwargs.get("safeMark", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putInt(self.inventoryMode)
        if self.filter is not None:
            buffer.putInt(0x01)
            filter_bytes = self.filter.toBytes()
            buffer.putShort(len(filter_bytes))
            buffer.putBytes(filter_bytes)
        if self.readTid is not None:
            buffer.putInt(0x02)
            buffer.putBytes(self.readTid.toBytes())
        if self.readUserData is not None:
            buffer.putInt(0x03)
            buffer.putBytes(self.readUserData.toBytes())
        if self.hexPassword is not None:
            buffer.putInt(0x05)
            buffer.putBytes(hexToBytes(self.hexPassword))
        if self.safeMark is not None:
            buffer.putInt(0x06)
            buffer.putInt(self.safeMark)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter error.",
                      2: "Filter parameter error.", 3: "TID parameter error.", 4: "User parameter error.",
                      5: "Other error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
