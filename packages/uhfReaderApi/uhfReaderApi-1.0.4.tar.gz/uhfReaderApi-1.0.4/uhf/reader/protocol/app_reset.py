from uhf.reader.protocol.message import Message
from uhf.reader.protocol.enumg import EnumG


class MsgAppReset(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_Reset.value

    def pack(self):
        super().pack()

    def unPack(self):
        pass
