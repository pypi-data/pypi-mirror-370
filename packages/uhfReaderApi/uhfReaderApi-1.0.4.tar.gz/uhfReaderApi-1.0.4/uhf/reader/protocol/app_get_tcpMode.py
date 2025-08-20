from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetTcpMode(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetTcpMode.value
        self.tcpMode = None
        self.serverPort = None
        self.clientIp = None
        self.clientPort = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.tcpMode = buffer.readInt()
            self.serverPort = buffer.readShort()
            self.clientIp = str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(
                buffer.readInt()) + "." + str(
                buffer.readInt())
            self.clientPort = buffer.readShort()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.tcpMode, self.serverPort, self.clientIp, self.clientPort))
        # return "{0},{1},{2},{3},{4},{5}".format(self.readerSerialNumber, self.powerOnTime, self.baseCompileTime,
        #                                     self.appVersions, self.systemVersions, self.appCompileTime)
