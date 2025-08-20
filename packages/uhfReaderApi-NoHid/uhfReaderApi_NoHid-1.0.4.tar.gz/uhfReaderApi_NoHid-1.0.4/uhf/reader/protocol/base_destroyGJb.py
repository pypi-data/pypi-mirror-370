from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseDestroyGJb(Message):

    def __init__(self, antennaEnable: int, hexPassword: str, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_DestroyGJb.value
        self.antennaEnable = antennaEnable
        self.filter = kwargs.get("filter", None)  # type:ParamEpcFilter
        self.hexPassword = kwargs.get("hexPassword", None)
        self.safeMark = kwargs.get("safeMark", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        if self.filter is not None:
            buffer.putInt(0x01)
            filter_bytes = self.filter.toBytes()
            buffer.putShort(len(filter_bytes))
            buffer.putBytes(filter_bytes)
        if self.hexPassword is not None:
            buffer.putInt(0x02)
            buffer.putBytes(hexToBytes(self.hexPassword))
        if self.safeMark is not None:
            buffer.putInt(0x03)
            buffer.putInt(self.safeMark)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter error.",
                      2: "Filter parameter error.", 3: "CRC check error.",
                      4: "Underpower error.", 5: "Access password error.", 6: "Permission denied.",
                      7: "Identify failure.", 8: "Other error.", 9: "Label is missing.", 10: "Command error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
