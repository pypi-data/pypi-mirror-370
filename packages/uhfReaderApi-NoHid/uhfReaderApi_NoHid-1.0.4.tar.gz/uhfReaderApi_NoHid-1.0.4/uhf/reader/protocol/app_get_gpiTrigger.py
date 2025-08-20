from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetGpiTrigger(Message):

    def __init__(self, gpiPort):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetGpiTrigger.value
        self.gpiPort = gpiPort
        self.triggerStart = None
        self.hexTriggerCommand = None
        self.triggerOver = None
        self.overDelayTime = None
        self.levelUploadSwitch = None

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.gpiPort)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.triggerStart = buffer.readInt()
            cmdLen = buffer.readShort()
            if cmdLen:
                self.hexTriggerCommand = bytesToHex(buffer.readBytes(cmdLen * 8))
            self.triggerOver = buffer.readInt()
            self.overDelayTime = buffer.readShort()
            self.levelUploadSwitch = buffer.readInt()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.gpiPort, self.triggerStart, self.hexTriggerCommand, self.triggerOver, self.overDelayTime,
                    self.levelUploadSwitch))
        # return "{0},{1},{2},{3},{4},{5}".format(self.readerSerialNumber, self.powerOnTime, self.baseCompileTime,
        #                                     self.appVersions, self.systemVersions, self.appCompileTime)
