from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetEasAlarm(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetEasAlarm.value
        self.alarmSwitch = None
        self.filterArea = None
        self.start = None
        self.hexContent = None
        self.hexMask = None
        self.actionSuccess = None  # type:ActionParamSuccess
        self.actionFail = None  # type:ActionParamFail

    def bytesToClass(self):
        pass

    def pack(self):
        pass

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.alarmSwitch = buffer.readInt()
            self.filterArea = buffer.readInt()
            self.start = buffer.readShort()
            dataLen = buffer.readShort()
            if dataLen:
                self.hexContent = bytesToHex(buffer.readBytes(dataLen * 8))
            maskLen = buffer.readShort()
            if maskLen:
                self.hexMask = bytesToHex(buffer.readBytes(maskLen * 8))
            while buffer.pos / 8 < len(self.cData):
                pid = buffer.readInt()
                if pid == 1:
                    sucLen = buffer.readShort()
                    if sucLen:
                        suc_bytes = buffer.readBytes(sucLen * 8)
                        self.actionSuccess = ActionParamSuccess(0).bytesToClass(suc_bytes)
                if pid == 2:
                    failLen = buffer.readShort()
                    if failLen:
                        fail_bytes = buffer.readBytes(failLen * 8)
                        self.actionFail = ActionParamSuccess(0).bytesToClass(fail_bytes)
            self.rtCode = 0

    def __str__(self) -> str:
        return str(
            (self.alarmSwitch, self.filterArea, self.start, self.hexContent, self.hexMask, self.actionSuccess.__str__(),
             self.actionFail.__str__()))
