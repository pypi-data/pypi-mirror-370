import threading
from uhf.reader.utils import *
from uhf.reader.protocol import *


class CommunicationInter(object):

    def __init__(self):
        self.serialNumber = None
        self.rs485Address = 0
        self.isRs485 = False
        self.isSendHeartbeat = False
        self.keepReceived = False
        self.ringBuffer = RingBuffer()
        self.ringLock = threading.Condition()
        self.onMessageReceived = None
        self.onTcpDisConnect = None
        # self.callBackEpcInfo = None
        # self.callBackEpcOver = None
        # self.callBack6bInfo = None
        # self.callBack6bOver = None
        # self.callBackGbInfo = None
        # self.callBackGbOver = None

    def open(self, param, **kwargs):
        pass

    def openSocket(self, serverSocket):
        pass

    def sendMsg(self, message):
        # message.pack()
        pass

    def sendBytes(self, bytes):
        pass

    def close(self):
        pass

    def callMessage(self, msg: Message):
        if self.onMessageReceived:
            self.onMessageReceived(msg)

    def callDisConnect(self, addr):
        if self.onTcpDisConnect:
            self.onTcpDisConnect(addr)

    def startProcess(self):
        while self.keepReceived:
            try:
                # print('thread %s is running...' % threading.current_thread().name)
                with self.ringLock:
                    if self.ringBuffer.dataCount < 48:
                        self.ringLock.notify()
                        self.ringLock.wait()
                    if self.ringBuffer.indexData(0) != EnumG.Msg_Header.value:
                        self.ringBuffer.cleanData(1 * 8)
                        continue
                    else:
                        temp = DynamicBuffer()
                        if self.ringBuffer.dataCount >= 56:
                            if self.isRs485:
                                temp.putBytes(self.ringBuffer.readData(48))
                            else:
                                temp.putBytes(self.ringBuffer.readData(40))
                            dataLen = self.ringBuffer.readBit(16)
                            if dataLen != 0:
                                temp.putShort(dataLen)
                            if (dataLen + 2) * 8 > self.ringBuffer.dataCount:
                                if dataLen > 1024:
                                    self.ringBuffer.cleanData(1 * 8)
                                else:
                                    self.ringBuffer.subPos(temp.len)
                                    self.ringLock.notify()
                                    self.ringLock.wait()
                                continue
                            else:
                                temp.putBytes(self.ringBuffer.readData(dataLen * 8))
                                data = self.ringBuffer.readData(16)
                                temp.putBytes(data)
                                msg = Message().new(temp.hex)
                                if msg:
                                    if msg.checkCrc():
                                        if self.isRs485 and self.rs485Address != msg.rs485Address:
                                            continue
                                        self.ringBuffer.cleanAll()
                                        self.callMessage(msg)
                                    else:
                                        print("crc错误")
                                else:
                                    print("-------------------------------解析错误--------------------------------")
                                    self.ringBuffer.cleanData(temp.len)
                        else:
                            self.ringLock.notify()
                            self.ringLock.wait()
            except Exception as ex:
                # pass
                print(ex.args)
                raise ex
