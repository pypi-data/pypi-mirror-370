from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSetBaseband(Message):

    def __init__(self, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SetBaseband.value
        self.baseSpeed = kwargs.get("baseSpeed", None)
        self.qValue = kwargs.get("qValue", None)
        self.session = kwargs.get("session", None)
        self.inventoryFlag = kwargs.get("inventoryFlag", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.baseSpeed is not None:
            buffer.putInt(0x01)
            buffer.putInt(self.baseSpeed)
        if self.qValue is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.qValue)
        if self.session is not None:
            buffer.putInt(0x03)
            buffer.putInt(self.session)
        if self.inventoryFlag is not None:
            buffer.putInt(0x04)
            buffer.putInt(self.inventoryFlag)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Parameter reader is not supported.",
                      2: "Q value parameter error.", 3: "Session parameter error.", 4: "Inventory parameter error.",
                      5: "Other error.", 6: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
