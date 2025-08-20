from uhf.reader.protocol import *
from uhf.reader.utils import *


class ParamSafeEncipheredData(Parameter):

    def __init__(self, start: int, enData: str):
        self.start = start
        self.enData = enData

    def bytesToClass(self, dataBytes):
        hex = bytesToHex(dataBytes)
        buffer = DynamicBuffer("0x" + hex)
        self.start = buffer.readShort()
        dataLen = buffer.readShort()
        self.enData = bytesToHex(buffer.readBytes(dataLen * 8))
        return self

    def toBytes(self):
        buffer = DynamicBuffer()
        buffer.putShort(self.start)
        buffer.putBytes(hexToBytes(self.enData))
        return buffer.tobytes()

    def __str__(self) -> str:
        return str((self.start, self.enData))
