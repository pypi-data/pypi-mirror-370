from uhf.reader.protocol import *
from .enumg import EnumG


class MsgBaseStop(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_Stop.value

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Stop failure"}
            self.rtCode = self.cData[0]
            self.rtMsg = dirMsg.get(self.rtCode, None)
