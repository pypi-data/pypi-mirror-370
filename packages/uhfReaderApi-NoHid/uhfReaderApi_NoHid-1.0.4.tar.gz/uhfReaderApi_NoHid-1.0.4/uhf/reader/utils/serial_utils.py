import serial.tools.list_ports


def getSerials():
    """
    查询串口列表
    :return: 串口list
    """
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) == 0:
        return []
    else:
        return [port_list[i].device for i in range(0, len(port_list))]