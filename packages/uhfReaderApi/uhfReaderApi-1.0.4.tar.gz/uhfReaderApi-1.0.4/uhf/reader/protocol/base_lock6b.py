from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseLock6b(Message):

    def __init__(self, antennaEnable: int, hexMatchTid: str, lockIndex: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_Lock6b.value
        self.antennaEnable = antennaEnable
        self.hexMatchTid = hexMatchTid
        self.lockIndex = lockIndex
        self.errorIndex = None

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putBytes(hexToBytes(self.hexMatchTid))
        buffer.putInt(self.lockIndex)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Other error.", }
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
            if len(self.cData) > 1:
                errBuffer = DynamicBuffer("0x" + bytesToHex(self.cData))
                errBuffer.pos = 8
                if errBuffer.readInt() == 1:
                    self.errorIndex = errBuffer.readInt()
