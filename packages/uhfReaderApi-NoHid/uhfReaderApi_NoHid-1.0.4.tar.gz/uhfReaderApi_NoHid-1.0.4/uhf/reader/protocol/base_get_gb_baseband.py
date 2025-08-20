from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseGetGbBaseBand(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_GetGbBaseBand.value
        self.speed_tc = None
        self.speed_trext = None
        self.speed_k = None
        self.speed_miller = None
        self.cin = None
        self.ccn = None
        self.session = None
        self.inventoryFlag = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.speed_tc = buffer.readBitLen(1)
            self.speed_trext = buffer.readBitLen(1)
            self.speed_k = buffer.readBitLen(4)
            self.speed_miller = buffer.readBitLen(2)
            self.cin = buffer.readBitLen(4)
            self.ccn = buffer.readBitLen(4)
            self.session = buffer.readInt()
            self.inventoryFlag = buffer.readInt()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.speed_tc, self.speed_trext, self.speed_k, self.speed_miller, self.cin, self.ccn, self.session,
                    self.inventoryFlag))
