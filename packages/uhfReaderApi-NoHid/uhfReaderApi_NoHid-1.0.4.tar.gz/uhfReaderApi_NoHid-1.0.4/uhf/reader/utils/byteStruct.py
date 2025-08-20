import struct


class DataStream(bytearray):

    def append(self, v, fmt='>B'):
        self.extend(struct.pack(fmt, v))


if __name__ == '__main__':
    x = DataStream()
    x.append(5)
    print(x)
    x.append(0xff, '>B')
    print(x)
    x.append(0x12,">H")
    print(x)
    print(x.hex())

# Character	Byte order	Size	Alignment
# @(默认)	本机	本机	本机,凑够4字节
# =	本机	标准	none,按原字节数
# <	小端	标准	none,按原字节数
# >	大端	标准	none,按原字节数
# !	network(大端)	标准	none,按原字节数
#
# 格式符	C语言类型	Python类型	Standard size
# x	pad byte(填充字节)	no value	 
# c	char	string of length 1	1
# b	signed char	integer	1
# B	unsigned char	integer	1
# ?	_Bool	bool	1
# h	short	integer	2
# H	unsigned short	integer	2
# i	int	integer	4
# I(大写的i)	unsigned int	integer	4
# l(小写的L)	long	integer	4
# L	unsigned long	long	4
# q	long long	long	8
# Q	unsigned long long	long	8
# f	float	float	4
# d	double	float	8
# s	char[]	string	 
# p	char[]	string	 
# P	void *	long	 
# 注- -!

# _Bool在C99中定义,如果没有这个类型,则将这个类型视为char,一个字节;
# q和Q只适用于64位机器;
# 每个格式前可以有一个数字,表示这个类型的个数,如s格式表示一定长度的字符串,4s表示长度为4的字符串;4i表示四个int;
# P用来转换一个指针,其长度和计算机相关;
# f和d的长度和计算机相关;
