from uhf.reader.protocol.message import Message
from uhf.reader.protocol.enumg import EnumG
from uhf.reader.utils.byteBuffer import DynamicBuffer
from uhf.reader.utils.HexUtils import *


class LogBaseEpcInfo(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseLogMid_Epc.value
        self.readerName = None
        self.epc = None
        self.bEpc = None
        self.pc = None
        self.antId = None
        self.rssi = None
        self.result = 0
        self.tid = None
        self.bTid = None
        self.userData = None
        self.bUser = None
        self.reserved = None
        self.bRes = None
        self.childAntId = None
        self.strUtc = None
        self.frequencyPoint = None
        self.phase = None
        self.epcData = None
        self.bEpcData = None
        self.ctesiusLtu27 = None
        self.ctesiusLtu31 = None
        self.readerSerialNumber = None
        self.replySerialNumber = None
        self.kunYue = None
        self.rssidBm = None
        self.cykeoRule = None

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x"+hex)
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
                elif pid == 5:
                    resLen = buffer.readShort()
                    self.bRes = buffer.readBytes(resLen * 8)
                    if self.bRes:
                        self.reserved = bytesToHex(self.bRes)
                elif pid == 6:
                    self.childAntId = buffer.readInt()
                elif pid == 7:
                    utcSecond = buffer.readLong() * 1000
                    utcMicrosecond = buffer.readLong() / 1000
                    self.strUtc = utcSecond + utcMicrosecond
                    # print(ms)
                elif pid == 8:
                    self.frequencyPoint = buffer.readLong()
                elif pid == 9:
                    self.phase = buffer.readInt()
                elif pid == 10:
                    epcDataLen = buffer.readShort()
                    self.bEpcData = buffer.readBytes(epcDataLen * 8)
                    if self.bEpcData:
                        self.epcData = bytesToHex(self.bEpcData)
                elif pid == 0x11:
                    self.ctesiusLtu27 = buffer.readShort()
                elif pid == 0x12:
                    self.ctesiusLtu31 = buffer.readShort()
                elif pid == 0x13:
                    self.kunYue = buffer.readShort()
                elif pid == 0x14:
                    self.rssidBm = buffer.readShort()
                elif pid == 0x20:
                    snLen = buffer.readShort()
                    if snLen:
                        self.readerSerialNumber = "".join([chr(x) for x in buffer.readBytes(snLen * 8)])
                elif pid == 0x22:
                    self.replySerialNumber = buffer.readLong()
                elif pid == 0x24:
                    self.cykeoRule = buffer.readInt()

                    

