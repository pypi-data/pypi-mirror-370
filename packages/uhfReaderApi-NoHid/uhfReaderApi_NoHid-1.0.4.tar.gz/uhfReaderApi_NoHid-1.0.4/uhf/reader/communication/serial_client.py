from uhf.reader.communication import CommunicationInter
from uhf.reader.protocol import *
import serial
import threading


class SerialClient(CommunicationInter):

    def __init__(self):
        super().__init__()
        self.client = None
        self.lock = threading.Condition()

    def open(self, param, **kwargs):
        try:
            if not param:
                return False
            # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
            self.client = serial.Serial(param[0], param[1], timeout=kwargs.get("timeout", 0.01))
            if self.client.is_open:
                self.keepReceived = True
                received = threading.Thread(target=self.startReceived, name="SerialReceived")
                received.start()
                processRing = threading.Thread(target=self.startProcess, name="RingBuffer")
                processRing.start()
                return True
        except Exception as ex:
            print(ex.args)
            # raise ex

    def sendMsg(self, message: Message):
        try:
            message.pack()
            if self.isRs485:
                message.mt_13 = "1"
                message.rs485Address = self.rs485Address
            self.client.write(message.toByte(self.isRs485))
            # with self.lock:
            #     print("开始等待")
            #     self.lock.wait(timeout)
        except Exception as ex:
            print(ex.args)

    def sendBytes(self, bytes):
        try:
            self.client.write(bytes)
        except Exception as ex:
            print(ex.args)

    def close(self):
        self.keepReceived = False
        # if self.client:
        #     if self.client.is_open:
        #         self.client.close()
        with self.ringLock:
            self.ringLock.notifyAll()

    def startReceived(self):
        while self.keepReceived:
            try:
                # print('thread %s is running...' % threading.current_thread().name)
                with self.ringLock:
                    recv = self.client.read(1024)  # type:bytes
                    if recv:
                        # print("接收===", recv.hex().upper())
                        self.ringBuffer.writeData(recv)
                        # print("环形内容===", self.ringBuffer.buffer.hex)
                        self.ringLock.notify()
                        self.ringLock.wait()
            except Exception as ex:
                print("startReceived->",ex.args)
                # raise ex
        else:
            if self.client:
                if self.client.is_open:
                    self.client.close()
