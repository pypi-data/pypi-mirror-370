from bitstring import *

"""
Token examples: 
                        'int:12'    : 12 bits as a signed integer
                        'uint:8'    : 8 bits as an unsigned integer
                        'float:64'  : 8 bytes as a big-endian float
                        'intbe:16'  : 2 bytes as a big-endian signed integer
                        'uintbe:16' : 2 bytes as a big-endian unsigned integer
                        'intle:32'  : 4 bytes as a little-endian signed integer
                        'uintle:32' : 4 bytes as a little-endian unsigned integer
                        'floatle:64': 8 bytes as a little-endian float
                        'intne:24'  : 3 bytes as a native-endian signed integer
                        'uintne:24' : 3 bytes as a native-endian unsigned integer
                        'floatne:32': 4 bytes as a native-endian float
                        'hex:80'    : 80 bits as a hex string
                        'oct:9'     : 9 bits as an octal string
                        'bin:1'     : single bit binary string
                        'ue'        : next bits as unsigned exp-Golomb code
                        'se'        : next bits as signed exp-Golomb code
                        'uie'       : next bits as unsigned interleaved exp-Golomb code
                        'sie'       : next bits as signed interleaved exp-Golomb code
                        'bits:5'    : 5 bits as a bitstring
                        'bytes:10'  : 10 bytes as a bytes object
                        'bool'      : 1 bit as a bool
                        'pad:3'     : 3 bits of padding to ignore - returns None
"""


class DynamicBuffer(BitStream):

    # 重写init需要super
    # def __init__(self):
    #     super().__init__()

    def putInt(self, value):
        self.append("uint:8=%d" % value)
        return self

    def putShort(self, value):
        self.append("uint:16=%d" % value)
        return self

    def putLong(self, value):
        self.append("uint:32=%d" % value)
        return self

    def putString(self, bitLen, value):
        self.append("uint:%d=%s" % (bitLen, value))
        return self

    def putSigned(self, bitLen, value):
        self.append("int:%d=%s" % (bitLen, value))
        return self

    def putBytes(self, bytes):
        if bytes:
            for byte in bytes:
                self.putInt(byte)
        return self

    def addPos(self, bitLen):
        self.pos += bitLen

    def setPos(self, bitLen):
        self.pos = bitLen

    def readInt(self):
        return self.read("uint:8")

    def readShort(self):
        return self.read("uint:16")

    def readLong(self):
        return self.read("uint:32")

    def readBitLen(self, bitLen):
        return self.read("uint:%d" % bitLen)

    def readSigned(self, bitLen):
        return self.read("int:%d" % bitLen)

    def readBytes(self, bitLen):
        if bitLen:
            return [self.readInt() for bit in range(int(bitLen / 8))]


if __name__ == '__main__':
    print("int:8=", 5, sep="")

    buffer = DynamicBuffer()
    buffer.putString(1,1)
    buffer.putString(1,1)
    buffer.putString(4,0)
    buffer.putString(2,0)
    # r = "000102FF0000"
    # print(hexToBytes(r))
    # buffer.putInt(0x5a)
    # buffer.putInt(0x00)
    # buffer.putInt(0x01)
    # buffer.putString(4, "0011")
    # buffer.putString(4, 2)
    # buffer.putInt(0xff)
    # buffer.putShort(0)
    # buffer.putInt(0x88)
    # buffer.putInt(0x5a)
    # buffer.putInt(int("192"))
    # buffer.putBytes([12, 43, 54])
    print(buffer.hex)
    # tobytes = buffer.tobytes()
    # for b in tobytes:
    #     print(b)

    # dynamic_buffer = DynamicBuffer("0x" + buffer.hex)
    # print(dynamic_buffer)
    # print(dynamic_buffer.readBytes(32))
    # dynamic_buffer.setPos(8)
    # print(dynamic_buffer.pos)
    # print(dynamic_buffer.readBytes(32))
