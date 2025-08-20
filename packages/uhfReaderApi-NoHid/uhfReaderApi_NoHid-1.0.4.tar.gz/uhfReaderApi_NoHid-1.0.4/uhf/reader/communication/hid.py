# from uhf.reader.communication import CommunicationInter
# import threading
# from hid import *
#
#
# class HidClient(CommunicationInter):
#
#     def __init__(self):
#         super().__init__()
#         self.client = device()
#         self.lock = threading.Condition()
#
#     def open(self, param, **kwargs):
#         try:
#             self.client.open_path(param)
#             self.client.set_nonblocking(True)
#             self.keepReceived = True
#             received = threading.Thread(target=self.startReceived, name="HidReceived")
#             received.start()
#             processRing = threading.Thread(target=self.startProcess, name="RingBuffer")
#             processRing.start()
#             return True
#         except Exception as ex:
#             print(ex.args)
#
#     def sendMsg(self, message):
#         try:
#             message.pack()
#             arr = message.toByte(False)  # type:bytes
#             self.sendBytes(arr)
#         except Exception as ex:
#             print(ex.args)
#             # raise ex
#
#     def sendBytes(self, bytes):
#         tempList = list(bytes)
#         tempLen = len(tempList)
#         dataLen = tempLen
#         for i in range(divmod(tempLen, 64)[0] + 1):
#             if dataLen > 64:
#                 dataLen -= 64
#                 self.client.write([0] + tempList[i * 64:(i + 1) * 64])
#             else:
#                 len_ = tempList[i * 64:(i * 64) + dataLen]
#                 repair = [0 for i in range(64 - dataLen)]
#                 len_.extend(repair)
#                 self.client.write([0] + len_)
#
#     def close(self):
#         self.keepReceived = False
#         self.client.close()
#         with self.ringLock:
#             self.ringLock.notifyAll()
#
#     def startReceived(self):
#         while self.keepReceived:
#             try:
#                 with self.ringLock:
#                     recv = self.client.read(64, 1000)
#                     if recv:
#                         self.ringBuffer.writeData(recv)
#                         self.ringLock.notify()
#                         self.ringLock.wait()
#
#             except Exception as ex:
#                 # pass
#                 print(ex.args)
#                 self.keepReceived = False
#                 # raise ex
#         else:
#             pass
