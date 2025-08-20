from uhf.reader.utils.HexUtils import bytesToHex
from uhf.reader.utils.byteBuffer import *


def getPcLen(value: str):
    """
    :rtype: int
    """
    if value:
        t1, t2 = divmod(len(value), 4)
        if t2 == 0:
            return t1
        elif t2 > 0:
            return t1 + 1


def getPcValue(value: str):
    """
    计算epc的pc值
    :param value: 16进制写入内容
    :return: 16进制 pc值
    """
    pcLen = getPcLen(value)
    iPc = pcLen << 11
    buffer = DynamicBuffer()
    buffer.putLong(iPc)
    buffer.pos = 16
    return bytesToHex(buffer.readBytes(16))


def getEpcData(value: str):
    """
    写6C epc 快捷返回pc+内容
    :param value: 16进制写入内容
    :return:pc+内容
    """
    value_len = getPcLen(value) * 4
    pc_value = getPcValue(value)
    return pc_value + value.ljust(value_len, "0")


def getGbPcValue(value: str):
    """
    计算GB 编码区的pc值
    :param value: 16进制写入内容
    :return: 16进制 pc值
    """
    pcLen = getPcLen(value)
    iPc = pcLen << 8
    buffer = DynamicBuffer()
    buffer.putLong(iPc)
    buffer.pos = 16
    return bytesToHex(buffer.readBytes(16))


def getGbData(value: str):
    """
    写GB 编码区 快捷返回pc+内容
    :param value: 16写入进制内容
    :return: pc+内容
    """
    value_len = getPcLen(value) * 4
    pc_value = getGbPcValue(value)
    return pc_value + value.ljust(value_len, "0")


if __name__ == '__main__':

    print(divmod(632,64))
    for i in range(1):
        print(i)
    l = [1, 2, 3, 4, 5]
    l.extend([4, 5, 6, 7])
    print(l)

