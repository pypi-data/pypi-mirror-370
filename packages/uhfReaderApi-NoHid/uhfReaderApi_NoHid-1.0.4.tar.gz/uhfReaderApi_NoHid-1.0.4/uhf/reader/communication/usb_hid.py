# from uhf.reader.communication import CommunicationInter
# from uhf.reader.protocol import *
# from uhf.reader.utils import *
# import threading
# import usb.core
# import usb.util
# import platform
#
#
# class UsbHidClient(CommunicationInter):
#
#     def __init__(self):
#         super().__init__()
#         # self.dev = usb.core.find(idVendor=0x03EB, idProduct=0x2421)
#         self.__inPoint = None
#         self.__outPoint = None
#         self.dev = None  # type:usb.core.Device
#         self.lock = threading.Condition()
#
#     def open(self, dev: usb.core.Device, **kwargs):
#         try:
#             if dev:
#                 self.dev = dev
#                 if platform.system().lower() == 'linux':
#                     if self.dev.is_kernel_driver_active(0):
#                         self.dev.detach_kernel_driver(0)
#
#                 self.dev.set_configuration()
#                 configuration = self.dev.get_active_configuration()
#                 cfg_ = configuration[(0, 0)]
#                 self.__outPoint = usb.util.find_descriptor(
#                     cfg_,
#                     custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
#                 self.__inPoint = usb.util.find_descriptor(
#                     cfg_,
#                     custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
#                 if self.__outPoint and self.__inPoint is None:
#                     return False
#                 self.keepReceived = True
#                 received = threading.Thread(target=self.startReceived, name="HidReceived",
#                                             args=(self.dev,))
#                 received.start()
#                 processRing = threading.Thread(target=self.startProcess, name="RingBuffer")
#                 processRing.start()
#                 return True
#             else:
#                 return False
#         except Exception as ex:
#             print(ex.args)
#
#     def sendMsg(self, message: Message):
#         try:
#             message.pack()
#             arr = message.toByte(False)  # type:bytes
#             self.sendBytes(arr)
#         except Exception as ex:
#             print(ex.args)
#             # raise ex
#
#     # 传输大字节待解决
#     def sendBytes(self, bytes):
#         tempList = list(bytes)
#         tempLen = len(tempList)
#         dataLen = tempLen
#         for i in range(divmod(tempLen, 64)[0] + 1):
#             if dataLen > 64:
#                 dataLen -= 64
#                 self.__outPoint.write(tempList[i * 64:(i + 1) * 64])
#             else:
#                 len_ = tempList[i * 64:(i * 64) + dataLen]
#                 repair = [0 for i in range(64 - dataLen)]
#                 len_.extend(repair)
#                 self.__outPoint.write(len_)
#
#     def close(self):
#         # usb.util.release_interface(self.dev, self.__inPoint)
#         # usb.util.release_interface(self.dev, self.__outPoint)
#         self.keepReceived = False
#         with self.ringLock:
#             self.ringLock.notifyAll()
#             self.ringLock = None
#
#     def startReceived(self, dev):
#         while self.keepReceived:
#             try:
#                 with self.ringLock:
#                     recv = self.__inPoint.read(64)
#                     # recv = self.dev.read(self.__inPoint, 64)
#                     if recv:
#                         self.ringBuffer.writeData(recv)
#                         self.ringLock.notify()
#                         self.ringLock.wait()
#             except Exception as ex:
#                 pass
#                 # print(ex.args)
#                 # raise ex
#         else:
#             usb.util.dispose_resources(dev)
