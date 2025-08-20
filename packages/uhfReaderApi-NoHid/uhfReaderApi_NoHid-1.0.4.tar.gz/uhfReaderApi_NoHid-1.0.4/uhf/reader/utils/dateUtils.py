from time import *


def secondToDhms(second):
    """
    秒转换成天、时、分、秒格式
    :param second:秒
    :return:天、时、分、秒格式字符串
    """
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return str("%02d:%02d:%02d:%02d" % (d, h, m, s))


def secondToHms(second):
    """
    秒转换成时、分、秒格式
    :param second: 秒
    :return: 时、分、秒格式字符串
    """
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    return str("%02d:%02d:%02d" % (h, m, s))


def nowTimeStr():
    """
    当前时间格式化
    :return: 当前时间格式化后的字符串
    """
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


# def nowTimeSecond():
#     """
#     当前时间的秒数
#     :rtype: object
#     """
#     return int(mktime(strptime(nowTimeStr(), "%Y-%m-%d %H:%M:%S")))


def nowTimeSecond():
    """

    :return: 当前时间的秒数
    """
    return int(time())


def secondFormat(second):
    """
    给定秒数格式化
    :param second:秒
    :return: 格式化后的字符串
    """
    return strftime("%Y-%m-%d %H:%M:%S", localtime(second))


if __name__ == '__main__':
    print(int(time()))
    print(nowTimeSecond())
