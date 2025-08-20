from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetReaderInfo(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetReaderInfo.value
        self.readerSerialNumber = ""
        self.powerOnTime = ""
        self.baseCompileTime = ""
        self.appVersions = ""
        self.systemVersions = ""
        self.appCompileTime = ""

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            snLen = buffer.readShort()
            sn = buffer.readBytes(snLen * 8)
            if sn:
                self.readerSerialNumber = listToAscii(sn)
            self.powerOnTime = secondToDhms(buffer.readLong())
            btLen = buffer.readShort()
            bt = buffer.readBytes(btLen * 8)
            if bt:
                self.baseCompileTime = listToAscii(bt)
            while buffer.pos / 8 < len(self.cData):
                pid = buffer.readInt()
                if pid == 1:
                    self.appVersions = str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(
                        buffer.readInt()) + "." + str(buffer.readInt())
                elif pid == 2:
                    svLen = buffer.readShort()
                    sv = buffer.readBytes(svLen * 8)
                    if sv:
                        self.systemVersions = listToAscii(sv)
                elif pid == 3:
                    atLen = buffer.readShort()
                    at = buffer.readBytes(atLen * 8)
                    if at:
                        self.appCompileTime = listToAscii(at)
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.readerSerialNumber, self.powerOnTime, self.baseCompileTime.strip(b'\x00'.decode()),
                    self.appVersions, self.systemVersions, self.appCompileTime))
        # return "{0},{1},{2},{3},{4},{5}".format(self.readerSerialNumber, self.powerOnTime, self.baseCompileTime,
        #                                     self.appVersions, self.systemVersions, self.appCompileTime)
