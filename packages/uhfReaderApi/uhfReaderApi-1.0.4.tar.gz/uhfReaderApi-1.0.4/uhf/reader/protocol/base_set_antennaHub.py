from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetAntennaHub(Message):

    def __init__(self, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetAntennaHub.value
        self.dicHub = kwargs

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.dicHub:
            for key, value in self.dicHub.items():
                if str(key).isdigit():
                    buffer.putInt(int(key))
                    buffer.putShort(value)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter reader is not supported.",
                      2: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
