from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseSafeAttestation(Message):

    def __init__(self, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_SafeAttestation.value
        self.token1 = kwargs.get("token1", None)
        self.token2Result = kwargs.get("token2Result", None)
        self.encipheredData = kwargs.get("encipheredData", None)  # type:ParamSafeEncipheredData
        self.key = kwargs.get("key", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.token1 is not None:
            buffer.putInt(0x01)
            buffer.putBytes(hexToBytes(self.token1))
        if self.token2Result is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.token2Result)
        if self.encipheredData is not None:
            buffer.putInt(0x03)
            data_to_bytes = self.encipheredData.toBytes()
            buffer.putShort(len(data_to_bytes))
            buffer.putBytes(data_to_bytes)
        if self.key is not None:
            buffer.putInt(0x04)
            to_bytes = hexToBytes(self.key)
            buffer.putShort(len(to_bytes))
            buffer.putBytes(to_bytes)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Frequency parameter reader is not supported.",
                      2: "Save failure."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
