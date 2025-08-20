from uhf.reader.protocol.message import Message
from uhf.reader.protocol.enumg import EnumG


class LogBaseGbOver(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseLogMid_GbOver.value
        self.readerSerialNumber = None
        self.readerName = None

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Single operation complete.", 1: "Receive stop instruction.",
                      2: "A hardware failure causes an interrupt."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
