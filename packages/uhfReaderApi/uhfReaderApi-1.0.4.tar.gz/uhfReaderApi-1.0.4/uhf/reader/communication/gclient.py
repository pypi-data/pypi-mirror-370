from .tcp_client import TcpClient
from .serial_client import SerialClient
# from .usb_hid import UsbHidClient
from .hid import HidClient
from uhf.reader.protocol import *
from uhf.reader.utils import *


# import usb.core


class GClient(object):

    def __init__(self):
        self.__ci = None
        self.__msgDic = {}
        self.readerName = None
        self.__serialNumber = None
        self.__callEpcInfo = None
        self.__callEpcOver = None
        self.__call6bInfo = None
        self.__call6bOver = None
        self.__callGbInfo = None
        self.__callGbOver = None
        self.__callGJbInfo = None
        self.__callGJbOver = None
        self.__callTcpDisconnect = None
        self.__callGpiStart = None
        self.__callGpiOver = None
        self.__callCacheDataOver = None
        self.__allGpiState = None
        self.printLog = True

    def openTcp(self, readName: (), **kwargs):
        self.__ci = TcpClient()
        if self.__ci.open(readName, **kwargs):
            self.readerName = readName
            self.__ci.onMessageReceived = self.processMessage
            self.__ci.onTcpDisConnect = self.__callTcpDisConnectEvent
            return True
        return False

    def __callTcpDisConnectEvent(self, addr):
        if self.__callTcpDisconnect:
            self.__callTcpDisconnect(addr, self)

    def openServer(self, tcpClient: TcpClient):
        if not tcpClient:
            return False
        self.__ci = tcpClient
        self.readerName = tcpClient.addr
        self.__ci.onMessageReceived = self.processMessage
        self.__ci.onTcpDisConnect = self.__callTcpDisConnectEvent
        return True

    def openSerial(self, readName: (), **kwargs):
        if len(readName) == 2:
            self.__ci = SerialClient()
            if self.__ci.open(readName, **kwargs):
                self.readerName = readName
                self.__ci.onMessageReceived = self.processMessage
                return True
        return False

    def openSerial485(self, readName: (), **kwargs):
        if len(readName) == 3:
            self.__ci = SerialClient()
            if self.__ci.open(readName, **kwargs):
                self.__ci.rs485Address = readName[2]
                self.__ci.isRs485 = True
                self.readerName = readName
                self.__ci.onMessageReceived = self.processMessage
                return True
        return False

    # def openUsbHidDevice(self, dev: usb.core.Device):
    #     self.__ci = UsbHidClient()
    #     if self.__ci.open(dev):
    #         self.__ci.onMessageReceived = self.processMessage
    #         return True
    #     return False

    def openUsbHid(self, param: bytes):
        self.__ci = HidClient()
        if self.__ci.open(param):
            self.readerName = param
            self.__ci.onMessageReceived = self.processMessage
            return True
        return False

    def sendSynMsg(self, msg: Message, timeout=3):
        if self.__ci:
            self.__msgDic[msg.toKey()] = None
            self.__ci.sendMsg(msg)
            if self.printLog:
                print("send -> ", bytesToHex(msg.msgData))
            with self.__ci.lock:
                # print("开始等待")
                self.__ci.lock.wait(timeout)
            data = self.__msgDic.get(msg.toKey(), None)
            if data:
                if self.printLog:
                    print("receive->", bytesToHex(data.msgData))
                msg.cData = data.cData
                msg.unPack()
                return msg.rtCode

    def sendSynBytes(self, bytes, timeout=3):
        if self.__ci:
            return self.sendSynMsg(Message().new(bytesToHex(bytes)), timeout)

    def senUnSynMsg(self, msg: Message):
        if self.__ci:
            self.__ci.sendMsg(msg)

    def senUnSynBytes(self, bytes):
        if self.__ci:
            self.__ci.sendBytes(bytes)

    def processMessage(self, msg: Message):
        if msg.mt_12 == 0:
            # print("收发指令", msg.msgId)
            if msg.toKey() in self.__msgDic:
                self.__msgDic[msg.toKey()] = msg
                with self.__ci.lock:
                    # print("结束等待")
                    self.__ci.lock.notify()
        else:
            if msg.mt_8_11 == EnumG.Msg_Type_Bit_Base.value:
                if msg.msgId == EnumG.BaseLogMid_Epc.value:
                    if self.__callEpcInfo:
                        info = LogBaseEpcInfo()
                        info.cData = msg.cData
                        info.unPack()
                        if self.__serialNumber:
                            info.readerSerialNumber = self.__serialNumber
                        info.readerName = self.readerName
                        self.__callEpcInfo(info)
                elif msg.msgId == EnumG.BaseLogMid_EpcOver.value:
                    if self.__callEpcOver:
                        over = LogBaseEpcOver()
                        over.cData = msg.cData
                        over.unPack()
                        if self.__serialNumber:
                            over.readerSerialNumber = self.__serialNumber
                        over.readerName = self.readerName
                        self.__callEpcOver(over)
                elif msg.msgId == EnumG.BaseLogMid_6b.value:
                    if self.__call6bInfo:
                        b_info = LogBase6bInfo()
                        b_info.cData = msg.cData
                        b_info.unPack()
                        if self.__serialNumber:
                            b_info.readerSerialNumber = self.__serialNumber
                        b_info.readerName = self.readerName
                        self.__call6bInfo(b_info)
                elif msg.msgId == EnumG.BaseLogMid_6bOver.value:
                    if self.__call6bOver:
                        b_over = LogBase6bOver()
                        b_over.cData = msg.cData
                        b_over.unPack()
                        if self.__serialNumber:
                            b_over.readerSerialNumber = self.__serialNumber
                        b_over.readerName = self.readerName
                        self.__call6bOver(b_over)
                elif msg.msgId == EnumG.BaseLogMid_Gb.value:
                    if self.__callGbInfo:
                        gb_info = LogBaseGbInfo()
                        gb_info.cData = msg.cData
                        gb_info.unPack()
                        if self.__serialNumber:
                            gb_info.readerSerialNumber = self.__serialNumber
                        gb_info.readerName = self.readerName
                        self.__callGbInfo(gb_info)
                elif msg.msgId == EnumG.BaseLogMid_GbOver.value:
                    if self.__callGbOver:
                        gb_over = LogBaseGbOver()
                        gb_over.cData = msg.cData
                        gb_over.unPack()
                        if self.__serialNumber:
                            gb_over.readerSerialNumber = self.__serialNumber
                        gb_over.readerName = self.readerName
                        self.__callGbOver(gb_over)
                elif msg.msgId == EnumG.BaseLogMid_GJb.value:
                    if self.__callGJbInfo:
                        gjb_info = LogBaseGJbInfo()
                        gjb_info.cData = msg.cData
                        gjb_info.unPack()
                        if self.__serialNumber:
                            gjb_info.readerSerialNumber = self.__serialNumber
                        gjb_info.readerName = self.readerName
                        self.__callGJbInfo(gjb_info)
                elif msg.msgId == EnumG.BaseLogMid_GJbOver.value:
                    if self.__callGJbOver:
                        gjb_over = LogBaseGJbOver()
                        gjb_over.cData = msg.cData
                        gjb_over.unPack()
                        if self.__serialNumber:
                            gjb_over.readerSerialNumber = self.__serialNumber
                        gjb_over.readerName = self.readerName
                        self.__callGJbOver(gjb_over)
            elif msg.mt_8_11 == EnumG.Msg_Type_Bit_App.value:
                if msg.msgId == EnumG.AppMid_Heartbeat.value:
                    if self.printLog:
                        print("[heartbeat]", bytesToHex(msg.msgData))
                    self.senUnSynBytes(msg.msgData)
                if msg.msgId == EnumG.AppLogMid_gpi.value:
                    if self.__callGpiStart:
                        start = LogGpiStart()
                        start.cData = msg.cData
                        start.unPack()
                        if self.__serialNumber:
                            start.readerSerialNumber = self.__serialNumber
                        start.readerName = self.readerName
                        self.__callGpiStart(start)
                elif msg.msgId == EnumG.AppLogMid_gpiOver.value:
                    if self.__callGpiOver:
                        over = LogGpiOver()
                        over.cData = msg.cData
                        over.unPack()
                        if self.__serialNumber:
                            over.readerSerialNumber = self.__serialNumber
                        over.readerName = self.readerName
                        self.__callGpiOver(over)
                elif msg.msgId == EnumG.AppLogMid_allGpiState.value:
                    if self.__allGpiState:
                        state = LogAppAllGpiState()
                        state.cData = msg.cData
                        state.unPack()
                        if self.__serialNumber:
                            state.readerSerialNumber = self.__serialNumber
                        state.readerName = self.readerName
                        self.__allGpiState(state)
                elif msg.msgId == EnumG.AppMid_GetCacheTagData.value:
                    if self.__callCacheDataOver:
                        data = MsgAppGetCacheTagData()
                        data.cData = msg.cData
                        data.unPack()
                        self.__callCacheDataOver(data)

    @property
    def callEpcInfo(self):
        return self.__callEpcInfo

    @callEpcInfo.setter
    def callEpcInfo(self, callEpc):
        # if self.ci:
        self.__callEpcInfo = callEpc

    @property
    def callEpcOver(self):
        return self.__callEpcOver

    @callEpcOver.setter
    def callEpcOver(self, callEpcOver):
        # if self.ci:
        self.__callEpcOver = callEpcOver

    @property
    def call6bInfo(self):
        return self.__call6bInfo

    @call6bInfo.setter
    def call6bInfo(self, call6b):
        # if self.ci:
        self.__call6bInfo = call6b

    @property
    def call6bOver(self):
        return self.__call6bOver

    @call6bOver.setter
    def call6bOver(self, call6bOver):
        # if self.ci:
        self.__call6bOver = call6bOver

    @property
    def callGbInfo(self):
        return self.__callGbInfo

    @callGbInfo.setter
    def callGbInfo(self, callGb):
        # if self.ci:
        self.__callGbInfo = callGb

    @property
    def callGbOver(self):
        return self.__callGbOver

    @callGbOver.setter
    def callGbOver(self, callGbOver):
        # if self.ci:
        self.__callGbOver = callGbOver

    @property
    def callGJbInfo(self):
        return self.__callGJbInfo

    @callGJbInfo.setter
    def callGJbInfo(self, callGJb):
        # if self.ci:
        self.__callGJbInfo = callGJb

    @property
    def callGJbOver(self):
        return self.__callGJbOver

    @callGJbOver.setter
    def callGJbOver(self, callGJbOver):
        # if self.ci:
        self.__callGJbOver = callGJbOver

    @property
    def serialNumber(self):
        return self.__serialNumber

    @serialNumber.setter
    def serialNumber(self, serialNumber):
        # if self.ci:
        self.__serialNumber = serialNumber

    @property
    def callTcpDisconnect(self):
        return self.__callTcpDisconnect

    @callTcpDisconnect.setter
    def callTcpDisconnect(self, callDis):
        # if self.ci and isinstance(self.ci, TcpClient):
        self.__callTcpDisconnect = callDis
        # self.ci.callDisconnected = callDis

    @property
    def callGpiStart(self):
        return self.__callGpiStart

    @callGpiStart.setter
    def callGpiStart(self, callGpi):
        self.__callGpiStart = callGpi

    @property
    def callGpiOver(self):
        return self.__callGpiOver

    @callGpiOver.setter
    def callGpiOver(self, callGpi):
        self.__callGpiOver = callGpi

    @property
    def callCacheDataOver(self):
        return self.__callCacheDataOver

    @callCacheDataOver.setter
    def callCacheDataOver(self, cacheOver):
        self.__callCacheDataOver = cacheOver

    @property
    def allGpiState(self):
        return self.__allGpiState

    @allGpiState.setter
    def allGpiState(self, callGpi):
        self.__allGpiState = callGpi

    def close(self):
        if self.__ci:
            self.__ci.close()
            self.__ci = None
            self.__msgDic.clear()
            self.readerName = None
            self.__serialNumber = None
            self.__callEpcInfo = None
            self.__callEpcOver = None
            self.__call6bInfo = None
            self.__call6bOver = None
            self.__callGbInfo = None
            self.__callGbOver = None
            self.__callGJbInfo = None
            self.__callGJbOver = None
            self.__callTcpDisconnect = None
            self.__callGpiStart = None
            self.__callGpiOver = None
            self.__callCacheDataOver = None
            self.__allGpiState = None
