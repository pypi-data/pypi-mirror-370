from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestPowerCalibrationGet(Message):

    def __init__(self, childFreqRange: int, power: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_PowerCalibrationGet.value
        self.childFreqRange = childFreqRange
        self.power = power
        self.powerParam = None

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.childFreqRange)
        buffer.putInt(self.power)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.childFreqRange = buffer.readInt()
            self.power = buffer.readInt()
            self.powerParam = buffer.readInt()
            self.rtCode = 0

    def __str__(self) -> str:
        return str(self.powerParam)
