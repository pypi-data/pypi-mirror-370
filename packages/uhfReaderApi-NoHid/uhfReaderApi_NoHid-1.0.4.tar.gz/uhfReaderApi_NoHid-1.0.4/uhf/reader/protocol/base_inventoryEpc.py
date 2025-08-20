from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseInventoryEpc(Message):

    def __init__(self, antennaEnable: int, inventoryMode: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_InventoryEpc.value
        self.antennaEnable = antennaEnable
        self.inventoryMode = inventoryMode
        self.filter = kwargs.get("filter", None)  # type:ParamEpcFilter
        self.readTid = kwargs.get("readTid", None)  # type:ParamEpcReadTid
        self.readUserData = kwargs.get("readUserData", None)  # type:ParamEpcReadUserData
        self.readReserved = kwargs.get("readReserved", None)  # type:ParamEpcReadReserved
        self.hexPassword = kwargs.get("hexPassword", None)
        self.monzaQtPeek = kwargs.get("monzaQtPeek", None)
        self.rfmicron = kwargs.get("rfmicron", None)
        self.emSensor = kwargs.get("emSensor", None)
        self.readEpc = kwargs.get("readEpc", None)  # type:ParamEpcReadEpc
        self.paramFastId = kwargs.get("paramFastId", None)  # type:ParamEpcFastId
        self.ctesius = kwargs.get("ctesius", None)
        self.seed = kwargs.get("seed", None)
        self.desEcpParam = kwargs.get("desEcpParam", None)
        self.kunYue = kwargs.get("kunYue", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putInt(self.inventoryMode)
        if self.filter is not None:
            buffer.putInt(0x01)
            filter_bytes = self.filter.toBytes()
            buffer.putShort(len(filter_bytes))
            buffer.putBytes(filter_bytes)
        if self.readTid is not None:
            buffer.putInt(0x02)
            buffer.putBytes(self.readTid.toBytes())
        if self.readUserData is not None:
            buffer.putInt(0x03)
            buffer.putBytes(self.readUserData.toBytes())
        if self.readReserved is not None:
            buffer.putInt(0x04)
            buffer.putBytes(self.readReserved.toBytes())
        if self.hexPassword is not None:
            buffer.putInt(0x05)
            buffer.putBytes(hexToBytes(self.hexPassword))
        if self.monzaQtPeek is not None:
            buffer.putInt(0x06)
            buffer.putInt(self.monzaQtPeek)
        if self.rfmicron is not None:
            buffer.putInt(0x07)
            buffer.putInt(self.rfmicron)
        if self.emSensor is not None:
            buffer.putInt(0x08)
            buffer.putInt(self.emSensor)
        if self.readEpc is not None:
            buffer.putInt(0x09)
            buffer.putBytes(self.readEpc.toBytes())
        if self.paramFastId is not None:
            buffer.putInt(0x0A)
            buffer.putBytes(self.paramFastId.toBytes())
        if self.ctesius is not None:
            buffer.putInt(0x12)
            buffer.putInt(self.ctesius)
        if self.desEcpParam is not None:
            buffer.putInt(0x14)
            buffer.putInt(self.desEcpParam)
        if self.kunYue is not None:
            buffer.putInt(0x16)
            buffer.putInt(self.kunYue)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter error.",
                      2: "Filter parameter error.", 3: "TID parameter error.", 4: "User parameter error.",
                      5: "Reserve parameter error.", 6: "Other error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
