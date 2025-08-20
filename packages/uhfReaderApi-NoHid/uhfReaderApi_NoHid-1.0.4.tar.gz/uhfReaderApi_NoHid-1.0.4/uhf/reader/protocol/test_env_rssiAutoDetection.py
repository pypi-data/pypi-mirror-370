from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestEnvRssiAutoDetection(Message):

    def __init__(self, antennaEnable: int, startFrequency: int, endFrequency: int, mode: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_EnvRssiAutoDetection.value
        self.antennaEnable = antennaEnable
        self.startFrequency = startFrequency
        self.endFrequency = endFrequency
        self.mode = mode

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putShort(self.startFrequency)
        buffer.putShort(self.endFrequency)
        buffer.putInt(self.mode)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "FrequencyPoint Param Reader Not Support.", 2: "Port Param Reader Not Support.",
                      3: "Phase-locked loop locking failed", 4: "Other error"}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
