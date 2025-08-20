from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetAutoDormancy(Message):

    def __init__(self, onOff: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetAutoDormancy.value
        self.onOff = onOff
        self.freeTime = kwargs.get("freeTime", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.onOff)
        if self.freeTime is not None:
            buffer.putInt(0x01)
            buffer.putShort(self.freeTime)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Parameter error.",
                      2: "Other error.", 3: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
