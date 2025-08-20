from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestCarrierWave(Message):

    def __init__(self, antennaNum: int, frequencyNum: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_CarrierWave.value
        self.antennaNum = antennaNum
        self.frequencyNum = frequencyNum

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaNum)
        buffer.putInt(self.frequencyNum)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Frequency parameter reader is not supported.",
                      2: "Port parameter reader is not supported.", 3: "Lock failure.", 4: "Other error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
