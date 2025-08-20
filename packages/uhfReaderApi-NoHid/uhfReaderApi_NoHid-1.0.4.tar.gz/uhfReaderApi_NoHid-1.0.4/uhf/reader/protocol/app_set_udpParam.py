from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetUdpParam(Message):

    def __init__(self, onOrOff: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetUdpParam.value
        self.onOrOff = onOrOff
        self.ip = kwargs.get("ip", None)
        self.port = kwargs.get("port", None)
        self.period = kwargs.get("period", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.onOrOff)
        if self.onOrOff == 1:
            if self.ip is not None:
                buffer.putInt(0x01)
                splitIp = self.ip.split('.')
                for ips in splitIp:
                    buffer.putInt(int(ips))

            if self.port is not None:
                buffer.putInt(0x02)
                buffer.putShort(self.port)

            if self.period is not None:
                buffer.putInt(0x03)
                buffer.putShort(self.period)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Fail"}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
