from uhf.reader.communication.tcp_client import TcpClient
from uhf.reader.communication.tcp_server import TcpServer
from uhf.reader.communication.gclient import GClient
from uhf.reader.protocol import *


class GServer(object):

    def __init__(self):
        self.__tcpServer = None
        self.__dicClients = {}
        self.__callGClientConnected = None

    def openServer(self, port: int, address="0.0.0.0"):
        if self.__tcpServer:
            return False
        self.__tcpServer = TcpServer()
        self.__tcpServer.onRemoteConnected = self.__processConnect
        if self.__tcpServer.open(port, address):
            return True
        else:
            self.close()
            return False

    def __processConnect(self, tcpClient: TcpClient):
        if not tcpClient:
            return
        g_client = GClient()
        if g_client.openServer(tcpClient):
            if tcpClient.addr not in self.__dicClients:
                self.__dicClients[tcpClient.addr] = g_client
            else:
                self.__dicClients[tcpClient.addr].close()
                self.__dicClients[tcpClient.addr] = g_client
            if self.__callGClientConnected:
                info = MsgAppGetReaderInfo()
                if g_client.sendSynMsg(info) == 0:
                    g_client.serialNumber = info.readerSerialNumber
                    self.__callGClientConnected(info.readerSerialNumber, g_client)
                else:
                    g_client.close()

    def close(self):
        if self.__tcpServer:
            self.__tcpServer.close()
            self.__tcpServer = None
            # self.closeAllClient()

    def closeClient(self, readerName: ()):
        if len(readerName):
            if readerName in self.__dicClients:
                self.__dicClients[readerName].close()
                del self.__dicClients[readerName]

    def closeAllClient(self):
        for client in self.__dicClients.values():
            client.close()
        self.__dicClients.clear()

    @property
    def callGClientConnected(self):
        return self.callGClientConnected

    @callGClientConnected.setter
    def callGClientConnected(self, call):
        self.__callGClientConnected = call
