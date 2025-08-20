from uhf.reader.protocol import *
from uhf.reader.utils import *


class ParamEpcFilter(Parameter):
    # bitLength: int,
    def __init__(self, area: int, bitStart: int, hexData: str):
        self.area = area
        self.bitStart = bitStart
        self.hexData = hexData
        self.bitLength = len(hexData) * 4

    def bytesToClass(self, dataBytes):
        hex = bytesToHex(dataBytes)
        buffer = DynamicBuffer("0x" + hex)
        self.area = buffer.readInt()
        self.bitStart = buffer.readShort()
        self.bitLength = buffer.readInt()
        self.hexData = bytesToHex(buffer.readBytes(self.bitLength))
        return self

    def toBytes(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.area)
        buffer.putShort(self.bitStart)
        buffer.putInt(self.bitLength)
        buffer.putBytes(hexToBytes(self.hexData))
        return buffer.tobytes()

    def __str__(self) -> str:
        return str((self.area, self.bitStart, self.bitLength, self.hexData))
