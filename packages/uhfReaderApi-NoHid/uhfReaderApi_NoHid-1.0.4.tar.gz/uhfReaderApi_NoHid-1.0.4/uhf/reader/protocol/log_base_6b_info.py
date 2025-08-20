from uhf.reader.protocol.message import Message
from uhf.reader.protocol.enumg import EnumG
from uhf.reader.utils.byteBuffer import DynamicBuffer
from uhf.reader.utils.HexUtils import *


class LogBase6bInfo(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseLogMid_6b.value
        self.readerName = None
        self.tid = None
        self.bTid = None
        self.antId = None
        self.rssi = None
        self.result = 0
        self.userData = None
        self.bUser = None
        self.readerSerialNumber = None

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.bTid = buffer.readBytes(8 * 8)
            if self.bTid:
                self.tid = bytesToHex(self.bTid)
            self.antId = buffer.readInt()
            while buffer.pos / 8 < len(self.cData):
                pid = buffer.readInt()
                if pid == 1:
                    self.rssi = buffer.readInt()
                elif pid == 2:
                    self.result = buffer.readInt()
                elif pid == 3:
                    userLen = buffer.readShort()
                    self.bUser = buffer.readBytes(userLen * 8)
                    if self.bUser:
                        self.userData = bytesToHex(self.bUser)

