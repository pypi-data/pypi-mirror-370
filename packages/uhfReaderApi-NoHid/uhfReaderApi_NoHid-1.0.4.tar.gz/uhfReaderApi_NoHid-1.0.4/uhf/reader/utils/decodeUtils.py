def listToAscii(arr: list):
    if arr:
        return "".join(list(map(chr, arr)))


def bytesToAscii(arr):
    if arr:
        b = bytearray()
        b.extend(arr)
        return b.decode(encoding='ascii')
