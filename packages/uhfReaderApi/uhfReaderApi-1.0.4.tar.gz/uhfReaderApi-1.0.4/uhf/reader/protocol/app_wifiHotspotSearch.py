from uhf.reader.protocol import *
from .enumg import EnumG


class MsgAppSetWifiHotspotSearch(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetWifiHotspotSearch.value

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Reader is not supported."}
            self.rtCode = self.cData[0]
            self.rtMsg = dirMsg.get(self.rtCode, None)
