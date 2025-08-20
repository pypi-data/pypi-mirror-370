from uhf.reader.protocol.message import Message
from uhf.reader.protocol.enumg import EnumG
from uhf.reader.utils.byteBuffer import DynamicBuffer
from uhf.reader.utils.HexUtils import *


class LogBaseGbInfo(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseLogMid_Gb.value
        self.readerName = None
        self.epc = None
        self.bEpc = None
        self.tid = None
        self.bTid = None
        self.pc = None
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
            epcLength = buffer.readShort()
            self.bEpc = buffer.readBytes(epcLength * 8)
            if self.bEpc:
                self.epc = bytesToHex(self.bEpc)
            self.pc = buffer.readShort()
            self.antId = buffer.readInt()
            while buffer.pos / 8 < len(self.cData):
                pid = buffer.readInt()
                if pid == 1:
                    self.rssi = buffer.readInt()
                elif pid == 2:
                    self.result = buffer.readInt()
                elif pid == 3:
                    tidLen = buffer.readShort()
                    self.bTid = buffer.readBytes(tidLen * 8)
                    if self.bTid:
                        self.tid = bytesToHex(self.bTid)
                elif pid == 4:
                    userLen = buffer.readShort()
                    self.bUser = buffer.readBytes(userLen * 8)
                    if self.bUser:
                        self.userData = bytesToHex(self.bUser)
