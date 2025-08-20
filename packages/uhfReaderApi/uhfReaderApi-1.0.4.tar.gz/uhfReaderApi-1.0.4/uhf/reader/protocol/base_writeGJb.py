from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseWriteGJb(Message):

    def __init__(self, antennaEnable: int, area: int, start: int, hexWriteData: str, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_WriteGJb.value
        self.antennaEnable = antennaEnable
        self.area = area
        self.start = start
        self.hexWriteData = hexWriteData
        self.filter = kwargs.get("filter", None)  # type:ParamEpcFilter
        self.hexPassword = kwargs.get("hexPassword", None)
        self.safeMark = kwargs.get("safeMark", None)
        self.stayCarrierWave = kwargs.get("stayCarrierWave", None)
        self.errorIndex = None

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.antennaEnable)
        buffer.putInt(self.area)
        buffer.putShort(self.start)
        if self.hexWriteData:
            to_bytes = hexToBytes(self.hexWriteData)
            buffer.putShort(len(to_bytes))
            buffer.putBytes(to_bytes)
        if self.filter is not None:
            buffer.putInt(0x01)
            filter_bytes = self.filter.toBytes()
            buffer.putShort(len(filter_bytes))
            buffer.putBytes(filter_bytes)
        if self.hexPassword is not None:
            buffer.putInt(0x02)
            buffer.putBytes(hexToBytes(self.hexPassword))
        if self.safeMark is not None:
            buffer.putInt(0x03)
            buffer.putInt(self.safeMark)
        if self.stayCarrierWave is not None:
            buffer.putInt(0x05)
            buffer.putInt(self.stayCarrierWave)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter error.",
                      2: "Filter parameter error.", 3: "Write parameter error.", 4: "CRC check error.",
                      5: "Underpower error.", 6: "Data area overflow.", 7: "Data area is locked.",
                      8: "Access password error.", 9: "Permission denied.", 10: "Identify failure.", 11: "Other error.",
                      12: "Label is missing.", 13: "Command error."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
            if len(self.cData) > 1:
                errBuffer = DynamicBuffer("0x" + bytesToHex(self.cData))
                errBuffer.pos = 8
                if errBuffer.readInt() == 1:
                    self.errorIndex = errBuffer.readShort()
