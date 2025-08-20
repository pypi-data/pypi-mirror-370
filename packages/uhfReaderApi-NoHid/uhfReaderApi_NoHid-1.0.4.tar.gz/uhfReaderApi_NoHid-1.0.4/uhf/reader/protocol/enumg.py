from enum import Enum


class EnumG(Enum):

    Msg_Header = 0x5A
    # Msg_Header = 0xC5
    # 消息类别
    Msg_Type_Bit_App = 1
    Msg_Type_Bit_Base = 2
    Msg_Type_Bit_Update = 4
    Msg_Type_Bit_Test = 5

    # base mid
    BaseMid_GetCapabilities = 0x00
    BaseMid_SetPower = 0x01
    BaseMid_GetPower = 0x02
    BaseMid_SetFreqRange = 0x03
    BaseMid_GetFreqRange = 0x04
    BaseMid_SetFrequency = 0x05
    BaseMid_GetFrequency = 0x06
    BaseMid_SetAntennaHub = 0x07
    BaseMid_GetAntennaHub = 0x08
    BaseMid_SetTagLog = 0x09
    BaseMid_GetTagLog = 0x0A
    BaseMid_SetBaseband = 0x0B
    BaseMid_GetBaseband = 0x0C
    BaseMid_SetAutoDormancy = 0x0D
    BaseMid_GetAutoDormancy = 0x0E
    BaseMid_SetResidenceTime = 0xE0
    BaseMid_GetResidenceTime = 0xE1
    BaseMid_SetGbBaseBand = 0xE2
    BaseMid_GetGbBaseBand = 0xE3
    BaseMid_InventoryEpc = 0x10
    BaseMid_WriteEpc = 0x11
    BaseMid_LockEpc = 0x12
    BaseMid_DestroyEpc = 0x13
    BaseMid_MonzaQT = 0x14
    BaseMid_SuperRW = 0x1A
    BaseMid_Inventory6b = 0x40
    BaseMid_Write6b = 0x41
    BaseMid_Lock6b = 0x42
    BaseMid_Lock6bGet = 0x43
    BaseMid_InventoryGb = 0x50
    BaseMid_WriteGb = 0x51
    BaseMid_LockGb = 0x52
    BaseMid_DestroyGb = 0x53
    BaseMid_InventoryGJb = 0x60
    BaseMid_WriteGJb = 0x61
    BaseMid_LockGJb = 0x62
    BaseMid_DestroyGJb = 0x63
    BaseMid_SafeAttestation = 0xF0
    BaseMid_Hybrid = 0xA0
    BaseMid_Stop = 0xFF

    # app mid
    AppMid_GetReaderInfo = 0x00
    AppMid_GetBaseVersion = 0x01
    AppMid_SetSerialParam = 0x02
    AppMid_GetSerialParam = 0x03
    AppMid_SetReaderIP = 0x04
    AppMid_GetReaderIP = 0x05
    AppMid_GetReaderMac = 0x06
    AppMid_SetTcpMode = 0x07
    AppMid_GetTcpMode = 0x08
    AppMid_SetGpo = 0x09
    AppMid_GetGpiState = 0x0A
    AppMid_SetGpiTrigger = 0x0B
    AppMid_GetGpiTrigger = 0x0C
    AppMid_SetWigan = 0x0D
    AppMid_GetWigan = 0x0E
    AppMid_Reset = 0x0F
    AppMid_SetReaderTime = 0x10
    AppMid_GetReaderTime = 0x11
    AppMid_Heartbeat = 0x12
    AppMid_SetReaderMac = 0x13
    AppMid_RestoreDefault = 0x14
    AppMid_SetRs485 = 0x15
    AppMid_GetRs485 = 0x16
    AppMid_SetBreakpointResume = 0x17
    AppMid_GetBreakpointResume = 0x18
    AppMid_GetCacheTagData = 0x1B
    AppMid_ClearCacheTagData = 0x1C
    AppMid_TagDataReply = 0x1D
    AppMid_SetBeepOnOff = 0x1E
    AppMid_SetBeep = 0x1F
    AppMid_GetWhiteList = 0x20
    AppMid_ImportWhiteList = 0x21
    AppMid_DelWhiteList = 0x22
    AppMid_SetWhiteListActionParam = 0x23
    AppMid_GetWhiteListActionParam = 0x24
    AppMid_SetWhiteListSwitch = 0x25
    AppMid_GetWhiteListSwitch = 0x26
    AppMid_SetUdpParam = 0x27
    AppMid_GetUdpParam = 0x28
    AppMid_SetHttpParam = 0x29
    AppMid_GetHttpParam = 0x2A
    AppMid_SetWifiHotspotSearch = 0x31
    AppMid_GetWifiHotspotSearch = 0x32
    AppMid_SetWifiHotspot = 0x33
    AppMid_GetWifiConnectStatus = 0x34
    AppMid_SetWifiIp = 0x35
    AppMid_GetWifiIp = 0x36
    AppMid_SetWifiOnOff = 0x37
    AppMid_GetWifiOnOff = 0x38

    # EAS定制
    AppMid_SetEasAlarm = 0x3F
    AppMid_GetEasAlarm = 0x40
    AppMid_SetAlarmPerform = 0x23
    AppMid_GetAlarmPerform = 0x24

    # 基带主动上传指令
    BaseLogMid_Epc = 0x00
    BaseLogMid_EpcOver = 0x01
    BaseLogMid_EpcAntId = 0x02
    BaseLogMid_6b = 0x20
    BaseLogMid_6bOver = 0x21
    BaseLogMid_Gb = 0x30
    BaseLogMid_GbOver = 0x31
    BaseLogMid_GJb = 0x40
    BaseLogMid_GJbOver = 0x41

    # 应用主动上传指令 mid
    AppLogMid_gpi = 0x00
    AppLogMid_gpiOver = 0x01
    AppLogMid_allGpiState = 0x02

    # 升级指令 mid
    UpdateMid_App = 0x00
    UpdateMid_Baseband = 0x01

    # 测试指令 mid
    TestMid_CarrierWave = 0x00
    TestMid_DCbias = 0x01
    TestMid_DCbiasGet = 0x02
    TestMid_PowerCalibration = 0x03
    TestMid_PowerCalibrationGet = 0x04
    TestMid_VSWRcheck = 0x05
    TestMid_DCAutobias = 0x06
    TestMid_EnvRssiDetection = 0x07
    TestMid_RssiCalibrationSet = 0x08
    TestMid_RssiCalibrationGet = 0x09
    TestMid_EnvRssiAutoDetection = 0x0A
    TestMid_SerialNoSet = 0x10
    TestMid_ReaderWorkModeSet = 0x11
    TestMid_ReaderWorkModeGet = 0x12
    TestMid_EpcEncryptionSet = 0x13
    TestMid_EpcEncryptionGet = 0x14
    TestMid_R2000ReadWrite = 0x15
    TestMid_R2000ReceivingGain = 0x16

    TestMid_Chip = 0x31

    # 连续 / 单次
    InventoryMode_Single = 0
    InventoryMode_Inventory = 1

    # 锁定类型
    LockMode_Unlock = 0
    LockMode_Lock = 1
    LockMode_PermanentUnlock = 2
    LockMode_PermanentLock = 3

    # 6b标签读取类型
    ReadMode6b_Tid = 0
    ReadMode6b_TidAndUserData = 1
    ReadMode6b_UserData = 2

    # 选择参数匹配区
    ParamFilterArea_EPC = 1
    ParamFilterArea_TID = 2
    ParamFilterArea_UserData = 3

    # 写入标签数据区
    WriteArea_Reserved = 0
    WriteArea_Epc = 1
    WriteArea_Tid = 2
    WriteArea_UserData = 3

    # 6C标签TID读取模式
    ParamTidMode_Auto = 0
    ParamTidMode_Fixed = 1

    # 锁定标签区
    LockArea_Destroy = 0
    LockArea_Access = 1
    LockArea_Epc = 2
    LockArea_Tid = 3
    LockArea_UserData = 4

    AntennaNo_1 = 1
    AntennaNo_2 = 2
    AntennaNo_3 = 4
    AntennaNo_4 = 8
    AntennaNo_5 = 16
    AntennaNo_6 = 32
    AntennaNo_7 = 64
    AntennaNo_8 = 128
    AntennaNo_9 = 256
    AntennaNo_10 = 512
    AntennaNo_11 = 1024
    AntennaNo_12 = 2048
    AntennaNo_13 = 4096
    AntennaNo_14 = 8192
    AntennaNo_15 = 16384
    AntennaNo_16 = 32768
    AntennaNo_17 = 65536
    AntennaNo_18 = 131072
    AntennaNo_19 = 262144
    AntennaNo_20 = 524288
    AntennaNo_21 = 1048576
    AntennaNo_22 = 2097152
    AntennaNo_23 = 4194304
    AntennaNo_24 = 8388608
    AntennaNo_25 = 16777216
    AntennaNo_26 = 33554432
    AntennaNo_27 = 67108864
    AntennaNo_28 = 134217728
    AntennaNo_29 = 268435456
    AntennaNo_30 = 536870912
    AntennaNo_31 = 1073741824
    AntennaNo_32 = 2147483648