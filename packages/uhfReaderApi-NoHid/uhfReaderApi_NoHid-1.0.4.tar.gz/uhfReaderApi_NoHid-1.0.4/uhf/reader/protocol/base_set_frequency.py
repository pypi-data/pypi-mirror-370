from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetFrequency(Message):

    def __init__(self, automatically: int, *args, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetFrequency.value
        self.automatically = automatically
        self.listFreqCursor = args
        self.powerDownSave = kwargs.get("powerDownSave", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.automatically)
        if self.automatically == 0 and self.listFreqCursor:
            buffer.putInt(0x01)
            buffer.putShort(len(self.listFreqCursor))
            for value in self.listFreqCursor:
                buffer.putInt(value)
        if self.powerDownSave is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.powerDownSave)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "The channel number is not in the current frequency band.",
                      2: "Invalid frequency points.", 3: "Other error.", 4: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
