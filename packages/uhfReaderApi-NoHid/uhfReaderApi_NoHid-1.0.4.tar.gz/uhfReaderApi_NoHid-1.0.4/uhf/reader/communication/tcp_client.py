from uhf.reader.communication import CommunicationInter
from uhf.reader.protocol import *
import socket
import threading


class TcpClient(CommunicationInter):

    def __init__(self):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Condition()
        self.addr = None
        self.callDisconnected = None
        self.timeout_count = 0

    def open(self, param, **kwargs):
        try:
            if not param:
                return False
            self.client.settimeout(kwargs.get("timeout", 3))
            self.client.connect(param)
            self.client.settimeout(None)
            self.keepReceived = True
            self.addr = param
            received = threading.Thread(target=self.startReceived, name="TcpReceived")
            received.start()
            processRing = threading.Thread(target=self.startProcess, name="RingBuffer")
            processRing.start()
            return True
        except Exception as ex:
            print(ex.args)

    def openSocket(self, serverSocket):
        if serverSocket:
            self.keepReceived = True
            self.client = serverSocket
            received = threading.Thread(target=self.startReceived, name="TcpReceived")
            received.start()
            processRing = threading.Thread(target=self.startProcess, name="RingBuffer")
            processRing.start()
            return True
        return False

    def sendMsg(self, message: Message):
        try:
            message.pack()
            self.client.send(message.toByte(False))
        except Exception as ex:
            print(ex.args)
        # with self.lock:
        #     print("开始等待")
        #     self.lock.wait(timeout)

    def sendBytes(self, bytes):
        self.client.send(bytes)

    def close(self):
        self.keepReceived = False
        if self.client:
            self.client.close()
        with self.ringLock:
            self.ringLock.notifyAll()

    def startReceived(self):
        while self.keepReceived:
            try:
                # print('thread %s is running...' % threading.current_thread().name)
                with self.ringLock:
                    self.client.settimeout(5)
                    recv = self.client.recv(1024)
                    self.timeout_count = 0
                    if recv:
                        # print("接收===", recv.hex().upper())
                        self.ringBuffer.writeData(recv)
                        self.ringLock.notify()
                        self.ringLock.wait()
                    else:
                        self.sendMsg(MsgAppGetBaseVersion())
            except Exception as ex:
                if ex.args[0] == "timed out":
                    self.timeout_count += 1
                    self.sendMsg(MsgAppGetBaseVersion())
                    if self.timeout_count == 3:
                        self.keepReceived = False
                        self.callDisConnect(self.addr)
                else:
                    print(ex.args)
                    # raise ex
                    self.keepReceived = False
                    self.callDisConnect(self.addr)
