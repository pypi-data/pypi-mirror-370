from uhf.reader.protocol.message import Message
from uhf.reader.protocol.enumg import EnumG


class MsgAppDelWhiteList(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_DelWhiteList.value

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Del Fail."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
