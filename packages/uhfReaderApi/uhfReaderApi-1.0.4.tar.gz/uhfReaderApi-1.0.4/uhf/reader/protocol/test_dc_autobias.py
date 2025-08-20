from uhf.reader.protocol import *


class MsgTestDCAutoBias(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_DCAutobias.value

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
