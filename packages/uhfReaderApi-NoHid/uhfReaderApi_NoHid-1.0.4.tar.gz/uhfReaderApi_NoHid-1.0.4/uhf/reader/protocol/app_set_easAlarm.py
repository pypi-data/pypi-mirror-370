from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetEasAlarm(Message):

    def __init__(self, alarmSwitch: int, filterData: int, start: int, hexContent: str, hexMask: str,
                 **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetEasAlarm.value
        self.alarmSwitch = alarmSwitch
        self.filterData = filterData
        self.start = start
        self.hexContent = hexContent
        self.hexMask = hexMask
        self.actionSuccess = kwargs.get("actionSuccess", None)  # type:ActionParamSuccess
        self.actionFail = kwargs.get("actionFail", None)  # type:ActionParamFail

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.alarmSwitch)
        buffer.putInt(self.filterData)
        buffer.putShort(self.start)
        if self.hexContent:
            content_bytes = hexToBytes(self.hexContent)
            buffer.putShort(len(content_bytes))
            buffer.putBytes(content_bytes)

        if self.hexMask:
            mask_bytes = hexToBytes(self.hexMask)
            buffer.putShort(len(mask_bytes))
            buffer.putBytes(mask_bytes)

        if self.actionSuccess is not None:
            buffer.putInt(0x01)
            suc_bytes = self.actionSuccess.toBytes()
            buffer.putShort(len(suc_bytes))
            buffer.putBytes(suc_bytes)

        if self.actionFail is not None:
            buffer.putInt(0x02)
            fail_bytes = self.actionFail.toBytes()
            buffer.putShort(len(fail_bytes))
            buffer.putBytes(fail_bytes)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Set failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
