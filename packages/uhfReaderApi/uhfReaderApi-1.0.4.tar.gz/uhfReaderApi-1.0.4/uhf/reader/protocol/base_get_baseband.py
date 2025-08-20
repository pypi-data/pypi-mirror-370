from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseGetBaseband(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_GetBaseband.value
        self.baseSpeed = None
        self.qValue = None
        self.session = None
        self.inventoryFlag = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.baseSpeed = buffer.readInt()
            self.qValue = buffer.readInt()
            self.session = buffer.readInt()
            self.inventoryFlag = buffer.readInt()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.baseSpeed, self.qValue, self.session, self.inventoryFlag))
