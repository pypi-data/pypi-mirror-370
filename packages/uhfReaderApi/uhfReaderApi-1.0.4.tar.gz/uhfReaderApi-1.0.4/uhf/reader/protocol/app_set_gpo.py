from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetGpo(Message):

    def __init__(self, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetGpo.value
        self.gpo1 = kwargs.get("gpo1", None)
        self.gpo2 = kwargs.get("gpo2", None)
        self.gpo3 = kwargs.get("gpo3", None)
        self.gpo4 = kwargs.get("gpo4", None)
        self.gpo5 = kwargs.get("gpo5", None)
        self.gpo6 = kwargs.get("gpo6", None)
        self.gpo7 = kwargs.get("gpo7", None)
        self.gpo8 = kwargs.get("gpo8", None)
        self.gpo9 = kwargs.get("gpo9", None)
        self.gpo10 = kwargs.get("gpo10", None)
        self.gpo11 = kwargs.get("gpo11", None)
        self.gpo12 = kwargs.get("gpo12", None)
        self.gpo13 = kwargs.get("gpo13", None)
        self.gpo14 = kwargs.get("gpo14", None)
        self.gpo15 = kwargs.get("gpo15", None)
        self.gpo16 = kwargs.get("gpo16", None)
        self.gpo17 = kwargs.get("gpo17", None)
        self.gpo18 = kwargs.get("gpo18", None)
        self.gpo19 = kwargs.get("gpo19", None)
        self.gpo20 = kwargs.get("gpo20", None)
        self.gpo21 = kwargs.get("gpo21", None)
        self.gpo22 = kwargs.get("gpo22", None)
        self.gpo23 = kwargs.get("gpo23", None)
        self.gpo24 = kwargs.get("gpo24", None)
        self.gpo25 = kwargs.get("gpo25", None)
        self.gpo26 = kwargs.get("gpo26", None)
        self.gpo27 = kwargs.get("gpo27", None)
        self.gpo28 = kwargs.get("gpo28", None)
        self.gpo29 = kwargs.get("gpo29", None)
        self.gpo30 = kwargs.get("gpo30", None)
        self.gpo31 = kwargs.get("gpo31", None)
        self.gpo32 = kwargs.get("gpo32", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.gpo1 is not None:
            buffer.putInt(0x01)
            buffer.putInt(self.gpo1)
        if self.gpo2 is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.gpo2)
        if self.gpo3 is not None:
            buffer.putInt(0x03)
            buffer.putInt(self.gpo3)
        if self.gpo4 is not None:
            buffer.putInt(0x04)
            buffer.putInt(self.gpo4)
        if self.gpo5 is not None:
            buffer.putInt(0x05)
            buffer.putInt(self.gpo5)
        if self.gpo6 is not None:
            buffer.putInt(0x06)
            buffer.putInt(self.gpo6)
        if self.gpo7 is not None:
            buffer.putInt(0x07)
            buffer.putInt(self.gpo7)
        if self.gpo8 is not None:
            buffer.putInt(0x08)
            buffer.putInt(self.gpo8)
        if self.gpo9 is not None:
            buffer.putInt(0x09)
            buffer.putInt(self.gpo9)
        if self.gpo10 is not None:
            buffer.putInt(0x0A)
            buffer.putInt(self.gpo10)
        if self.gpo11 is not None:
            buffer.putInt(0x0B)
            buffer.putInt(self.gpo11)
        if self.gpo12 is not None:
            buffer.putInt(0x0C)
            buffer.putInt(self.gpo12)
        if self.gpo13 is not None:
            buffer.putInt(0x0D)
            buffer.putInt(self.gpo13)
        if self.gpo14 is not None:
            buffer.putInt(0x0E)
            buffer.putInt(self.gpo14)
        if self.gpo15 is not None:
            buffer.putInt(0x0F)
            buffer.putInt(self.gpo15)
        if self.gpo16 is not None:
            buffer.putInt(0x10)
            buffer.putInt(self.gpo16)
        if self.gpo17 is not None:
            buffer.putInt(0x11)
            buffer.putInt(self.gpo17)
        if self.gpo18 is not None:
            buffer.putInt(0x12)
            buffer.putInt(self.gpo18)
        if self.gpo19 is not None:
            buffer.putInt(0x13)
            buffer.putInt(self.gpo19)
        if self.gpo20 is not None:
            buffer.putInt(0x14)
            buffer.putInt(self.gpo20)
        if self.gpo21 is not None:
            buffer.putInt(0x15)
            buffer.putInt(self.gpo21)
        if self.gpo22 is not None:
            buffer.putInt(0x16)
            buffer.putInt(self.gpo22)
        if self.gpo23 is not None:
            buffer.putInt(0x17)
            buffer.putInt(self.gpo23)
        if self.gpo24 is not None:
            buffer.putInt(0x18)
            buffer.putInt(self.gpo24)
        if self.gpo25 is not None:
            buffer.putInt(0x19)
            buffer.putInt(self.gpo25)
        if self.gpo26 is not None:
            buffer.putInt(0x1A)
            buffer.putInt(self.gpo26)
        if self.gpo27 is not None:
            buffer.putInt(0x1B)
            buffer.putInt(self.gpo27)
        if self.gpo28 is not None:
            buffer.putInt(0x1C)
            buffer.putInt(self.gpo28)
        if self.gpo29 is not None:
            buffer.putInt(0x1D)
            buffer.putInt(self.gpo29)
        if self.gpo30 is not None:
            buffer.putInt(0x1E)
            buffer.putInt(self.gpo30)
        if self.gpo31 is not None:
            buffer.putInt(0x1F)
            buffer.putInt(self.gpo31)
        if self.gpo32 is not None:
            buffer.putInt(0x20)
            buffer.putInt(self.gpo32)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter reader hardware is not supported ."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
