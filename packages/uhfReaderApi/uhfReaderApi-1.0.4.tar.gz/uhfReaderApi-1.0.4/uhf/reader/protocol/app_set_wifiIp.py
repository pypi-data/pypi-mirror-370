from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetWifiIp(Message):

    def __init__(self, autoIp: int, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetWifiIp.value
        self.autoIp = autoIp
        self.ip = kwargs.get("ip", None)
        self.mask = kwargs.get("mask", None)
        self.gateway = kwargs.get("gateway", None)
        self.dns1 = kwargs.get("dns1", None)
        self.dns2 = kwargs.get("dns2", None)
        self.hotId = kwargs.get("hotId", None)

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
                masks = self.mask.split('.')
                for ms in masks:
                    buffer.putInt(int(ms))

            if self.gateway is not None:
                buffer.putInt(0x03)
                gateways = self.gateway.split('.')
                for gs in gateways:
                    buffer.putInt(int(gs))

            if self.dns1 is not None:
                buffer.putInt(0x04)
                dns1s = self.dns1.split('.')
                for d1 in dns1s:
                    buffer.putInt(int(d1))

            if self.dns2 is not None:
                buffer.putInt(0x05)
                dns2s = self.dns2.split('.')
                for d2 in dns2s:
                    buffer.putInt(int(d2))
        if self.hotId is not None:
            buffer.putInt(0x06)
            buffer.putLong(self.hotId)
        else:
            buffer.putInt(0x06)
            buffer.putLong(0)

        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "ReaderIp parameter error ."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
