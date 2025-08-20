from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppRestoreDefault(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_RestoreDefault.value
        self.confirmationCode = 0x5AA5A55A

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.confirmationCode)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Other error."}
            self.rtCode = self.cData[0]
            self.rtMsg = dirMsg.get(self.rtCode, None)
