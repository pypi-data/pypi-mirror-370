from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetRs485(Message):

    def __init__(self, address: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetRs485.value
        self.address = address
        self.baudRate = kwargs.get("baudRate", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.address)
        if self.baudRate is not None:
            buffer.putInt(0x01)
            buffer.putInt(self.baudRate)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Other error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
