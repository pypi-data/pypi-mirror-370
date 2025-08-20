# from uhf.reader import *
# import logging
# from time import *
#
#
# def receivedEpc(epcInfo: LogBaseEpcInfo):
#     if epcInfo.result == 0:
#         pass
#         print(epcInfo.epc)
#
#
# def uploadEpcOver(epcOver: LogBaseEpcOver):
#     print("LogBaseEpcOver")
#
#
# def tcpDisconnect(readName: (),client):
#     print("触发断链--》", readName)

#
# def gpiStart(start: LogGpiStart):
#     pass
#
#
# def gpiOver(over: LogGpiOver):
#     pass
#
#
# def clientConnected(readerSerialNumber: str, gClient: GClient):
#     pass
#
#
# # logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] '
# #                            '- %(levelname)s: %(message)s', level=logging.INFO)
#
# if __name__ == '__main__':
#     client = GClient()
#     # 串口连接 True 即成功连接
#     # if client.openSerial(("COM7", 115200)):  # 不要重复连接，可调用close释放资源再次连接，未close的client可复用
#     # if client.openUsbHid(getUsbHidPathList()[0]):
#     if client.openTcp(("192.168.1.168", 8160)):
#         # 订阅盘点回调
#         # client.printLog = False
#         client.callTcpDisconnect = tcpDisconnect
#         client.callEpcInfo = receivedEpc
#         client.callEpcOver = uploadEpcOver
#
#         msg = MsgAppSetGpo()
#         msg.gpo1 = 1  # 1-高 0-低
#         if client.sendSynMsg(msg) == 0:
#             print("发送成功")
#
#
#         # client.callTcpDisconnect = tcpDisconnect
#         # client.callGpiStart = gpiStart
#         # client.callGpiOver = gpiOver
#         # 盘点6c 1号天线 循环盘点
#         # while True:
#         #     s = input()
#         #     # print(type(s))
#         #     if s == "1":
#         #         msg = MsgBaseInventoryEpc(EnumG.AntennaNo_1.value, EnumG.InventoryMode_Inventory.value)
#         #         # msg.readEpc = ParamEpcReadEpc(2, 6)
#         #         # msg.readTid = ParamEpcReadTid(0, 6)
#         #         # msg.readUserData = ParamEpcReadUserData(0, 6)
#         #
#         #         # for i in range(20):
#         #         # logging.info("sendSynMsg")
#         #         client.sendSynMsg(msg)
#         #         # print(msg.rtMsg)
#         #         # logging.info(msg.rtMsg)
#         #     else:
#         #         client.close()
#
#         # sleep(10)  # 盘点5s
#
#         # stop = MsgBaseStop()  # 停止盘点
#         # if client.sendSynMsg(stop) == 0:
#         #     print(stop.rtMsg)
#
#         # data = "FFFFFF2222233333333333333333311111111111100FFFFFFFFFF2222233333333333333333311111111111100FFFFFFFFFFFFFFFFFFFFF3FFFFFFFFFFFFFF33"
#         # value = getEpcData(data)
#         #
#         # print(value)
#         # epc = MsgBaseWriteEpc(1, EnumG.WriteArea_UserData.value, 0, data)
#         # client.sendSynMsg(epc)
#         # print(epc.rtMsg)
#
#         # stop = MsgBaseStop()  # 停止盘点
#         # if client.sendSynMsg(stop) == 0:
#         #     print(stop.rtMsg)
#
#         # client.close()  # 断开连接 释放资源
#
#         # g_server = GServer()
#         # g_server.callGClientConnected = clientConnected
