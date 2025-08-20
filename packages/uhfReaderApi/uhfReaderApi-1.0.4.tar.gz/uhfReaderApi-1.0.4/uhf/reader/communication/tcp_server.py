import socket
import threading
from uhf.reader.communication.tcp_client import TcpClient


class TcpServer(object):

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.keepListen = False
        self.listenPort = 8160
        self.serverSocket = None
        self.onRemoteConnected = None

    def open(self, port: int, address="0.0.0.0"):
        if self.serverSocket:
            return False
        self.keepListen = True
        self.listenPort = port
        self.server.bind((address, self.listenPort))
        self.server.listen(9999)  # 设置最大连接数，超过后排队
        listen = threading.Thread(target=self.startListen, name="TcpServerListen")
        listen.start()
        return True

    def startListen(self):
        while self.keepListen:
            try:
                # 建立客户端连接
                self.serverSocket, addr = self.server.accept()
                # print("连接地址: %s" % str(addr))
                if self.onRemoteConnected:
                    client = TcpClient()
                    client.addr = addr
                    # self.serverSocket.setblocking(False)
                    if client.openSocket(self.serverSocket):
                        self.onRemoteConnected(client)
            except Exception as ex:
                print("stop listen")
                # print(ex.args)

    def close(self):
        try:
            self.keepListen = False
            self.server.close()
        except Exception as ex:
            print("stop listen")
