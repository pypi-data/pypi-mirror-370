from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetGpiTrigger(Message):

    def __init__(self, gpiPort: int, triggerStart: int, hexTriggerCommand: str, triggerOver: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetGpiTrigger.value
        self.gpiPort = gpiPort
        self.triggerStart = triggerStart
        # self.triggerCommand = None
        self.hexTriggerCommand = hexTriggerCommand
        self.triggerOver = triggerOver
        self.overDelayTime = kwargs.get("overDelayTime", None)
        self.levelUploadSwitch = kwargs.get("levelUploadSwitch", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.gpiPort)
        buffer.putInt(self.triggerStart)
        if self.hexTriggerCommand:
            to_bytes = hexToBytes(self.hexTriggerCommand)
            buffer.putShort(len(to_bytes))
            buffer.putBytes(to_bytes)
        else:
            buffer.putShort(0)

        buffer.putInt(self.triggerOver)
        if self.overDelayTime is not None:
            buffer.putInt(0x01)
            buffer.putShort(self.overDelayTime)
        if self.levelUploadSwitch is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.levelUploadSwitch)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter reader hardware is not supported .",
                      2: "Parameters are missing ."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
