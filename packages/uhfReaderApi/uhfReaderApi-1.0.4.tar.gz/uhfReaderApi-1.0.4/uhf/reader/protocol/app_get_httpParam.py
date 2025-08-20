from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetHttpParam(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetHttpParam.value
        self.onOrOff = None
        self.period = None
        self.formats = None
        self.timeout = None
        self.openCache = None
        self.reportAddress = None  # type:str

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.onOrOff = buffer.readInt()
            self.period = buffer.readShort()
            self.formats = buffer.readInt()
            self.timeout = buffer.readShort()
            self.openCache = buffer.readInt()
            while buffer.pos / 8 < len(self.cData):
                pid = buffer.readInt()
                if pid == 1:
                    reLen = buffer.readShort()
                    if reLen:
                        self.reportAddress = listToAscii(buffer.readBytes(reLen * 8))
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.onOrOff, self.period, self.timeout, self.reportAddress))
