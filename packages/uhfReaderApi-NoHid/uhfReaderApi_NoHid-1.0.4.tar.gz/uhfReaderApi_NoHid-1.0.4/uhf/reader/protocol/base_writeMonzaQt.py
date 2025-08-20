from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseWriteMonzaQt(Message):

    def __init__(self, antennaEnable: int, operationType: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_MonzaQT.value
        self.antennaEnable = antennaEnable
        self.operationType = operationType
        self.filter = kwargs.get("filter", None)  # type:ParamEpcFilter
        self.hexPassword = kwargs.get("hexPassword", None)
        self.responseDistance = kwargs.get("responseDistance", None)
        # self.qtParam = kwargs.get("qtParam", None)
        self.pattern = kwargs.get("pattern", None)
        self.qtParamResult = None

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putInt(self.operationType)
        if self.filter is not None:
            buffer.putInt(0x01)
            filter_bytes = self.filter.toBytes()
            buffer.putShort(len(filter_bytes))
            buffer.putBytes(filter_bytes)
        if self.hexPassword is not None:
            buffer.putInt(0x02)
            buffer.putBytes(hexToBytes(self.hexPassword))
        if self.responseDistance is not None and self.pattern is not None:
            buffer.putInt(0x03)
            buffer.putString(1, self.responseDistance)
            buffer.putString(1, self.pattern)
            buffer.putString(6, 0)
            buffer.putInt(0)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter error.",
                      2: "Filter parameter error.", 3: "Qt parameter error.", 4: "CRC check error.",
                      5: "Underpower error.", 6: "Access password error.", 7: "Other error.", 8: "Label is missing.",
                      9: "Command error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
            if len(self.cData) > 1:
                queryBuffer = DynamicBuffer("0x" + bytesToHex(self.cData))
                queryBuffer.pos = 8
                if queryBuffer.readInt() == 1:
                    self.qtParamResult = queryBuffer.readShort()
