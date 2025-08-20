from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetWhiteListAction(Message):

    def __init__(self, relay: int, relayCloseTime: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetWhiteListActionParam.value
        self.relay = relay
        self.relayCloseTime = relayCloseTime

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.relay)
        buffer.putShort(self.relayCloseTime)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Set Fail."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
