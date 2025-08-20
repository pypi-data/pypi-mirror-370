from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseDestroyEpc(Message):

    def __init__(self, antennaEnable: int, hexPassword: str, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_DestroyEpc.value
        self.antennaEnable = antennaEnable
        self.hexPassword = hexPassword
        self.filter = kwargs.get("filter", None)  # type:ParamEpcFilter

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putBytes(hexToBytes(self.hexPassword))
        if self.filter is not None:
            buffer.putInt(0x01)
            filter_bytes = self.filter.toBytes()
            buffer.putShort(len(filter_bytes))
            buffer.putBytes(filter_bytes)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter error.",
                      2: "Filter parameter error.", 3: "CRC check error.",
                      4: "Underpower error.", 5: "Access password error.", 6: "Other error.", 7: "Label is missing.",
                      8: "Command error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
