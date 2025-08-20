from uhf.reader.utils.HexUtils import *
from uhf.reader.utils.byteBuffer import *
from uhf.reader.protocol import EnumG

class Message(object):

    def __init__(self):
        # self.head = 0x5A
        self.head = EnumG.Msg_Header.value
        self.pType = 0x00
        self.pVersion = 0x01
        self.mt_14_15 = "00"
        self.mt_13 = "0"
        self.mt_12 = "0"
        self.mt_8_11 = 0
        self.msgId = 0xFF

        self.rs485Address = 0
        self.dataLen = 0
        self.cData = []
        self.crcData = []
        self.crc = []
        self.msgData = []
        self.rtCode = -1
        self.rtMsg = None

    def new(self, data: str):
        try:
            if not data.startswith("0x"):
                data = "0x" + data
            bitBuffer = DynamicBuffer(data)
            self.msgData = bitBuffer.tobytes()
            self.head = bitBuffer.readInt()
            self.pType = bitBuffer.readInt()
            self.pVersion = bitBuffer.readInt()
            self.mt_14_15 = bitBuffer.readBitLen(2)
            self.mt_13 = bitBuffer.readBitLen(1)
            self.mt_12 = bitBuffer.readBitLen(1)
            self.mt_8_11 = bitBuffer.readBitLen(4)
            self.msgId = bitBuffer.readInt()
            if self.mt_13 == 1:
                self.rs485Address = bitBuffer.readInt()
            self.dataLen = bitBuffer.readShort()
            if self.dataLen:
                self.cData = bitBuffer.readBytes(self.dataLen * 8)
            self.crc = bitBuffer.readBytes(16)
            bitBuffer.setPos(8)
            self.crcData = bitBuffer.readBytes((len(self.msgData) - 3) * 8)
            return self
        except Exception as ex:
            print(["Message-->"], ex.args)
            # raise ex
            # return None

    def toByte(self, is485):
        try:
            bitBuffer = DynamicBuffer()
            bitBuffer.putInt(self.head).putInt(self.pType).putInt(self.pVersion)
            bitBuffer.putString(4, str(self.mt_14_15) + str(self.mt_13) + str(self.mt_12))
            bitBuffer.putString(4, self.mt_8_11).putInt(self.msgId)
            if is485:
                bitBuffer.putInt(self.rs485Address)
            bitBuffer.putShort(self.dataLen)
            if self.cData and len(self.cData) == self.dataLen:
                bitBuffer.putBytes(self.cData)
            self.crcData = Message.crc16_Xmodem_hex(bitBuffer.hex[2:]).zfill(4)  # 当前hex去掉5a
            self.crc = hexToBytes(self.crcData)
            bitBuffer.putBytes(self.crc)
            self.msgData = bitBuffer.tobytes()
            # print(bytesToHex(self.msgData))
            return self.msgData
        except Exception as ex:
            raise ex

    def pack(self):
        pass

    def unPack(self):
        pass

    def toKey(self):
        return str(self.mt_8_11) + str(self.msgId)

    def checkCrc(self):
        if self.crcData and self.crc:
            xmodem_hex = Message.crc16_Xmodem_hex(self.crcData)
            to_hex = bytesToHex(self.crc)
            if xmodem_hex.zfill(4) == to_hex:
                return True
            return False

    @staticmethod
    def crc16_Xmodem(bytes):
        if isinstance(bytes, str):
            bytes = hexToBytes(bytes)
        crc = 0x00
        polynomial = 0x1021
        for byte in bytes:
            for i in range(8):
                bit = ((byte >> (7 - i) & 1) == 1)
                c15 = ((crc >> 15 & 1) == 1)
                crc <<= 1
                if c15 ^ bit:
                    crc ^= polynomial
        crc &= 0xffff
        return crc

    @staticmethod
    def crc16_Xmodem_hex(bytes):
        return hex(Message.crc16_Xmodem(bytes))[2:].zfill(4)

    @staticmethod
    def intToByte(value):
        return value.to_bytes(2, byteorder='big', signed=False)


if __name__ == '__main__':
    pass
    print(Message.crc16_Xmodem([0, 1, 17, 18, 0, 4, 0, 0, 1, 82]))
    print()
    print(hex(1628))
    print(bytesToHex(Message.intToByte(1628)))
    print("65c0".zfill(4))
    # msg = Message()
    # print(msg.toByte(False).hex())
    # msg.test([1])
    # if 1:
    #     print(124)
    # new = msg.new("0x5a000102ff0000885a")
    # print(new)
    # s1 = 34906
    # print(Message.crc16_Xmodem("000102FF0000"))
    # print(msg.calc_crc("000102FF0000"))
    # for key, value in enumerate(range(8)):
    #     print(key, value)
    # print(hex(Message.crc16_Xmodem("000102FF0000"))[2:])
    # print(Message.crc16_Xmodem_hex("000102FF0000"))
    # print(hexToBytes(s1.to_bytes(4, byteorder='big', signed=True).hex()))
    # temp=[90, 0, 1, 0, 255, 0, 0, 101, 50]
    # print(temp[1:len(temp)-2])
    # se = 20
    # print(hex(18))
    # print(se.to_bytes(4, byteorder='big', signed=False))
    # print("123"[-1])
    # print(int("2"))
    # print(str(bytesToInt("0000")) + str(bytesToInt("0001")))

    # msgType = str(bytesToInt(self.mt_14_15 + self.mt_13 + self.mt_12)) + str(bytesToInt(self.mt_8_11))
    # buffer = [self.head, self.pType, self.pVersion, int(msgType, 16), self.msgId]
    # if is485:
    #     buffer.append(self.rs485Address)
    # buffer.append(self.dataLen)
    # if self.cData and len(self.cData) == self.dataLen:
    #     buffer.append(self.cData)
    # self.crcData = Message.crc16_Xmodem_hex(buffer[1:])
    # self.crc = hexToBytes(self.crcData)
    # buffer.extend(self.crc)
    # self.msgData = buffer
