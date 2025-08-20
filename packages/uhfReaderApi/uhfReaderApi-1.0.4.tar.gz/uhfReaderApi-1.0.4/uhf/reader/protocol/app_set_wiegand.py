from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetWiegand(Message):

    def __init__(self, wiegandSwitch: int, wiegandFormat: int, wiegandContent: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetWigan.value
        self.wiegandSwitch = wiegandSwitch
        self.wiegandFormat = wiegandFormat
        self.wiegandContent = wiegandContent

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.wiegandSwitch)
        buffer.putInt(self.wiegandFormat)
        buffer.putInt(self.wiegandContent)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Reader hardware is not supported Wigan port.",
                      2: "Wigan communication format not supported by reader .",
                      3: "Data content not supported by the reader"}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
