from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetGbBaseBand(Message):

    def __init__(self, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetGbBaseBand.value
        self.speed_tc = kwargs.get("speed_tc", None)
        self.speed_trext = kwargs.get("speed_trext", None)
        self.speed_k = kwargs.get("speed_k", None)
        self.speed_miller = kwargs.get("speed_miller", None)
        self.cin = kwargs.get("cin", 4)
        self.ccn = kwargs.get("ccn", 3)
        self.session = kwargs.get("session", None)
        self.inventoryFlag = kwargs.get("inventoryFlag", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.speed_tc is not None and self.speed_trext is not None and self.speed_k is not None and self.speed_miller is not None:
            buffer.putInt(0x01)
            buffer.putString(1, self.speed_tc)
            buffer.putString(1, self.speed_trext)
            buffer.putString(4, self.speed_k)
            buffer.putString(2, self.speed_miller)
        if self.cin is not None and self.ccn is not None:
            buffer.putInt(0x02)
            buffer.putString(4, self.cin)
            buffer.putString(4, self.ccn)
        if self.session is not None:
            buffer.putInt(0x03)
            buffer.putInt(self.session)
        if self.inventoryFlag is not None:
            buffer.putInt(0x04)
            buffer.putInt(self.inventoryFlag)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Parameter reader is not supported.",
                      2: "Q value parameter error.", 3: "Session parameter error.", 4: "Inventory parameter error.",
                      5: "Other error.", 6: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
