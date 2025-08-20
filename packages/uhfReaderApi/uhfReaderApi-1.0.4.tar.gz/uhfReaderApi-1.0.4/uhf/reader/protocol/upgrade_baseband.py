from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgUpgradeBaseband(Message):

    def __init__(self, packetNumber: int, packetContent):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Update.value
        self.msgId = EnumG.UpdateMid_Baseband.value
        self.packetNumber = packetNumber
        self.packetContent = packetContent

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.packetNumber)
        if self.packetContent:
            buffer.putShort(len(self.packetContent))
            buffer.putBytes(self.packetContent)
        else:
            buffer.putShort(0)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Fail."}
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.packetNumber = buffer.readLong()
            result = buffer.readInt()
            self.rtCode = result
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(result, None)
