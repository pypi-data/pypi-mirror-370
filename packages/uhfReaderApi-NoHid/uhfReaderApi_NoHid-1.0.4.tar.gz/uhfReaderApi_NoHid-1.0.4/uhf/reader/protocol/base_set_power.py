from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetPower(Message):

    def __init__(self, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetPower.value
        self.dicPower = kwargs
        self.powerDownSave = kwargs.get("powerDownSave", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.dicPower:
            for key, value in self.dicPower.items():
                if str(key).isdigit():
                    buffer.putInt(int(key))
                    buffer.putInt(value)

        if self.powerDownSave is not None:
            buffer.putInt(0xFF)
            buffer.putInt(self.powerDownSave)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter reader is not supported.",
                      2: "Power parameter reader is not supported.", 3: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)

