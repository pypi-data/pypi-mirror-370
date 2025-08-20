from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetEthernetIP(Message):

    def __init__(self, autoIp: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetReaderIP.value
        self.autoIp = autoIp
        self.ip = kwargs.get("ip", None)
        self.mask = kwargs.get("mask", None)
        self.gateway = kwargs.get("gateway", None)
        self.dns1 = kwargs.get("dns1", None)
        self.dns2 = kwargs.get("dns2", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.autoIp)
        if self.autoIp == 1:
            if self.ip is not None:
                buffer.putInt(0x01)
                splitIp = self.ip.split('.')
                for ips in splitIp:
                    buffer.putInt(int(ips))

            if self.mask is not None:
                buffer.putInt(0x02)
                splitMask = self.mask.split('.')
                for masks in splitMask:
                    buffer.putInt(int(masks))

            if self.gateway is not None:
                buffer.putInt(0x03)
                splitGateway = self.gateway.split('.')
                for gateways in splitGateway:
                    buffer.putInt(int(gateways))

            if self.dns1 is not None:
                buffer.putInt(0x04)
                splitDns1 = self.dns1.split('.')
                for dns1s in splitDns1:
                    buffer.putInt(int(dns1s))

            if self.dns2 is not None:
                buffer.putInt(0x05)
                splitDns2 = self.dns2.split('.')
                for dns2s in splitDns2:
                    buffer.putInt(int(dns2s))

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "ReaderIp parameter error ."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
