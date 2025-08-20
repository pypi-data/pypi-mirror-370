from uhf.reader.utils.byteBuffer import DynamicBuffer
from uhf.reader.utils.HexUtils import *


class RingBuffer(object):

    def __init__(self):
        super().__init__()
        self.buffer = DynamicBuffer()
        self.buffer.pos = 0
        self.dataCount = 0
        self.dataHead = 0
        self.dataEnd = 0

    def reset(self):
        # self.buffer.pos = 0
        self.dataCount = 0
        self.dataHead = 0
        self.dataEnd = 0

    def writeData(self, data: bytes):
        self.buffer.putBytes(data)
        self.dataEnd += len(data) * 8
        self.dataCount += len(data) * 8

    def readData(self, bitLen):
        if self.dataCount:
            if bitLen <= self.dataCount:
                read_bitLen_bytes = self.buffer.readBytes(bitLen)
                self.dataHead += bitLen
                self.dataCount -= bitLen
                return read_bitLen_bytes

    def readBit(self, bitLen):
        if self.dataCount:
            if bitLen <= self.dataCount:
                self.dataHead += bitLen
                self.dataCount -= bitLen
                bit_len = self.buffer.readBitLen(bitLen)
                return bit_len
            else:
                return 0

    def indexData(self, pos):
        if pos < self.dataCount and self.dataCount > 0:
            read_int = self.buffer.readInt()
            self.buffer.pos -= 8
            return read_int

    def cleanData(self, bitLen):
        if bitLen > self.dataCount:
            self.reset()
            self.buffer.clear()
        else:
            self.dataHead += bitLen
            self.dataCount -= bitLen
            self.buffer.pos += bitLen

    def cleanAll(self):
        if self.dataHead == self.dataEnd:
            self.buffer.clear()

    def subPos(self, pos):
        if pos <= self.buffer.pos:
            self.buffer.pos -= pos
            self.dataCount += pos
            self.dataHead -= pos


if __name__ == '__main__':
    buffer = RingBuffer()
    buffer.writeData(hexToBytes("AAbbccddeeff"))
    print(hex(buffer.indexData(0)))
    print(buffer)
    print(bytesToHex(buffer.readData(32)))
    print(buffer)
    print(bytesToHex(buffer.readData(32)))
    print(buffer)
    buffer.writeData(hexToBytes("112211221122"))
    print(buffer.readBit(8))
    print(bytesToHex(buffer.readData(32)))
