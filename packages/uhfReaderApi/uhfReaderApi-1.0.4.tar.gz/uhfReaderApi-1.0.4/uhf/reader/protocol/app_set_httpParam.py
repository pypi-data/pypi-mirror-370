from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetHttpParam(Message):

    def __init__(self, onOrOff: int, period: int, timeout: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetHttpParam.value
        self.onOrOff = onOrOff
        self.period = period
        self.formats = kwargs.get("formats", 0)
        self.timeout = timeout
        self.openCache = kwargs.get("openCache", 0)
        self.reportAddress = kwargs.get("reportAddress", None)  # type:str

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.onOrOff)
        buffer.putShort(self.period)
        buffer.putInt(self.formats)
        buffer.putShort(self.timeout)
        buffer.putInt(self.openCache)
        if self.reportAddress is not None:
            buffer.putInt(0x01)
            buffer.putShort(len(self.reportAddress))
            buffer.putBytes(self.reportAddress.encode())
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Fail"}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)

