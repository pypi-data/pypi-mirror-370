from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetEthernetIP(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetReaderIP.value
        self.autoIp = None
        self.ip = None
        self.mask = None
        self.gateway = None
        self.dns1 = None
        self.dns2 = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.autoIp = buffer.readInt()
            self.ip = str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(
                buffer.readInt())
            self.mask = str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(
                buffer.readInt())
            self.gateway = str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(
                buffer.readInt()) + "." + str(buffer.readInt())
            self.dns1 = str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(
                buffer.readInt())
            self.dns2 = str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(
                buffer.readInt())
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.autoIp, self.ip, self.mask,
                    self.gateway, self.dns1, self.dns2))
        # return "{0},{1},{2},{3},{4},{5}".format(self.readerSerialNumber, self.powerOnTime, self.baseCompileTime,
        #                                     self.appVersions, self.systemVersions, self.appCompileTime)
