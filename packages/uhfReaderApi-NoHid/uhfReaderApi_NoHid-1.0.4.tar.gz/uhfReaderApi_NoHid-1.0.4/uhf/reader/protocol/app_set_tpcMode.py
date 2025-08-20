from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetTcpMode(Message):

    def __init__(self, tcpMode, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetTcpMode.value
        self.tcpMode = tcpMode
        self.serverPort = kwargs.get("serverPort", None)
        self.clientIp = kwargs.get("clientIp", None)
        self.clientPort = kwargs.get("clientPort", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.tcpMode)
        if self.tcpMode == 0:  # 服务器模式
            if self.serverPort is not None:
                buffer.putInt(0x01)
                buffer.putShort(self.serverPort)
        else:  # 客户端模式
            if self.clientIp is not None:
                buffer.putInt(0x02)
                splitIp = self.clientIp.split('.')
                for ips in splitIp:
                    buffer.putInt(int(ips))
            if self.clientPort is not None:
                buffer.putInt(0x03)
                buffer.putShort(self.clientPort)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Server IP parameter error ."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
